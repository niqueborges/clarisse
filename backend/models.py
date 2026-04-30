from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Date, Text
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()
class Cliente(Base):
    __tablename__ = "clientes"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    data_nascimento = Column(Date, nullable=False)
    integridade = Column(Float, nullable=False, default=1.0)
    telefone = Column(String(20), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    foto_path = Column(String(255), nullable=True)
    analises = relationship(
        "AnaliseImagem", back_populates="cliente", cascade="all, delete-orphan")


class AnaliseImagem(Base):
    __tablename__ = "analises_imagem"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    foto_path = Column(String(255), nullable=False)
    emocao_dominante = Column(String(50))
    confianca_emocao = Column(Float)
    resultado_completo = Column(Text)
    data_analise = Column(DateTime, default=datetime.utcnow)
    
    cliente = relationship("Cliente", back_populates="analises")
