import os
from typing import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config import settings

# Cria o engine assíncrono baseado na URL definida pelo ambiente
engine = create_async_engine(
    settings.database_url,
    echo=(settings.ENVIRONMENT == "development"),
    # Exibe queries SQL no terminal em dev
)

# Fábrica de sessões assíncronas
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def init_db() -> None:
    """Executa o script schema.sql na inicialização do banco."""
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    if not os.path.exists(schema_path):
        return

    with open(schema_path, mode="r", encoding="utf-8") as f:
        schema_sql = f.read()

    async with engine.begin() as conn:
        # Divide as instruções por ';'
        # para compatibilidade entre SQLite e PostgreSQL
        for statement in schema_sql.split(";"):
            clean_stmt = statement.strip()
            if clean_stmt:
                await conn.execute(text(clean_stmt))


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Injetor de dependência para rotas do FastAPI."""
    async with AsyncSessionLocal() as session:
        yield session
