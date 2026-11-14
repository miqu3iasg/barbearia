from connection import connect


def criar_cliente(nome: str, telefone: int):
    """Cria um novo cliente e salva ele no banco de dados.

    Args:
        nome: Nome do cliente a ser salvo.
        telefone: Telefone do cliente.

    Returns:
        O ID do novo cliente salvo, ou None se nenhuma linha foi inserida no banco de
        dados.
    """
    query = "INSERT INTO cliente(nome, telefone) VALUES (%s, %s)"
    cnx = connect()
    try:
        cursor = cnx.cursor()
        cursor.execute(query, (nome, telefone))
        cursor.commit()
        return cursor.lastrowid
    finally:
        cnx.close()


def buscar_cliente_por_id(cliente_id: int):
    """Retorna um cliente pelo ID.

    Args:
        cliente_id: Identiicador único do cliente no banco de dados.

    Returns:
        Um dicionário com os dados do cliente, ou None se não existir nenhum cliente no
        banco de dados com o ID desejado.
    """
    query = "SELECT nome, telefone FROM clientes WHERE id = %s"
    cnx = connect()
    try:
        cursor = cnx.cursor(dictionary=True)
        cursor.execute(query, (cliente_id))
        return cursor.fetchone()
    finally:
        cnx.close()


def listar_todos_os_clientes():
    """Retorna todos os clientes cadastrados no banco de dados.

    Returns:
        Uma lista de dicionários com os dados de todos os clientes cadastrados.
    """
    cnx = connect()
    try:
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT nome, telefone FROM clientes")
        return cursor.fetchall()
    finally:
        cnx.close()


def excluir_cliente(cliente_id):
    """Exclui um cliente do banco de dados.

    Args:
        cliente_id: Identiicador único do cliente no banco de dados.

    Returns:
        True se o cliente foi encontrado e deletado com sucesso, ou False se não existe
        cliente com o id cadastrado.
    """
    query = "DELETE FROM clientes where id = %s"
    cnx = connect()
    try:
        cursor = cnx.cursor()
        cursor.execute(query, (cliente_id))
        cnx.commit()
        return cursor.rowcount > 0
    finally:
        cnx.close()


def atualizar_cliente(cliente_id: int, nome: str, telefone: int):
    """Atualiza todos os campos no banco de dados de um cliente já cadastrado.

    Args:
        cliente_id: Identificador único do cliente no banco de dados.
        nome: Nome do cliente a ser salvo.
        telefone: Telefone do cliente.

    Returns:
        True se o cliente foi encontrado e atualizado com sucesso, ou False se não
        existe cliente com o id cadastrado.
    """
    query = "UPDATE clientes SET nome=%s, telefone=%s WHERE id=%s"
    cnx = connect()
    try:
        cursor = cnx.cursor()
        cursor.execute(query, (nome, telefone, cliente_id))
        cursor.commit()
        return cursor.rowcount > 0
    finally:
        cnx.close()
