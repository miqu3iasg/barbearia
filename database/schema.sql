-- utf8mb4 para salvar os acentos corretamente
CREATE DATABASE IF NOT EXISTS barbearia CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE barbearia;

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

-- ---------------------------- inserts ----------------------------
INSERT INTO
    barbeiro (id, nome, status)
VALUES
    (1, 'Wild', 'Disponível'),
    (2, 'Alexandre de Moraes', 'Disponível'),
    (3, 'Ximbinha', 'Disponível'),
    (5, 'Cleito Rasta', 'Disponível');

-- preços e serviços
INSERT INTO
    servico (id, nome, preco)
VALUES
    (1, 'Degradê', 35.00),
    (2, 'Social', 30.00),
    (3, 'Corte na Tesoura', 40.00),
    (4, 'Sobrancelha', 15.00),
    (5, 'Barba', 25.00),
    (6, 'Pigmentação', 50.00),
    (7, 'Nevou', 120.00),
    (8, 'Reflexo', 100.00),
    (9, 'Alisamento', 80.00),
    (10, 'Corte + Barba', 55.00),
    (11, 'Corte + Sobrancelha', 45.00),
    (12, 'Corte + Barba + Sobrancelha', 65.00);

-- os clientes 5 e 8 não têm agendamento
INSERT INTO
    cliente (id, nome, telefone)
VALUES
    (1, 'Carlos Souza', '74999110001'),
    (2, 'Mateus Lima', '74999110002'),
    (3, 'Rafael Pereira', '74999110003'),
    (4, 'João Almeida', '74999110004'),
    (5, 'Diego Campos', '74999110005'),
    (6, 'Lucas Barbosa', '74999110006'),
    (7, 'Pedro Henrique', '74999110007'),
    (8, 'Gabriel Santos', '74999110008');

-- do 1 ao 9 já foram atendidos, do 10 ao 14 estão na fila
INSERT INTO
    agendamento (
        cliente_id,
        barbeiro_id,
        servico_id,
        data_agendamento,
        horario,
        pagamento,
        observacao,
        status
    )
VALUES
    (
        1,
        1,
        10,
        '2026-10-05',
        '09:00',
        'APOS_CORTE',
        NULL,
        'ATENDIDO'
    ),
    (
        2,
        2,
        1,
        '2026-10-05',
        '09:00',
        'PIX_ONLINE',
        'Degradê baixo',
        'ATENDIDO'
    ),
    (
        3,
        3,
        5,
        '2026-10-06',
        '10:00',
        'APOS_CORTE',
        NULL,
        'ATENDIDO'
    ),
    (
        1,
        1,
        1,
        '2026-10-08',
        '08:00',
        'APOS_CORTE',
        NULL,
        'ATENDIDO'
    ),
    (
        2,
        1,
        12,
        '2026-10-09',
        '10:00',
        'PIX_ONLINE',
        'Barba bem desenhada',
        'ATENDIDO'
    ),
    (
        4,
        5,
        7,
        '2026-10-09',
        '14:00',
        'PIX_ONLINE',
        'Quer o nevou bem claro',
        'ATENDIDO'
    ),
    (
        6,
        2,
        3,
        '2026-10-12',
        '11:00',
        'APOS_CORTE',
        NULL,
        'ATENDIDO'
    ),
    (
        7,
        3,
        11,
        '2026-10-13',
        '15:00',
        'PIX_ONLINE',
        NULL,
        'ATENDIDO'
    ),
    (
        3,
        5,
        6,
        '2026-10-14',
        '16:00',
        'APOS_CORTE',
        'Pigmentar só a barba',
        'ATENDIDO'
    ),
    (
        3,
        2,
        1,
        '2026-10-19',
        '14:00',
        'APOS_CORTE',
        NULL,
        'AGENDADO'
    ),
    (
        4,
        1,
        10,
        '2026-10-19',
        '15:00',
        'PIX_ONLINE',
        'Chego 5 minutos antes',
        'AGENDADO'
    ),
    (
        1,
        5,
        5,
        '2026-10-20',
        '09:00',
        'APOS_CORTE',
        NULL,
        'AGENDADO'
    ),
    (
        6,
        3,
        8,
        '2026-10-20',
        '10:00',
        'PIX_ONLINE',
        NULL,
        'AGENDADO'
    ),
    (
        7,
        1,
        2,
        '2026-10-21',
        '17:00',
        'APOS_CORTE',
        NULL,
        'AGENDADO'
    );

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

-- --------------------------- consultas ---------------------------
-- fila de atendimento
SELECT
    *
FROM
    vw_fila_atendimento;

-- barbeiros que faturaram 100 ou mais
SELECT
    b.nome AS barbeiro,
    COUNT(*) AS atendimentos,
    SUM(s.preco) AS total,
    AVG(s.preco) AS ticket_medio
FROM
    agendamento a
    INNER JOIN barbeiro b ON b.id = a.barbeiro_id
    INNER JOIN servico s ON s.id = a.servico_id
WHERE
    a.status = 'ATENDIDO'
GROUP BY
    b.id,
    b.nome
HAVING
    SUM(s.preco) >= 100
ORDER BY
    total DESC;

-- clientes que nunca agendaram
SELECT
    c.nome,
    c.telefone
FROM
    cliente c
    LEFT JOIN agendamento a ON a.cliente_id = c.id
WHERE
    a.id IS NULL;

-- quanto cada cliente gastou
SELECT
    c.nome,
    COUNT(a.id) AS agendamentos,
    COALESCE(SUM(s.preco), 0) AS total_gasto
FROM
    cliente c
    LEFT JOIN agendamento a ON a.cliente_id = c.id
    LEFT JOIN servico s ON s.id = a.servico_id
GROUP BY
    c.id,
    c.nome
ORDER BY
    total_gasto DESC;

-- serviços com preço acima da média
SELECT
    c.nome AS cliente,
    s.nome AS servico,
    s.preco
FROM
    agendamento a
    INNER JOIN cliente c ON c.id = a.cliente_id
    INNER JOIN servico s ON s.id = a.servico_id
WHERE
    s.preco > (
        SELECT
            AVG(preco)
        FROM
            servico
    );

-- agendamentos marcados
SELECT
    *
FROM
    vw_agendamentos;

-- -------------------------- transação --------------------------
-- atender o próximo da fila
START TRANSACTION;

-- o agendamento 10 é o primeiro da fila
UPDATE agendamento
SET
    status = 'ATENDIDO'
WHERE
    id = 10;

SELECT
    id,
    status
FROM
    agendamento
WHERE
    id = 10;

-- troque por COMMIT para confirmar
ROLLBACK;

-- ---------------------- testes de restrições ----------------------
-- esses comandos dão erro de propósito, vamos tirar o comentário para rodar um de cada vez
-- cliente que não existe
-- INSERT INTO agendamento (cliente_id, barbeiro_id, servico_id, data_agendamento, horario, pagamento)
-- VALUES (999, 1, 1, '2026-10-26', '09:00', 'APOS_CORTE');
-- telefone repetido
-- INSERT INTO cliente (nome, telefone)
-- VALUES ('Cliente Repetido', '74999110001');
-- cliente sem nome
-- INSERT INTO cliente (nome, telefone)
-- VALUES (NULL, '74999119999');
-- horário já ocupado
-- INSERT INTO agendamento (cliente_id, barbeiro_id, servico_id, data_agendamento, horario, pagamento)
-- VALUES (5, 1, 1, '2026-10-19', '15:00', 'APOS_CORTE');
-- pagamento inválido
-- INSERT INTO agendamento (cliente_id, barbeiro_id, servico_id, data_agendamento, horario, pagamento)
-- VALUES (5, 2, 1, '2026-10-22', '09:00', 'CARTAO');
-- preço negativo
-- INSERT INTO servico (nome, preco) VALUES ('Serviço Inválido', -10.00);
-- apagar barbeiro que já tem agendamento
-- DELETE FROM barbeiro WHERE id = 1;
-- mudar o id do cliente e ver os agendamentos acompanharem
-- START TRANSACTION;
-- UPDATE cliente SET id = 101 WHERE id = 1;
-- SELECT id, cliente_id FROM agendamento WHERE cliente_id IN (1, 101);
-- ROLLBACK;
