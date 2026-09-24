from datetime import timedelta
import pytest
from src.security import create_access_token, hash_password, verify_password


def test_hash_password_gera_hash_valido():
    senha = "minhaSenhaSegura123"
    hash_gerado = hash_password(senha)

    assert hash_gerado is not None
    assert "$" in hash_gerado
    assert hash_gerado != senha


def test_verify_password_sucesso():
    senha = "senhaCorreta"
    hash_gerado = hash_password(senha)

    assert verify_password(senha, hash_gerado) is True


def test_verify_password_falha():
    senha = "senhaCorreta"
    hash_gerado = hash_password(senha)

    assert verify_password("senhaErrada", hash_gerado) is False
    assert verify_password("", hash_gerado) is False


def test_create_access_token_estrutura():
    payload = {"sub": "1", "nome": "Teste"}
    token = create_access_token(payload, expires_delta=timedelta(minutes=15))

    partes = token.split(".")
    assert len(partes) == 3
    assert len(token) > 20
