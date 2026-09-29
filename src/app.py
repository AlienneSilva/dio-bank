from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from src.controllers import auth, contas, correntista, transacoes
from src.exceptions import BankException

tags_metadata = [
    {
        "name": "Autenticação",
        "description": "Endpoints responsáveis pela emissão e validação de tokens JWT.",
    },
    {
        "name": "Correntistas",
        "description": "Operações de registo e gestão de clientes da instituição financeira.",
    },
    {
        "name": "Contas",
        "description": "Gestão de contas bancárias associadas aos titulares.",
    },
    {
        "name": "Transações",
        "description": "Operações críticas com proteção de atomicidade: depósitos, levantamentos e transferências.",
    },
]

app = FastAPI(
    title="DIO Bank API",
    version="1.0.0",
    description="""
### API Bancária Assíncrona de Elevada Fiabilidade

Esta API fornece funcionalidades bancárias essenciais:
* **Concorrência Segura:** Proteção contra saldo negativo através de operações SQL atómicas com cláusula de guarda.
* **Autenticação:** Baseada em Bearer Token (JWT).
* **Migrações:** Esquema de base de dados gerido de forma declarativa via Alembic.
    """,
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
)


# Handlers globais de exceção
@app.exception_handler(BankException)
async def bank_exception_handler(request: Request, exc: BankException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "code": exc.code,
            "message": exc.message,
            "details": exc.details,
        },
    )


@app.exception_handler(IntegrityError)
async def integrity_exception_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "status": "error",
            "code": "DATABASE_INTEGRITY_VIOLATION",
            "message": "Registo conflituoso: identificador ou chave única já existente.",
            "details": [],
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    erros = [
        {"campo": " -> ".join(str(loc) for loc in err["loc"]), "erro": err["msg"]}
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "error",
            "code": "VALIDATION_ERROR",
            "message": "Dados de entrada inválidos.",
            "details": erros,
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "code": f"HTTP_{exc.status_code}",
            "message": exc.detail,
            "details": [],
        },
    )

# Roteadores organizados por Tag
app.include_router(auth.router, tags=["Autenticação"])
app.include_router(correntista.router, tags=["Correntistas"])
app.include_router(contas.router, tags=["Contas"])
app.include_router(transacoes.router, tags=["Transações"])
