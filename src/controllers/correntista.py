from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db_session
from src.schemas.schemas import CorrentistaCreate
from src.security import hash_password

router = APIRouter(prefix="/correntistas", tags=["Correntistas"])


@router.post(
    "/", response_model=dict, status_code=status.HTTP_201_CREATED
)
@router.post(
    "",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
async def criar_correntista(
    payload: CorrentistaCreate,
    session: AsyncSession = Depends(get_db_session),
):
    async with session.begin():
        query_check = """
            SELECT id FROM correntistas
            WHERE cpf = :cpf OR email = :email
        """
        duplicado = (
            await session.execute(
                text(query_check),
                {"cpf": payload.cpf, "email": payload.email},
            )
        ).mappings().first()

        if duplicado:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Correntista já cadastrado com este CPF ou E-mail.",
            )

        senha_criptografada = hash_password(payload.senha)

        query_insert = """
            INSERT INTO correntistas (nome, cpf, email, senha_hash)
            VALUES (:nome, :cpf, :email, :senha_hash);
        """
        await session.execute(
            text(query_insert),
            {
                "nome": payload.nome,
                "cpf": payload.cpf,
                "email": payload.email,
                "senha_hash": senha_criptografada,
            },
        )
        

    return {"mensagem": "Correntista cadastrado com sucesso!"}


@router.get("/", status_code=status.HTTP_200_OK)
async def listar_correntistas(session: AsyncSession = Depends(get_db_session)):
    query = "SELECT id, nome, cpf, email, criado_em FROM correntistas"
    resultado = await session.execute(text(query))
    return resultado.mappings().all()


@router.get("/{correntista_id}", status_code=status.HTTP_200_OK)
async def buscar_correntista(
    correntista_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    query = """
        SELECT id, nome, cpf, email, criado_em
        FROM correntistas
        WHERE id = :id
    """
    resultado = await session.execute(text(query), {"id": correntista_id})
    correntista = resultado.mappings().first()

    if not correntista:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Correntista não encontrado.",
        )

    return correntista


@router.delete("/{correntista_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_correntista(
    correntista_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    async with session.begin():
        query_user = "SELECT id FROM correntistas WHERE id = :id"
        correntista = (
            await session.execute(text(query_user), {"id": correntista_id})
        ).mappings().first()

        if not correntista:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Correntista não encontrado.",
            )

        query_contas = "SELECT id FROM contas WHERE correntista_id = :id"
        contas = (
            await session.execute(text(query_contas), {"id": correntista_id})
        ).mappings().all()

        if contas:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Correntista possui contas bancárias vinculadas.",
            )

        await session.execute(
            text("DELETE FROM correntistas WHERE id = :id"),
            {"id": correntista_id},
        )

    return None