# main.py
# API de Visão Computacional do Clarisse — Sprint 02-03
# Substitui AWS Rekognition + Lambda com análise local de emoções

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import shutil
import os
from datetime import datetime
from pathlib import Path

from database import get_db, criar_tabelas
from models import Cliente, AnaliseImagem
from vision_service import analisar_imagem, validar_imagem

# Cria as tabelas no banco
criar_tabelas()

app = FastAPI(
    title="Clarisse Vision API",
    description="API de análise de emoções em imagens — Sprint 02-03",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pasta para salvar uploads
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Servir arquivos estáticos (imagens)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ─────────────────────────────────────────
# Schemas
# ─────────────────────────────────────────

class AnaliseResponse(BaseModel):
    id: int
    cliente_id: int
    foto_path: str
    emocao_dominante: Optional[str]
    confianca_emocao: Optional[float]
    data_analise: datetime
    
    class Config:
        from_attributes = True

# ─────────────────────────────────────────
# Rotas
# ─────────────────────────────────────────

@app.get("/", tags=["Status"])
def status():
    """Verifica se a API está no ar."""
    return {"status": "🌿 Clarisse Vision API online"}


@app.post("/analisar", response_model=AnaliseResponse, tags=["Análise"])
async def analisar_foto_cliente(
    cliente_id: int = Form(...),
    foto: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Faz upload de uma foto, analisa as emoções e vincula ao cliente.
    """
    # Verifica se o cliente existe
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")
    
    # Gera nome único para o arquivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    extensao = Path(foto.filename).suffix
    nome_arquivo = f"cliente_{cliente_id}_{timestamp}{extensao}"
    caminho_completo = UPLOAD_DIR / nome_arquivo
    
    # Salva o arquivo
    with open(caminho_completo, "wb") as buffer:
        shutil.copyfileobj(foto.file, buffer)
    
    # Valida a imagem
    valido, mensagem = validar_imagem(str(caminho_completo))
    if not valido:
        os.remove(caminho_completo)  # Remove arquivo inválido
        raise HTTPException(status_code=400, detail=mensagem)
    
    # Analisa a imagem
    resultado = analisar_imagem(str(caminho_completo))
    
    if "erro" in resultado:
        os.remove(caminho_completo)  # Remove se não detectou face
        raise HTTPException(status_code=400, detail=resultado["erro"])
    
    # Salva no banco
    analise = AnaliseImagem(
        cliente_id=cliente_id,
        foto_path=f"uploads/{nome_arquivo}",
        emocao_dominante=resultado["emocao_dominante"],
        confianca_emocao=resultado["confianca"],
        resultado_completo=resultado["resultado_completo"]
    )
    
    db.add(analise)
    db.commit()
    db.refresh(analise)
    
    return analise


@app.get("/analises/cliente/{cliente_id}", response_model=list[AnaliseResponse], tags=["Análise"])
def listar_analises_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """Retorna todas as análises de um cliente específico."""
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")
    
    return db.query(AnaliseImagem).filter(AnaliseImagem.cliente_id == cliente_id).all()


@app.get("/analises", response_model=list[AnaliseResponse], tags=["Análise"])
def listar_todas_analises(db: Session = Depends(get_db)):
    """Retorna todas as análises cadastradas."""
    return db.query(AnaliseImagem).all()


@app.delete("/analises/{analise_id}", tags=["Análise"])
def excluir_analise(analise_id: int, db: Session = Depends(get_db)):
    """Exclui uma análise e sua foto."""
    analise = db.query(AnaliseImagem).filter(AnaliseImagem.id == analise_id).first()
    if not analise:
        raise HTTPException(status_code=404, detail="Análise não encontrada.")
    
    # Remove o arquivo de imagem
    try:
        caminho = Path(analise.foto_path)
        if caminho.exists():
            os.remove(caminho)
    except Exception as e:
        print(f"Erro ao remover arquivo: {e}")
    
    db.delete(analise)
    db.commit()
    return {"mensagem": "Análise excluída com sucesso."}