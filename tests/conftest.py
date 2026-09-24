import os
import sqlite3
from collections.abc import AsyncGenerator
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.app import app
from src.db import get_db_session

TEST_DB_FILE = "./test_bank.db"
TEST_DATABASE_URL = f"sqlite+aiosqlite:///{TEST_DB_FILE}"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Cria a base de dados de teste lendo o schema.sql de forma síncrona."""
    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except OSError:
            pass

    schema_path = os.path.join(
        os.path.dirname(__file__), "..", "src", "schema.sql"
    )
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn = sqlite3.connect(TEST_DB_FILE)
    conn.executescript(schema_sql)
    conn.commit()
    conn.close()

    yield

    # Libera os handles de conexao abertos pelo SQLAlchemy
    test_engine.sync_engine.dispose()

    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except OSError:
            pass


async def override_get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_db_session] = override_get_db_session


# Utiliza pytest_asyncio.fixture para o pytest reconhecer o gerador assíncrono
@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Cliente HTTP assíncrono para testar a API."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as ac:
        yield ac
