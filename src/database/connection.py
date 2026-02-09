from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from src.config import settings


engine = create_engine(
    settings.database_url,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    echo=False,
)

SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """Gera uma sessao do banco. Usa com: with get_db() as db:"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def criar_tabelas():
    """Cria todas as tabelas no banco de dados."""
    import src.database.models  # noqa: F401 - garante que os modelos sao registrados
    Base.metadata.create_all(bind=engine)
