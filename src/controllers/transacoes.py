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
    if payload.valor <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O valor do depósito deve ser maior que zero.",
        )

    res_update = await session.execute(
        text("UPDATE contas SET saldo = saldo + :valor WHERE id = :id AND ativa = 1"),
        {"valor": float(payload.valor), "id": payload.conta_id},
    )

    if res_update.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta não encontrada ou inativa.",
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
    if payload.valor <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O valor do saque deve ser maior que zero.",
        )

   # 1. Valida titularidade
    query_conta = await session.execute(
        text("SELECT correntista_id FROM contas WHERE id = :id AND ativa = 1"),
        {"id": payload.conta_id},
    )
    conta = query_conta.mappings().first()
    if not conta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta não encontrada ou inativa.",
        )

    token_user_id = current_user.get("id") or current_user.get("sub")
    if int(conta["correntista_id"]) != int(token_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operação não autorizada para esta conta bancária.",
        )

    # 2. Atualização atômica anti-race condition
    res_update = await session.execute(
        text("""
            UPDATE contas 
            SET saldo = saldo - :valor 
            WHERE id = :id AND saldo >= :valor AND ativa = 1
        """),
        {"valor": float(payload.valor), "id": payload.conta_id},
    )

    if res_update.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Saldo insuficiente ou transação concorrente detectada.",
        )

    # 3. Registro no extrato
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
    if payload.valor <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O valor da transferência deve ser maior que zero.",
        )

    if payload.conta_origem_id == payload.conta_destino_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contas de origem e destino não podem ser idênticas.",
        )

 # 1. Verifica titularidade da conta de origem
    query_origem = await session.execute(
        text("SELECT correntista_id FROM contas WHERE id = :id AND ativa = 1"),
        {"id": payload.conta_origem_id},
    )
    origem = query_origem.mappings().first()
    if not origem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta de origem não encontrada ou inativa.",
        )

    token_user_id = current_user.get("id") or current_user.get("sub")
    if int(origem["correntista_id"]) != int(token_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o titular pode transferir desta conta.",
        )

    # 2. Verifica existência da conta de destino
    query_destino = await session.execute(
        text("SELECT id FROM contas WHERE id = :id AND ativa = 1"),
        {"id": payload.conta_destino_id},
    )
    if not query_destino.mappings().first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta de destino não encontrada ou inativa.",
        )

    # 3. Débito atômico na origem (protege contra race condition)
    res_debito = await session.execute(
        text("""
            UPDATE contas 
            SET saldo = saldo - :valor 
            WHERE id = :id AND saldo >= :valor AND ativa = 1
        """),
        {"valor": float(payload.valor), "id": payload.conta_origem_id},
    )

    if res_debito.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Saldo insuficiente ou concorrência detectada.",
        )

    # 4. Crédito no destino
    await session.execute(
        text("UPDATE contas SET saldo = saldo + :valor WHERE id = :id AND ativa = 1"),
        {"valor": float(payload.valor), "id": payload.conta_destino_id},
    )

    # 5. Registro imutável no extrato
    query_transacao = """
        INSERT INTO transacoes
        (conta_origem_id, conta_destino_id, tipo, valor, descricao)
        VALUES (:origem, :destino, 'TRANSFERENCIA', :valor, 'Transferência bancária');
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
