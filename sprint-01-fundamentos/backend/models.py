from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Cliente(Base):
    __tablename__ = "clientes"

    id             = Column(Integer, primary_key=True, index=True)
    nome           = Column(String(100), nullable=False)
    data_nascimento = Column(Date, nullable=False)
    telefone       = Column(String(20), nullable=False)
    email          = Column(String(100), unique=True, nullable=False)
    foto_path      = Column(String(255), nullable=True)  # 📸 usado na Sprint 08

    def __repr__(self):
        return f"<Cliente(id={self.id}, nome='{self.nome}', email='{self.email}')>"