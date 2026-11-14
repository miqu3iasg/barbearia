USE barbearia;

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
    (12, 'Corte + Barba + Sobrancelha', 65.00)
ON DUPLICATE KEY UPDATE
    nome = VALUES(nome),
    preco = VALUES(preco);

INSERT INTO
    barbeiro (id, nome, status)
VALUES
    (1, 'Wild', 'Disponível'),
    (2, 'Alexandre de Moraes', 'Disponível'),
    (3, 'Ximbinha', 'Disponível'),
    (4, 'Cleito Rasta', 'Disponível')
ON DUPLICATE KEY UPDATE
    nome = VALUES(nome);
