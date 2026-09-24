from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.controllers.contas import router as contas_router
from src.controllers.correntista import router as correntistas_router
from src.controllers.transacoes import router as transacoes_router
from src.db import init_db
from src.controllers.auth import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Executado ao iniciar a aplicação: cria as tabelas se não existirem
    await init_db()
    yield
    # Código executado no encerramento da API (se necessário)


app = FastAPI(
    title="DIO Bank API",
    description="Sistema Bancário Assíncrono de Alta Performance",
    version="1.0.0",
    lifespan=lifespan,
)

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro das rotas bancárias
app.include_router(correntistas_router)
app.include_router(contas_router)
app.include_router(transacoes_router)
app.include_router(auth_router)


@app.get("/", tags=["Health Check"])
async def root():
    return {"status": "ok", "mensagem": "DIO Bank API está online!"}
