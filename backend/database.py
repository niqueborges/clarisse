import os
from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker 
from dotenv import load_dotenv

load_dotenv()
# Prioriza .env, caso contrário usa sqlite local 
 
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./clarisse.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) 

def get_db():
    db = SessionLocal() 
    try:
        yield db
    finally:
        db.close()

from models import Base

def criar_tabelas():
    Base.metadata.create_all(bind=engine)
