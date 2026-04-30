from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional
import os

from database import get_db, criar_tabelas
from models import Cliente

# Cria as tabelas no banco ao iniciar a aplicação
criar_tabelas()

app = FastAPI(
    title="Clarisse API",
    description="API de cadastro de clientes — base do projeto Clarisse",
    version="1.0.0"
)

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

class ClienteResponse(BaseModel):
    """Formato de resposta da API."""
    id: int
    nome: str
    data_nascimento: date
    telefone: str
    email: str
    foto_path: Optional[str] = None

    class Config:
        from_attributes = True

# ─────────────────────────────────────────
# Rotas
# ─────────────────────────────────────────

@app.get("/", tags=["Status"])
def status():
    """Verifica se a API está no ar."""
    return {"status": "🌿 Clarisse API online"}


@app.post("/clientes", response_model=ClienteResponse, tags=["Clientes"])
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


@app.get("/clientes", response_model=list[ClienteResponse], tags=["Clientes"])
def listar_clientes(db: Session = Depends(get_db)):
    """Retorna todos os clientes cadastrados."""
    return db.query(Cliente).all()


@app.get("/clientes/{cliente_id}", response_model=ClienteResponse, tags=["Clientes"])
def buscar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """Busca um cliente pelo ID."""
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")
    return cliente


@app.put("/clientes/{cliente_id}", response_model=ClienteResponse, tags=["Clientes"])
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


@app.delete("/clientes/{cliente_id}", tags=["Clientes"])
def excluir_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """Exclui um cliente pelo ID."""
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")

    db.delete(cliente)
    db.commit()
    return {"mensagem": f"Cliente '{cliente.nome}' excluído com sucesso."}