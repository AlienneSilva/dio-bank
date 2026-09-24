from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db_session
from src.schemas.schemas import LoginIn, TokenOut
from src.security import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login", response_model=TokenOut, status_code=status.HTTP_200_OK)
async def login(
    payload: LoginIn,
    session: AsyncSession = Depends(get_db_session),
):
    query_user = """
        SELECT id, nome, cpf, email, senha_hash
        FROM correntistas
        WHERE cpf = :identificador OR email = :identificador
    """
    result = await session.execute(
        text(query_user), {"identificador": payload.identificador}
    )
    usuario = result.mappings().first()

    # Validação segura do utilizador e da palavra-passe criptografada
    if not usuario or not verify_password(payload.senha, usuario["senha_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Gera o JWT assíncrono com o ID do titular no payload ('sub')
    token = create_access_token(
        data={"sub": str(usuario["id"]), "cpf": usuario["cpf"]}
    )

    return {"access_token": token, "token_type": "bearer"}
