import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_fluxo_correntistas_e_contas(client: AsyncClient):
    # 1. Cadastro com sucesso
    res_cad = await client.post(
        "/correntistas/",
        json={
            "nome": "Titular Um",
            "cpf": "11111111111",
            "email": "titular1@teste.com",
            "senha": "senha123",
        },
    )
    assert res_cad.status_code == 201

    # 2. Login correto
    res_log = await client.post(
        "/auth/login",
        json={"identificador": "11111111111", "senha": "senha123"},
    )
    assert res_log.status_code == 200
    assert "access_token" in res_log.json()

    # 3. Login com senha errada
    res_log_erro = await client.post(
        "/auth/login",
        json={"identificador": "11111111111", "senha": "senhaInvalida"},
    )
    assert res_log_erro.status_code in (401, 404)

    # 4. Criar Conta 1
    res_conta = await client.post(
        "/contas/", json={"correntista_id": 1, "numero_conta": "1001-A"}
    )
    assert res_conta.status_code == 201


@pytest.mark.asyncio
async def test_operacoes_deposito_e_saque(client: AsyncClient):
    # Obter token do titular 1
    res_log = await client.post(
        "/auth/login",
        json={"identificador": "11111111111", "senha": "senha123"},
    )
    token = res_log.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Depósito em conta inexistente (404)
    res_dep_invalido = await client.post(
        "/transacoes/deposito", json={"conta_id": 9999, "valor": 200.0}
    )
    assert res_dep_invalido.status_code == 404

    # 2. Depósito válido na Conta 1
    res_dep = await client.post(
        "/transacoes/deposito", json={"conta_id": 1, "valor": 500.00}
    )
    assert res_dep.status_code == 200

    # 3. Saque sem autenticação (401/403)
    res_sem_auth = await client.post(
        "/transacoes/saque", json={"conta_id": 1, "valor": 50.0}
    )
    assert res_sem_auth.status_code in (401, 403)

    # 4. Saque com saldo insuficiente (400)
    res_saldo_insuf = await client.post(
        "/transacoes/saque",
        headers=headers,
        json={"conta_id": 1, "valor": 9999.00},
    )
    assert res_saldo_insuf.status_code == 400

    # 5. Saque válido com saldo suficiente (200)
    res_saque_ok = await client.post(
        "/transacoes/saque",
        headers=headers,
        json={"conta_id": 1, "valor": 150.00},
    )
    assert res_saque_ok.status_code == 200


@pytest.mark.asyncio
async def test_transferencia_e_seguranca_titularidade(client: AsyncClient):
    # Cadastrar Titular 2 e Conta 2
    await client.post(
        "/correntistas/",
        json={
            "nome": "Titular Dois",
            "cpf": "22222222222",
            "email": "titular2@teste.com",
            "senha": "senha456",
        },
    )
    await client.post(
        "/contas/", json={"correntista_id": 2, "numero_conta": "2002-B"}
    )

    # Tokens dos titulares
    log1 = await client.post(
        "/auth/login",
        json={"identificador": "11111111111", "senha": "senha123"},
    )
    token1 = log1.json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}

    log2 = await client.post(
        "/auth/login",
        json={"identificador": "22222222222", "senha": "senha456"},
    )
    token2 = log2.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    # 1. Tentativa de transferir de Conta 1 usando o token do Titular 2 (403 Forbidden)
    res_fraude = await client.post(
        "/transacoes/transferencia",
        headers=headers2,
        json={"conta_origem_id": 1, "conta_destino_id": 2, "valor": 50.00},
    )
    assert res_fraude.status_code == 403

    # 2. Transferência para a mesma conta (400 Bad Request)
    res_mesma_conta = await client.post(
        "/transacoes/transferencia",
        headers=headers1,
        json={"conta_origem_id": 1, "conta_destino_id": 1, "valor": 20.00},
    )
    assert res_mesma_conta.status_code == 400

    # 3. Transferência legítima (Titular 1 -> Conta 2)
    res_transf = await client.post(
        "/transacoes/transferencia",
        headers=headers1,
        json={"conta_origem_id": 1, "conta_destino_id": 2, "valor": 100.00},
    )
    assert res_transf.status_code == 200

    # 4. Verificar extrato da Conta 1
    res_extrato = await client.get("/contas/1/extrato")
    assert res_extrato.status_code == 200
