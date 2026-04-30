from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session, selectinload
from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional, List
import os
import shutil
import uuid
import json
from pathlib import Path

from database import get_db, criar_tabelas
from models import Cliente, AnaliseImagem
from vision_service import analisar_imagem

# Cria as tabelas no banco ao iniciar a aplicação
# NOTA: Em um ambiente de produção, use uma ferramenta de migração como Alembic.
criar_tabelas()

app = FastAPI(
    title="Clarisse API",
    description="API de cadastro de clientes — base do projeto Clarisse",
    version="1.0.0"
)

# Diretório para uploads
UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(exist_ok=True)

# Servir arquivos estáticos (imagens de upload)
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

# CORS — permite que o frontend (navegador) converse com a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────
# Schemas Pydantic — validação dos dados
# ─────────────────────────────────────────

class AnaliseResponse(BaseModel):
    """Formato de resposta para uma análise de imagem."""
    id: int
    foto_path: str
    emocao_dominante: Optional[str] = None
    confianca_emocao: Optional[float] = None
    data_analise: datetime

    class Config:
        from_attributes = True


class ClienteCreate(BaseModel):
    """Dados obrigatórios para cadastrar um cliente."""
    nome: str
    data_nascimento: date
    telefone: str
    email: EmailStr
    foto_path: Optional[str] = None


class ClienteUpdate(BaseModel):
    """Todos os campos são opcionais na edição."""
    nome: Optional[str] = None
    data_nascimento: Optional[date] = None
    telefone: Optional[str] = None
    email: Optional[EmailStr] = None
    foto_path: Optional[str] = None


class ClienteSimpleResponse(BaseModel):
    """Formato de resposta para listagem de clientes (sem detalhes)."""
    id: int
    nome: str
    data_nascimento: date
    integridade: float
    telefone: str
    email: str
    foto_path: Optional[str] = None

class ClienteDetailResponse(ClienteSimpleResponse):
    """Formato de resposta para um cliente (com detalhes de análises)."""
    analises: List[AnaliseResponse] = []

    class Config:
        from_attributes = True

# ─────────────────────────────────────────
# Rotas
# ─────────────────────────────────────────

@app.get("/", tags=["Status"])
def status():
    """Verifica se a API está no ar."""
    return {"status": "🌿 Clarisse API online"}


@app.post("/clientes", response_model=ClienteSimpleResponse, status_code=201, tags=["Clientes"])
def cadastrar_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    """Cadastra um novo cliente."""
    existente = db.query(Cliente).filter(Cliente.email == cliente.email).first()
    if existente:
        raise HTTPException(status_code=400, detail="Email já cadastrado.")

    novo = Cliente(**cliente.model_dump())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


@app.get("/clientes", response_model=List[ClienteSimpleResponse], tags=["Clientes"])
def listar_clientes(db: Session = Depends(get_db)):
    """Retorna todos os clientes cadastrados."""
    return db.query(Cliente).all()


@app.get("/clientes/{cliente_id}", response_model=ClienteDetailResponse, tags=["Clientes"])
def buscar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """Busca um cliente pelo ID, incluindo seu histórico de análises."""
    # Usar `selectinload` para carregar as análises de forma eficiente (evita N+1 queries)
    cliente = db.query(Cliente).options(
        selectinload(Cliente.analises)).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")
    return cliente


@app.put("/clientes/{cliente_id}", response_model=ClienteSimpleResponse, tags=["Clientes"])
def editar_cliente(cliente_id: int, dados: ClienteUpdate, db: Session = Depends(get_db)):
    """Edita os dados de um cliente existente."""
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")

    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(cliente, campo, valor)

    db.commit()
    db.refresh(cliente)
    return cliente


@app.delete("/clientes/{cliente_id}", status_code=200, tags=["Clientes"])
def excluir_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """Exclui um cliente pelo ID."""
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")

    db.delete(cliente)
    db.commit()
    return {"mensagem": f"Cliente '{cliente.nome}' excluído com sucesso."}


# ─────────────────────────────────────────
# Rotas de Análise de Imagem
# ─────────────────────────────────────────

@app.post("/clientes/{cliente_id}/analise", response_model=AnaliseResponse, tags=["Análises"])
def analisar_foto_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    foto: UploadFile = File(...)
):
    """
    Faz upload de uma foto, analisa as emoções e salva o resultado.
    Atualiza a foto de perfil do cliente com a nova imagem.
    """
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")

    # Salvar o arquivo com um nome único
    file_extension = Path(foto.filename).suffix
    file_name = f"{uuid.uuid4()}{file_extension}"
    file_path = UPLOADS_DIR / file_name

    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(foto.file, buffer)

        # Chamar o serviço de visão para analisar a imagem
        resultado_analise = analisar_imagem(str(file_path.absolute()))

        if "erro" in resultado_analise:
            raise HTTPException(status_code=400, detail=f"Erro na análise: {resultado_analise['erro']}")

        # Salvar o resultado da análise no banco de dados
        caminho_relativo = f"/{UPLOADS_DIR.name}/{file_name}"
        nova_analise = AnaliseImagem(
            cliente_id=cliente_id,
            foto_path=caminho_relativo,
            emocao_dominante=resultado_analise.get("emocao_dominante"),
            confianca_emocao=resultado_analise.get("confianca"),
            resultado_completo=json.dumps(resultado_analise)
        )
        db.add(nova_analise)

        # Atualizar a foto de perfil do cliente
        cliente.foto_path = caminho_relativo

        db.commit()
        db.refresh(nova_analise)
        return nova_analise

    except Exception as e:
        # Em caso de erro, remover o arquivo que pode ter sido salvo
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Falha no processamento do upload: {e}")


@app.get("/clientes/{cliente_id}/analises", response_model=List[AnaliseResponse], tags=["Análises"])
def listar_analises_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """Lista todas as análises de imagem para um cliente específico."""
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")
    return cliente.analises