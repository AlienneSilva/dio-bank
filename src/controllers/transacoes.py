from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db_session
from src.schemas.schemas import DepositoIn, SaqueIn, TransferenciaIn
from src.security import get_current_user

router = APIRouter(prefix="/transacoes", tags=["Transações Bancárias"])


@router.post("/deposito", status_code=status.HTTP_200_OK)
async def depositar(
    payload: DepositoIn, session: AsyncSession = Depends(get_db_session)
):
    query_conta = await session.execute(
        text("SELECT id, saldo FROM contas WHERE id = :id AND ativa = 1"),
        {"id": payload.conta_id},
    )
    conta = query_conta.mappings().first()
    if not conta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta não encontrada ou inativa.",
        )

    await session.execute(
        text("UPDATE contas SET saldo = saldo + :valor WHERE id = :id"),
        {"valor": float(payload.valor), "id": payload.conta_id},
    )

    query_transacao = """
        INSERT INTO transacoes (conta_destino_id, tipo, valor, descricao)
        VALUES (:conta_id, 'DEPOSITO', :valor, 'Depósito em dinheiro');
    """
    await session.execute(
        text(query_transacao),
        {"conta_id": payload.conta_id, "valor": float(payload.valor)},
    )
    await session.commit()

    return {"detail": "Depósito realizado com sucesso!"}


@router.post("/saque", status_code=status.HTTP_200_OK)
async def sacar(
    payload: SaqueIn,
    session: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_user),
):
    query_conta = await session.execute(
        text("""
            SELECT id, correntista_id, saldo
            FROM contas
            WHERE id = :id AND ativa = 1
        """),
        {"id": payload.conta_id},
    )
    conta = query_conta.mappings().first()
    if not conta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta não encontrada ou inativa.",
        )

    if int(conta["correntista_id"]) != int(current_user["id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operação não autorizada para esta conta bancária.",
        )

    if float(conta["saldo"]) < float(payload.valor):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Saldo insuficiente para saque.",
        )

    await session.execute(
        text("UPDATE contas SET saldo = saldo - :valor WHERE id = :id"),
        {"valor": float(payload.valor), "id": payload.conta_id},
    )

    query_transacao = """
        INSERT INTO transacoes (conta_origem_id, tipo, valor, descricao)
        VALUES (:conta_id, 'SAQUE', :valor, 'Saque em caixa eletrônico');
    """
    await session.execute(
        text(query_transacao),
        {"conta_id": payload.conta_id, "valor": float(payload.valor)},
    )
    await session.commit()

    return {"detail": "Saque realizado com sucesso!"}


@router.post("/transferencia", status_code=status.HTTP_200_OK)
async def transferir(
    payload: TransferenciaIn,
    session: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_user),
):
    if payload.conta_origem_id == payload.conta_destino_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contas de origem e destino não podem ser idênticas.",
        )

    query_origem = await session.execute(
        text("""
            SELECT id, correntista_id, saldo
            FROM contas
            WHERE id = :id AND ativa = 1
        """),
        {"id": payload.conta_origem_id},
    )
    origem = query_origem.mappings().first()
    if not origem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta de origem não encontrada ou inativa.",
        )

    if int(origem["correntista_id"]) != int(current_user["id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o titular pode transferir desta conta.",
        )

    if float(origem["saldo"]) < float(payload.valor):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Saldo insuficiente.",
        )

    query_destino = await session.execute(
        text("SELECT id FROM contas WHERE id = :id AND ativa = 1"),
        {"id": payload.conta_destino_id},
    )
    destino = query_destino.mappings().first()
    if not destino:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta de destino não encontrada ou inativa.",
        )

    await session.execute(
        text("UPDATE contas SET saldo = saldo - :valor WHERE id = :id"),
        {"valor": float(payload.valor), "id": payload.conta_origem_id},
    )
    await session.execute(
        text("UPDATE contas SET saldo = saldo + :valor WHERE id = :id"),
        {"valor": float(payload.valor), "id": payload.conta_destino_id},
    )

    query_transacao = """
        INSERT INTO transacoes
        (conta_origem_id, conta_destino_id, tipo, valor, descricao)
        VALUES (:origem, :destino, 'TRANSFERENCIA', :valor, 'Transferência');
    """
    await session.execute(
        text(query_transacao),
        {
            "origem": payload.conta_origem_id,
            "destino": payload.conta_destino_id,
            "valor": float(payload.valor),
        },
    )
    await session.commit()

    return {"detail": "Transferência realizada com sucesso!"}
