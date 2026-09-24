from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db_session
from src.schemas.schemas import ContaCreate

router = APIRouter(prefix="/contas", tags=["Contas Bancárias"])


@router.post(
    "/", response_model=dict, status_code=status.HTTP_201_CREATED
)
async def criar_conta(
    payload: ContaCreate,
    session: AsyncSession = Depends(get_db_session),
):
    async with session.begin():
        query_check = "SELECT id FROM correntistas WHERE id = :id"
        resultado_correntista = await session.execute(
            text(query_check),
            {"id": payload.correntista_id},
        )
        if not resultado_correntista.mappings().first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Correntista não encontrado.",
            )

        insert_sql = """
            INSERT INTO contas (correntista_id, numero_conta, saldo)
            VALUES (:correntista_id, :numero_conta, 0.00);
        """
        await session.execute(
            text(insert_sql),
            {
                "correntista_id": payload.correntista_id,
                "numero_conta": payload.numero_conta,
            },
        )

    return {"mensagem": "Conta criada com sucesso!"}


@router.get("/", status_code=status.HTTP_200_OK)
async def listar_contas(session: AsyncSession = Depends(get_db_session)):
    query = "SELECT id, correntista_id, numero_conta, saldo, ativa FROM contas"
    resultado = await session.execute(text(query))
    return resultado.mappings().all()


@router.get("/{conta_id}", status_code=status.HTTP_200_OK)
async def buscar_conta(
    conta_id: int, session: AsyncSession = Depends(get_db_session)
):
    query = """
        SELECT id, correntista_id, numero_conta, saldo, ativa
        FROM contas
        WHERE id = :id
    """
    resultado = await session.execute(text(query), {"id": conta_id})
    conta = resultado.mappings().first()
    if not conta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta bancária não encontrada.",
        )
    return conta


@router.get("/{conta_id}/extrato", status_code=status.HTTP_200_OK)
async def extrato_conta(
    conta_id: int, session: AsyncSession = Depends(get_db_session)
):
    # 1. Verifica dados da conta
    query_conta = """
        SELECT id, numero_conta, saldo, ativa
        FROM contas
        WHERE id = :id
    """
    res_conta = await session.execute(text(query_conta), {"id": conta_id})
    conta = res_conta.mappings().first()
    if not conta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta bancária não encontrada.",
        )

    # 2. Busca todas as movimentações onde a conta seja origem ou destino
    query_transacoes = """
        SELECT id, conta_origem_id, conta_destino_id, tipo,
               valor, data_hora, descricao
        FROM transacoes
        WHERE conta_origem_id = :id OR conta_destino_id = :id
        ORDER BY data_hora DESC, id DESC
    """
    res_transacoes = await session.execute(
        text(query_transacoes), {"id": conta_id}
    )
    transacoes = res_transacoes.mappings().all()

    return {
        "conta_id": conta["id"],
        "numero_conta": conta["numero_conta"],
        "saldo_atual": conta["saldo"],
        "transacoes": transacoes,
    }