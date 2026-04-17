# database.py
# Configuração do banco para Sprint 02-03
# Reutiliza o clarisse.db criado no Sprint 01

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# Aponta para o banco na raiz do projeto
# ../../clarisse.db significa: sobe 2 níveis (backend → sprint-02-03 → raiz)
DATABASE_URL = "sqlite:///../../../clarisse.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def criar_tabelas():
    """
    Cria as tabelas novas (analises_imagem) no banco existente.
    As tabelas antigas (clientes) não são afetadas.
    """
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas/verificadas no clarisse.db")

def get_db():
    """
    Gerador de sessão para usar nas rotas da API.
    Padrão igual ao Sprint 01.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()