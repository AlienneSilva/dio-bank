import os
from pathlib import Path
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.app import app
from src.db import get_db_session

TEST_DB_FILE = "test_bank.db"
TEST_DATABASE_URL = f"sqlite+aiosqlite:///{TEST_DB_FILE}"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    """Cria as tabelas no início de toda a sessão de testes e limpa ao final."""
    schema_path = Path(__file__).resolve().parent.parent / "src" / "schema.sql"
    if not schema_path.exists():
        schema_path = Path("src/schema.sql")

    with open(schema_path, "r", encoding="utf-8") as f:
        ddl_script = f.read()

    async with test_engine.begin() as conn:
        # Garante banco limpo antes de iniciar
        await conn.execute(text("DROP TABLE IF EXISTS transacoes;"))
        await conn.execute(text("DROP TABLE IF EXISTS contas;"))
        await conn.execute(text("DROP TABLE IF EXISTS correntistas;"))

        for comando in ddl_script.split(";"):
            sql = comando.strip()
            if sql:
                await conn.execute(text(sql))

    yield

    async with test_engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS transacoes;"))
        await conn.execute(text("DROP TABLE IF EXISTS contas;"))
        await conn.execute(text("DROP TABLE IF EXISTS correntistas;"))

    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except OSError:
            pass


@pytest_asyncio.fixture(scope="function")
async def client():
    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db_session] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
