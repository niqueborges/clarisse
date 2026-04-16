from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# O banco será salvo como um arquivo local: clarisse.db
DATABASE_URL = "sqlite:///./clarisse.db"

# create_engine cria a "ponte" entre Python e o banco
# check_same_thread=False é necessário para o SQLite funcionar com FastAPI
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# SessionLocal é a "fábrica" de sessões — cada requisição abre uma sessão
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def criar_tabelas():
    """Cria todas as tabelas no banco se ainda não existirem."""
    Base.metadata.create_all(bind=engine)

def get_db():
    """
    Gerador de sessão para usar nas rotas da API.
    Garante que a sessão sempre será fechada após a requisição.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()