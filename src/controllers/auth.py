from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db_session
from src.schemas.schemas import LoginIn, TokenOut
from src.security import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login")
async def login(
    payload: LoginIn,
    session: AsyncSession = Depends(get_db_session),
):
    query_sql = (
        "SELECT id, cpf, senha_hash FROM correntistas "
        "WHERE cpf = :identificador OR email = :identificador"
    )
    query = await session.execute(
        text(query_sql),
        {"identificador": payload.identificador},
    )
    user = query.mappings().first()

    if not user or not verify_password(payload.senha, user["senha_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas.",
        )

    # Garanta que tanto 'id' quanto 'sub' recebam o id do banco
    access_token = create_access_token(
        data={
            "sub": str(user["id"]),
            "id": user["id"],
            "cpf": user["cpf"],
        }
    )
    return {"access_token": access_token, "token_type": "bearer"}
