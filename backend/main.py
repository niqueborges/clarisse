from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime
from typing import Optional, List
import shutil
import uuid
import json
from pathlib import Path

from .database import get_db, criar_tabelas
from .models import Cliente, AnaliseImagem
from .vision_service import analisar_imagem

# Criar tabelas no startup (evita efeitos colaterais em import)
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    criar_tabelas()
    yield

app = FastAPI(
    title="Clarisse API",
    description="API de cadastro de clientes — base do projeto Clarisse",
    version="1.0.0",
    lifespan=lifespan
)

# ───────────── Configurações ─────────────

BASE_DIR = Path(__file__).resolve().parent
UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ───────────── Schemas ─────────────

class AnaliseResponse(BaseModel):
    id: int
    foto_path: str
    emocao_dominante: Optional[str] = None
    confianca_emocao: Optional[float] = None
    data_analise: datetime

    class Config:
        from_attributes = True


class ClienteCreate(BaseModel):
    nome: str
    data_nascimento: date
    telefone: str
    email: EmailStr
    foto_path: Optional[str] = None


class ClienteUpdate(BaseModel):
    nome: Optional[str] = None
    data_nascimento: Optional[date] = None
    telefone: Optional[str] = None
    email: Optional[EmailStr] = None
    foto_path: Optional[str] = None


class ClienteSimpleResponse(BaseModel):
    id: int
    nome: str
    data_nascimento: date
    integridade: float
    telefone: str
    email: str
    foto_path: Optional[str] = None

    class Config:
        from_attributes = True


class ClienteDetailResponse(ClienteSimpleResponse):
    analises: List[AnaliseResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


# ───────────── Rotas ─────────────

@app.get("/")
def status():
    return {"status": "Clarisse API online"}


@app.post("/clientes", response_model=ClienteSimpleResponse, status_code=201)
def cadastrar_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    novo = Cliente(**cliente.model_dump())

    try:
        db.add(novo)
        db.commit()
        db.refresh(novo)
        return novo
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email já cadastrado.")


@app.get("/clientes", response_model=List[ClienteSimpleResponse])
def listar_clientes(db: Session = Depends(get_db)):
    return db.query(Cliente).all()


@app.get("/clientes/{cliente_id}", response_model=ClienteDetailResponse)
def buscar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = (
        db.query(Cliente)
        .options(selectinload(Cliente.analises))
        .filter(Cliente.id == cliente_id)
        .first()
    )

    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")

    return cliente


@app.put("/clientes/{cliente_id}", response_model=ClienteSimpleResponse)
def editar_cliente(cliente_id: int, dados: ClienteUpdate, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()

    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")

    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(cliente, campo, valor)

    try:
        db.commit()
        db.refresh(cliente)
        return cliente
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email já cadastrado.")


@app.delete("/clientes/{cliente_id}")
def excluir_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()

    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")

    db.delete(cliente)
    db.commit()
    return {"mensagem": f"Cliente '{cliente.nome}' excluído."}


# ───────────── Análise de imagem ─────────────

@app.post("/clientes/{cliente_id}/analise", response_model=AnaliseResponse)
def analisar_foto_cliente(
    cliente_id: int,
    foto: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()

    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")

    extensao = Path(foto.filename).suffix or ".jpg"
    nome_arquivo = f"{uuid.uuid4()}{extensao}"
    caminho = UPLOADS_DIR / nome_arquivo

    try:
        with caminho.open("wb") as buffer:
            shutil.copyfileobj(foto.file, buffer)

        resultado = analisar_imagem(str(caminho))

        if "erro" in resultado:
            caminho.unlink(missing_ok=True)
            raise HTTPException(status_code=400, detail=resultado["erro"])

        caminho_relativo = f"/uploads/{nome_arquivo}"

        nova_analise = AnaliseImagem(
            cliente_id=cliente.id,
            foto_path=caminho_relativo,
            emocao_dominante=resultado.get("emocao_dominante"),
            confianca_emocao=resultado.get("confianca"),
            resultado_completo=json.dumps(resultado)
        )

        db.add(nova_analise)
        cliente.foto_path = caminho_relativo

        db.commit()
        db.refresh(nova_analise)

        return nova_analise

    except HTTPException:
        raise
    except Exception as e:
        caminho.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Erro no upload: {str(e)}")


@app.get("/clientes/{cliente_id}/analises", response_model=List[AnaliseResponse])
def listar_analises_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()

    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")

    return cliente.analises