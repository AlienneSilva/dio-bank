import asyncio
from decimal import Decimal
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_concorrencia_saques_simultaneos_impede_saldo_negativo(
    client: AsyncClient,
):
    # 1. Cria correntista com saldo inicial
    res_user = await client.post(
        "/correntistas/",
        json={
            "nome": "Usuario Concorrencia",
            "cpf": "99988877766",
            "email": "concorrencia@teste.com",
            "senha": "senhaSegura123",
        },
    )
    assert res_user.status_code == 201

    # 2. Cria conta bancária
    res_conta = await client.post(
        "/contas/",
        json={"correntista_id": 1, "numero_conta": "9999-C"},
    )
    assert res_conta.status_code == 201
    conta_id = res_conta.json().get("id", 1)

    # 3. Autentica e extrai token
    res_login = await client.post(
        "/auth/login",
        json={"identificador": "99988877766", "senha": "senhaSegura123"},
    )
    token = res_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 4. Deposita R$ 100,00
    res_deposito = await client.post(
        "/transacoes/deposito",
        json={"conta_id": conta_id, "valor": 100.00},
    )
    assert res_deposito.status_code == 200

    # 5. Prepara 10 requisições simultâneas de saque de R$ 20,00 cada
    #    (10 x 20 = 200, mas o saldo é apenas 100)
    async def disparar_saque():
        return await client.post(
            "/transacoes/saque",
            headers=headers,
            json={"conta_id": conta_id, "valor": 20.00},
        )

    tarefas = [disparar_saque() for _ in range(10)]
    respostas = await asyncio.gather(*tarefas)

    # 6. Analisa os resultados das respostas concorrentes
    sucessos = sum(1 for r in respostas if r.status_code == 200)
    falhas = sum(1 for r in respostas if r.status_code == 400)

    # Devem passar exatamente 5 e falhar exatamente 5
    assert sucessos == 5, f"Esperado 5 sucessos, obtido: {sucessos}"
    assert falhas == 5, f"Esperado 5 falhas por falta de saldo, obtido: {falhas}"
