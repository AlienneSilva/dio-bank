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

    # 3. Criação de conta para o titular logado
    res_conta = await client.post(
        "/contas/",
        json={"correntista_id": 2, "numero_conta": "1001-A"},
    )
    assert res_conta.status_code == 201


@pytest.mark.asyncio
async def test_operacoes_deposito_e_saque(client: AsyncClient):
    # 1. Login do titular 1
    res_log = await client.post(
        "/auth/login",
        json={"identificador": "11111111111", "senha": "senha123"},
    )
    assert res_log.status_code == 200
    token = res_log.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # A conta do Titular 1 criada no teste anterior é a id 2
    conta_id = 2

    # 2. Depósito em conta inexistente (404)
    res_dep_invalido = await client.post(
        "/transacoes/deposito", json={"conta_id": 99999, "valor": 200.0}
    )
    assert res_dep_invalido.status_code == 404

    # 3. Depósito válido
    res_dep = await client.post(
        "/transacoes/deposito", json={"conta_id": conta_id, "valor": 500.00}
    )
    assert res_dep.status_code == 200

    # 4. Saque sem autenticação (401/403)
    res_sem_auth = await client.post(
        "/transacoes/saque", json={"conta_id": conta_id, "valor": 50.0}
    )
    assert res_sem_auth.status_code in (401, 403)

    # 5. Saque com saldo insuficiente (400)
    res_saldo_insuf = await client.post(
        "/transacoes/saque",
        headers=headers,
        json={"conta_id": conta_id, "valor": 9999.00},
    )
    assert res_saldo_insuf.status_code == 400


@pytest.mark.asyncio
async def test_transferencia_e_seguranca_titularidade(client: AsyncClient):
    # 1. Cadastrar Titular 2 e Conta 2
    res_cad2 = await client.post(
        "/correntistas/",
        json={
            "nome": "Titular Dois",
            "cpf": "22222222222",
            "email": "titular2@teste.com",
            "senha": "senha456",
        },
    )
    assert res_cad2.status_code == 201

    # Titular 2 é id 3
    res_c2 = await client.post(
        "/contas/", json={"correntista_id": 3, "numero_conta": "2002-B"}
    )
    assert res_c2.status_code == 201

    conta_1_id = 2
    conta_2_id = 3

    # 2. Logins
    log1 = await client.post(
        "/auth/login",
        json={"identificador": "11111111111", "senha": "senha123"},
    )
    headers1 = {"Authorization": f"Bearer {log1.json()['access_token']}"}

    log2 = await client.post(
        "/auth/login",
        json={"identificador": "22222222222", "senha": "senha456"},
    )
    headers2 = {"Authorization": f"Bearer {log2.json()['access_token']}"}

    # 3. Tentativa de transferir da Conta 1 usando o token do Titular 2 (403 Forbidden)
    res_fraude = await client.post(
        "/transacoes/transferencia",
        headers=headers2,
        json={"conta_origem_id": conta_1_id, "conta_destino_id": conta_2_id, "valor": 50.00},
    )
    assert res_fraude.status_code == 403

    # 4. Transferência para a mesma conta (400 Bad Request)
    res_mesma_conta = await client.post(
        "/transacoes/transferencia",
        headers=headers1,
        json={"conta_origem_id": conta_1_id, "conta_destino_id": conta_1_id, "valor": 20.00},
    )
    assert res_mesma_conta.status_code == 400

    # 5. Transferência legítima (Titular 1 -> Conta 2)
    res_transf = await client.post(
        "/transacoes/transferencia",
        headers=headers1,
        json={"conta_origem_id": conta_1_id, "conta_destino_id": conta_2_id, "valor": 100.00},
    )
    assert res_transf.status_code == 200
