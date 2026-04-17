# models.py
# Modelos de dados do Sprint 02-03 — Visão Computacional
# Reaproveita o banco clarisse.db do Sprint 01

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class Cliente(Base):
    """
    Reaproveita o modelo de Cliente do Sprint 01.
    Aqui só para manter a relação com Análise.
    """
    __tablename__ = "clientes"

    id             = Column(Integer, primary_key=True, index=True)
    nome           = Column(String(100), nullable=False)
    data_nascimento = Column(String, nullable=False)  # Date vira String no SQLite
    telefone       = Column(String(20), nullable=False)
    email          = Column(String(100), unique=True, nullable=False)
    foto_path      = Column(String(255), nullable=True)

    # Relacionamento: um cliente pode ter várias análises
    analises = relationship("AnaliseImagem", back_populates="cliente")

    def __repr__(self):
        return f"<Cliente(id={self.id}, nome='{self.nome}')>"


class AnaliseImagem(Base):
    """
    Armazena o resultado da análise de visão computacional.
    Vinculada a um cliente específico.
    """
    __tablename__ = "analises_imagem"

    id             = Column(Integer, primary_key=True, index=True)
    cliente_id     = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    foto_path      = Column(String(255), nullable=False)
    
    # Resultados da análise DeepFace
    emocao_dominante = Column(String(50))
    idade_estimada   = Column(Integer)
    genero           = Column(String(20))
    raca             = Column(String(50))
    
    # Confiança das predições (0-100)
    confianca_emocao = Column(Float)
    
    # JSON completo da análise (para debug e expansão futura)
    resultado_completo = Column(Text)
    
    # Timestamp
    data_analise     = Column(DateTime, default=datetime.utcnow)

    # Relacionamento reverso
    cliente = relationship("Cliente", back_populates="analises")

    def __repr__(self):
        return f"<Análise(id={self.id}, cliente={self.cliente_id}, emoção={self.emocao_dominante})>"