from typing import cast

from database.connection import connect


def criar_barbeiro(nome: str, status: str) -> int:
    """Cria um novo barbeiro e salva ele no banco de dados.

    Args:
        nome: Nome do barbeiro a ser cadastrado.
        status: Disponibilidade do barbeiro ('Disponível' ou 'Ocupado'). O valor default
        no banco de dados é 'Disponível'.

    Returns:
        O ID do novo barbeiro cadastrado.

    Raises:
        mysql.connector.Error: Se a inserção falhar.
    """
    query = "INSERT INTO barbeiro(nome, status) VALUES (%s, %s)"
    cnx = connect()
    try:
        cursor = cnx.cursor()
        cursor.execute(query, (nome, status))
        cnx.commit()
        return cast(int, cursor.lastrowid)
    except Exception:
        cnx.rollback()
        raise
    finally:
        cnx.close()


def buscar_barbeiro_por_id(barbeiro_id: int):
    """Retorna um barbeiro pelo ID.

    Args:
        barbeiro_id: Identificador único do barbeiro no banco de dados.

    Returns:
        Um dicionário com os dados do barbeiro, ou None se não existir nenhum barbeiro
        no banco de dados com o ID desejado.
    """
    query = "SELECT id, nome, status FROM barbeiro WHERE id = %s"
    cnx = connect()
    try:
        cursor = cnx.cursor(dictionary=True)
        cursor.execute(query, (barbeiro_id,))
        return cursor.fetchone()
    finally:
        cnx.close()


def listar_todos_os_barbeiros():
    """Retorna todos os barbeiros cadastrados no banco de dados.

    Returns:
        Uma lista de dicionários com os dados de todos os barbeiros cadastrados.
    """
    cnx = connect()
    try:
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT id, nome, status FROM barbeiro")
        return cursor.fetchall()
    finally:
        cnx.close()


def excluir_barbeiro(barbeiro_id: int):
    """Exclui um barbeiro do banco de dados.

    Args:
        barbeiro_id: Identificador único do barbeiro no banco de dados.

    Returns:
        True se o barbeiro foi encontrado e deletado com sucesso, ou False se não existe
        barbeiro com o id cadastrado.
    """
    query = "DELETE FROM barbeiro WHERE id = %s"
    cnx = connect()
    try:
        cursor = cnx.cursor()
        cursor.execute(query, (barbeiro_id,))
        cnx.commit()
        return cursor.rowcount > 0
    except Exception:
        cnx.rollback()
        raise
    finally:
        cnx.close()


def atualizar_barbeiro(barbeiro_id: int, nome: str, status: str):
    """Atualiza todos os campos no banco de dados de um barbeiro já cadastrado.

    Args:
        barbeiro_id: Identificador único do barbeiro no banco de dados.
        nome: Nome do barbeiro a ser atualizado.
        status: Disponibilidade do barbeiro ('Disponível' ou 'Ocupado').

    Returns:
        True se o barbeiro foi atualizado, ou False se não existe barbeiro com o id
        cadastrado ou se os dados informados já eram iguais aos salvos.
    """
    query = "UPDATE barbeiro SET nome=%s, status=%s WHERE id=%s"
    cnx = connect()
    try:
        cursor = cnx.cursor()
        cursor.execute(query, (nome, status, barbeiro_id))
        cnx.commit()
        return cursor.rowcount > 0
    except Exception:
        cnx.rollback()
        raise
    finally:
        cnx.close()


def atualizar_status_do_barbeiro(barbeiro_id: int, status: str):
    """Atualiza o status de um barbeiro já cadastrado no banco de dados.

    Args:
        barbeiro_id: Identificador único do barbeiro no banco de dados.
        status: Disponibilidade do barbeiro ('Disponível' ou 'Ocupado').

    Returns:
        True se o barbeiro foi atualizado, ou False se não existe barbeiro com o id
        cadastrado ou se os dados informados já eram iguais aos salvos.
    """
    query = "UPDATE barbeiro set status=%s WHERE id=%s"
    cnx = connect()
    try:
        cursor = cnx.cursor()
        cursor.execute(query, (status, barbeiro_id))
        cnx.commit()
        return cursor.rowcount > 0
    except:
        cnx.rollback()
        raise
    finally:
        cnx.close()
