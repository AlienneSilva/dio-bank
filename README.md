DIO Bank API 💳⚡

Uma API bancária assíncrona, robusta e de alta confiabilidade desenvolvida com FastAPI, SQLAlchemy 2.0 (async) e SQLite/aiosqlite. 

O sistema conta com proteção nativa contra race conditions em operações de débito, autenticação via JWT, controle de versão de banco com Alembic e testes automatizados de concorrência com Pytest.

🚀 Principais Funcionalidades

Operações Atômicas e Concorrência Segura: roteção contra saldo negativo e duplicidade de débitos através de instruções SQL atômicas com verificação de afetação de linhas (rowcount).

Autenticação & Autorização: Autenticação stateless via Bearer Token (JWT), com validação rigorosa de titularidade de conta para saques e transferências (bloqueio de fraudes com HTTP 403).

Tratamento Centralizado de Exceções: Formatação padronizada de erros HTTP, violações de integridade do banco (IntegrityError) e validações de esquema do Pydantic.

Migrações com Alembic: Controle declarativo e versionado de evolução do esquema de dados.

Documentação Interativa: OpenAPI v3 categorizada por tags de domínio com Swagger UI e ReDoc.

Testes Automatizados: Bateria de testes unitários e de integração de ponta a ponta, incluindo simulações de carga concorrente via asyncio.gather.

🛠️ Tecnologias Utilizadas

Linguagem: Python 3.12+
Framework Web: FastAPI
ORM / Conectividade: SQLAlchemy 2.0 (Async Engine) + aiosqlite
Gerenciador de Dependências: Poetry
Migrações: Alembic
Segurança: Bcrypt + PyJWT
Validação de Dados: Pydantic v2
Testes: Pytest, AnyIO, HTTPX

📁 Estrutura do Projetodio_bank/
├── alembic/              # Scripts e configurações de migração de banco
├── src/
│   ├── controllers/      # Roteadores FastAPI (auth, correntista, contas, transacoes)
│   ├── models/           # Modelos declarativos SQLAlchemy
│   ├── schemas/          # Schemas de validação e serialização Pydantic
│   ├── app.py            # Instância FastAPI, middlewares e handlers de erro
│   ├── config.py         # Configurações de ambiente via Pydantic Settings
│   ├── db.py             # Configuração da engine assíncrona e SessionLocal
│   ├── exceptions.py     # Hierarquia de exceções personalizadas de negócio
│   ├── schema.sql        # Script de inicialização DDL do banco
│   └── security.py       # Funções criptográficas e autenticação JWT
├── tests/
│   ├── integration/      # Testes de ponta a ponta e concorrência
│   ├── unit/             # Testes unitários (hashing, tokens, validações)
│   └── conftest.py       # Fixtures assíncronas e isolamento de banco de teste
├── alembic.ini
├── pyproject.toml
└── README.md

⚙️ Instalação e Execução

1. Pré-requisitosPython instalado (versão 3.12 ou superior)Poetry instalado (pip install poetry)
2. Clonar o repositório e instalar dependências
        git clone https://github.com/seu-usuario/dio_bank.git
        cd dio_bank
        poetry install
3. Configurar variáveis de ambiente
    Crie um arquivo .env na raiz do projeto (ou utilize os valores padrão de desenvolvimento):
        DATABASE_URL=sqlite+aiosqlite:///bank.db
        SECRET_KEY=sua_chave_secreta_super_segura_para_jwt
        ALGORITHM=HS256
        ACCESS_TOKEN_EXPIRE_MINUTES=30
4. Executar migrações do banco de dados
        poetry run alembic upgrade head
5. Iniciar a API
        poetry run uvicorn src.app:app --reload

        
A aplicação estará acessível em: http://127.0.0.1:8000

📖 Documentação da API

Com a aplicação rodando, acesse a documentação interativa:

Swagger UI: http://127.0.0.1:8000/docs
ReDoc: http://127.0.0.1:8000/redoc

Principais Rotas:
Método      Endpoint                            Descrição                                                Autenticação    
POST    /correntistas/                      Criação de novo correntista                                     Pública
POST    /auth/login                         Autenticação e obtenção do Bearer Token                         Pública
POST    /contas/                            Abertura de conta bancária                                      Pública
POST    /transacoes/deposito                Depósito em conta bancária ativa                                Pública
POST    /transacoes/saque                   Saque atômico com verificação de saldo                          Bearer Token
POST    /transacoes/transferencia           Transferência atômica entre contas distintas                    Bearer Token


🧪 Testes Automatizados

A suíte de testes valida a integridade funcional e simula concorrência em tempo real.
Executar todos os testes:
    poetry run pytest -v
O que é testado:
Concorrência Real (test_concorrencia.py): 10 requisições simultâneas de saque de R$ 20,00 disparadas paralelamente via asyncio.gather contra uma conta com apenas R$ 100,00 de saldo. 
Exatamente 5 requisições são aceitas (HTTP 200) e 5 são rejeitadas (HTTP 400), comprovando a impossibilidade de saldo negativo.

Segurança de Titularidade (test_transcoes.py): Tentativas de saque ou transferência de contas pertencentes a outros titulares são interceptadas com HTTP 403 Forbidden.

Criptografia e Segurança (test_utils.py): Geração de hash seguro via bcrypt e codificação/decodificação de tokens JWT.

🛡️ LicençaEste projeto é desenvolvido para fins didáticos e práticos sob a licença MIT.