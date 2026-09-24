DROP TABLE IF EXISTS transacoes;
DROP TABLE IF EXISTS contas;
DROP TABLE IF EXISTS correntistas;

-- 1. Tabela de Clientes/Correntistas
CREATE TABLE correntistas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(150) NOT NULL,
    cpf VARCHAR(14) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabela de Contas Bancárias
CREATE TABLE contas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    correntista_id INTEGER NOT NULL,
    numero_conta VARCHAR(20) UNIQUE NOT NULL,
    saldo NUMERIC(15, 2) NOT NULL DEFAULT 0.00 CHECK (saldo >= 0.00),
    ativa BOOLEAN NOT NULL DEFAULT 1,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (correntista_id) REFERENCES correntistas (id) ON DELETE RESTRICT
);

-- 3. Tabela de Transações / Ledger Imutável (Extrato)
CREATE TABLE transacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conta_origem_id INTEGER,
    conta_destino_id INTEGER,
    tipo VARCHAR(20) NOT NULL,
    valor NUMERIC(15, 2) NOT NULL CHECK (valor > 0.00),
    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    descricao VARCHAR(255),
    FOREIGN KEY (conta_origem_id) REFERENCES contas (id),
    FOREIGN KEY (conta_destino_id) REFERENCES contas (id)
);
