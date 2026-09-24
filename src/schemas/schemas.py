from decimal import Decimal
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class TipoTransacao(str, Enum):
    DEPOSITO = "DEPOSITO"
    SAQUE = "SAQUE"
    TRANSFERENCIA = "TRANSFERENCIA"


# --- Schemas de Correntista ---
class CorrentistaCreate(BaseModel):
    nome: str = Field(..., min_length=3, max_length=150)
    cpf: str = Field(..., min_length=11, max_length=14)
    email: str = Field(..., min_length=5, max_length=100)
    senha: str = Field(..., min_length=6, max_length=50)


class CorrentistaOut(BaseModel):
    id: int
    nome: str
    cpf: str
    email: str


# --- Schemas de Conta ---
class ContaCreate(BaseModel):
    correntista_id: int
    numero_conta: str = Field(..., min_length=4, max_length=20)


class ContaOut(BaseModel):
    id: int
    numero_conta: str
    saldo: Decimal
    ativa: bool


# --- Schemas de Operações Financeiras ---
class DepositoIn(BaseModel):
    conta_id: int
    valor: Decimal = Field(..., gt=Decimal("0.00"), decimal_places=2)


class SaqueIn(BaseModel):
    conta_id: int
    valor: Decimal = Field(..., gt=Decimal("0.00"), decimal_places=2)


class TransferenciaIn(BaseModel):
    conta_origem_id: int
    conta_destino_id: int
    valor: Decimal = Field(..., gt=Decimal("0.00"), decimal_places=2)


class TransacaoOut(BaseModel):
    id: int
    conta_origem_id: Optional[int] = None
    conta_destino_id: Optional[int] = None
    tipo: TipoTransacao
    valor: Decimal
    descricao: Optional[str] = None

# Adicione ao src/schemas/schemas.py:


class LoginIn(BaseModel):
    identificador: str = Field(..., description="CPF ou E-mail")
    senha: str = Field(..., min_length=4)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
