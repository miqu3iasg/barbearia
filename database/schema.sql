-- utf8mb4 para salvar os acentos corretamente
CREATE DATABASE IF NOT EXISTS barbearia_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE barbearia_db;

-- --------------------------- tabelas ---------------------------
CREATE TABLE cliente (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    telefone VARCHAR(15) NOT NULL UNIQUE,
    CONSTRAINT ck_cliente_telefone CHECK (CHAR_LENGTH(telefone) BETWEEN 10 AND 15)
);

CREATE TABLE barbeiro (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    status VARCHAR(10) NOT NULL DEFAULT 'Disponível', -- disponível ou ocupado
    CONSTRAINT ck_barbeiro_status CHECK (status IN ('Disponível', 'Ocupado'))
);

CREATE TABLE servico (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(50) NOT NULL UNIQUE,
    preco DECIMAL(10, 2) NOT NULL, -- decimal e não float, para não errar o arredondamento
    CONSTRAINT ck_servico_preco CHECK (preco > 0)
);

CREATE TABLE agendamento (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    barbeiro_id INT NOT NULL,
    servico_id INT NOT NULL,
    data_agendamento DATE NOT NULL,
    horario TIME NOT NULL,
    pagamento VARCHAR(20) NOT NULL, -- apos_corte ou pix_online
    observacao VARCHAR(255),
    status VARCHAR(20) NOT NULL DEFAULT 'AGENDADO', -- agendado ou atendido
    -- não deixa apagar quem já tem agendamento
    CONSTRAINT fk_agend_cliente FOREIGN KEY (cliente_id) REFERENCES cliente (id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_agend_barbeiro FOREIGN KEY (barbeiro_id) REFERENCES barbeiro (id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_agend_servico FOREIGN KEY (servico_id) REFERENCES servico (id) ON DELETE RESTRICT ON UPDATE CASCADE,
    -- o mesmo barbeiro não pode ter dois agendamentos no mesmo horário
    CONSTRAINT uq_barbeiro_data_horario UNIQUE (barbeiro_id, data_agendamento, horario),
    CONSTRAINT ck_agend_pagamento CHECK (pagamento IN ('APOS_CORTE', 'PIX_ONLINE')),
    CONSTRAINT ck_agend_status CHECK (status IN ('AGENDADO', 'ATENDIDO'))
);

-- ---------------------------- índices ----------------------------
CREATE INDEX idx_agend_cliente ON agendamento (cliente_id);

CREATE INDEX idx_agend_data ON agendamento (data_agendamento);

CREATE INDEX idx_agend_status ON agendamento (status);

-- ----------------------------- views -----------------------------
-- fila de atendimento
CREATE VIEW vw_fila_atendimento AS
SELECT
    a.id AS agendamento_id,
    c.nome AS cliente,
    s.nome AS servico,
    b.nome AS barbeiro,
    a.data_agendamento,
    a.horario
FROM
    agendamento a
    INNER JOIN cliente c ON c.id = a.cliente_id
    INNER JOIN servico s ON s.id = a.servico_id
    INNER JOIN barbeiro b ON b.id = a.barbeiro_id
WHERE
    a.status = 'AGENDADO'
ORDER BY
    a.id;

-- agendamentos marcados
CREATE VIEW vw_agendamentos AS
SELECT
    a.id AS agendamento_id,
    c.nome AS cliente,
    a.data_agendamento,
    b.nome AS barbeiro,
    a.horario,
    s.nome AS servico,
    a.status
FROM
    agendamento a
    INNER JOIN cliente c ON c.id = a.cliente_id
    INNER JOIN barbeiro b ON b.id = a.barbeiro_id
    INNER JOIN servico s ON s.id = a.servico_id
ORDER BY
    a.id;
