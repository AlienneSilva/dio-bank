import base64
import hashlib
import hmac
import json
import os
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.db import get_db_session

# --- Funções de Hash e Token ---

def hash_password(password: str) -> str:
    salt = os.urandom(16)
    kdf = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, 100_000
    )
    return f"{salt.hex()}${kdf.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        salt_hex, hash_hex = hashed_password.split("$")
        salt = bytes.fromhex(salt_hex)
        kdf = hashlib.pbkdf2_hmac(
            "sha256", plain_password.encode("utf-8"), salt, 100_000
        )
        return hmac.compare_digest(kdf.hex(), hash_hex)
    except Exception:
        return False


def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=60)
    to_encode.update({"exp": int(expire.timestamp())})

    header = {"alg": "HS256", "typ": "JWT"}
    header_b64 = _base64url_encode(json.dumps(header).encode("utf-8"))
    payload_b64 = _base64url_encode(json.dumps(to_encode).encode("utf-8"))

    secret = getattr(settings, "SECRET_KEY", "dio_bank_super_secret_key_2026")
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    signature = hmac.new(
        secret.encode("utf-8"), signing_input, hashlib.sha256
    ).digest()
    signature_b64 = _base64url_encode(signature)

    return f"{header_b64}.{payload_b64}.{signature_b64}"


# --- Dependência de Autenticação para proteger rotas ---

security_scheme = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    token = credentials.credentials
    try:
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Token inválido")

        payload_raw = parts[1]
        payload_raw += "=" * (-len(payload_raw) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_raw.encode()))

        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Payload sem sub")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    res = await session.execute(
        text("SELECT id, nome, cpf, email FROM correntistas WHERE id = :id"),
        {"id": int(user_id)},
    )
    user = res.mappings().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado.",
        )

    return dict(user)
