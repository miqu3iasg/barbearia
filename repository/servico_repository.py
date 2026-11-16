from database.connection import connect


def criar_servico(nome: str, preco: float):
    """Cria um novo serviço e salva ele no banco de dados.

    Args:
        nome: Nome do serviço a ser cadastrado.
        preco: Preço do serviço. Deve ser maior que zero.

    Returns:
        O ID do novo serviço cadastrado, ou None se nenhuma linha foi inserida no
        banco de dados.
    """
    query = "INSERT INTO servico(nome, preco) VALUES (%s, %s)"
    cnx = connect()
    try:
        cursor = cnx.cursor()
        cursor.execute(query, (nome, preco))
        cnx.commit()
        return cursor.lastrowid
    except Exception:
        cnx.rollback()
        raise
    finally:
        cnx.close()


def buscar_servico_por_id(servico_id):
    """Retorna um serviço pelo ID

    Args:
        servico_id: Identificador único do serviço no banco de dados.

    Returns:
        Um dicionário com os dados do serviço, ou None se não existir nenhum serviço
        no banco de dados com o ID desejado.
    """
    query = "SELECT id, nome, preco FROM servico WHERE id = %s"
    cnx = connect()
    try:
        cursor = cnx.cursor(dictionary=True)
        cursor.execute(query, (servico_id,))
        return cursor.fetchone()
    finally:
        cnx.close()


def listar_todos_os_servicos():
    """Retorna todos os serviços cadastrados no banco de dados.

    Returns:
        Uma lista de dicionários com todos os dados de serviços cadastrados.
    """
    query = "SELECT id, nome preco FROM servico"
    cnx = connect()
    try:
        cursor = cnx.cursor(dictionary=True)
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        cnx.close()


def atualizar_servico(servico_id: int, nome: str, preco: float):
    """Atualiza todos os campos no banco de dados de um serviço já cadastrado.

    Args:
        servico_id: Identificador único do serviço no banco de dados.
        nome: Nome do serviço a ser atualizado.
        preco: Preço do serviço. Deve ser maior que zero.

    Returns:
        True se o serviço foi encontrado e atualizado com sucesso, ou False se não
        existe serviço com o id cadastrado.
    """
    query = "UPDATE set nome = %s, preco = %s FROM servico WHERE id = %s"
    cnx = connect()
    try:
        cursor = cnx.cursor()
        cursor.execute(query, (nome, preco, servico_id))
        cnx.commit()
        return cursor.rowcount > 0
    except Exception:
        cnx.rollback()
        raise
    finally:
        cnx.close()


def excluir_servico(servico_id: int):
    """Exclui um serviço do banco de dados.

    Args:
        servico_id: Identificador único do serviço no banco de dados.

    Returns:
        True se o serviço foi encontrado e deletado com sucesso, ou False se não existe
        serviço com o id cadastrado.
    """
    query = "DELETE FROM servico WHERE id = %s"
    cnx = connect()
    try:
        cursor = cnx.cursor()
        cursor.execute(query, (servico_id,))
        cnx.commit()
        return cursor.rowcount > 0
    except Exception:
        cnx.rollback()
        raise
    finally:
        cnx.close()
