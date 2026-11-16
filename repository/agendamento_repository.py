from database.connection import connect


def criar_agendamento(
    cliente_id: int,
    barbeiro_id: int,
    servico_id: int,
    data_agendamento,
    horario: str,
    pagamento: str,
    observacao: str = None,  # Recebe None como valor default
):
    """Cria um novo agendamento e salva no banco de dados.

    Args:
        cliente_id: Identificador único do cliente no banco de dados.
        barbeiro_id: Identificador único do barbeiro no banco de dados.
        servico_id: Identificador único do serviço no banco de dados.
        data_agendamento: Data do agendamento, como objeto date ou string no formato
        'AAAA-MM-DD'.
        horario: Horário do agendamento, como objeto time ou string no formato
        'HH:MM'.
        pagamento: 'APOS_CORTE' ou 'PIX_ONLINE'.
        observacao: Texto livre, opcional, o valor default é None.

    Returns:
        O ID do novo agendamento cadastrado.

    Raises:
        mysql.connector.IntegrityError: Se o barbeiro já tem agendamento na mesma
        data e horário, ou se algum ID informado não existe no banco de dados.
    """
    query = """
        INSERT INTO agendamento (
            cliente_id,
            barbeiro_id,
            servico_id,
            data_agendamento,
            horario,
            pagamento,
            observacao
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cnx = connect()
    try:
        cursor = cnx.cursor()
        cursor.execute(
            query,
            (
                cliente_id,
                barbeiro_id,
                servico_id,
                data_agendamento,
                horario,
                pagamento,
                observacao,
            ),
        )
        cnx.commit()
        return cursor.lastrowid
    except Exception:
        cnx.rollback()
        raise
    finally:
        cnx.close()


def listar_horarios_ocupados(barbeiro_id: int, data_agendamento):
    """Retorna os horários já ocupados de um barbeiro em uma data.

    Args:
        barbeiro_id: Identificador único do barbeiro no banco de dados.
        data_agendamento: Data a ser consultada, como objeto date ou string no formato
        'AAAA-MM-DD'.

    Returns:
        Lista com os horários ocupados, cada um como objeto timedelta (é assim que o
        conector MySQL devolve colunas TIME). A lista fica vazia se não tem nenhum
        agendamento feito na data.
    """
    query = """
        SELECT horario FROM agendamento
        WHERE barbeiro_id = %s AND data_agendamento = %s
    """
    cnx = connect()
    try:
        cursor = cnx.cursor(dictionary=True)
        cursor.execute(query, (barbeiro_id, data_agendamento))
        linhas = cursor.fetchall()

        horarios = []
        for linha in linhas:
            horarios.append(linha["horario"])

        return horarios
    finally:
        cnx.close()


def listar_fila_atendimento(data_agendamento):
    """Lista a fila de atendimentos do dia.

    Args:
        data_agendamento: Data a ser consultada, como objeto date ou string no formato
        'AAAA-MM-DD'.

    Returns:
        Lista de dicionários com os agendamentos ainda não atendidos do dia, ordenados
        por horário. Cada dicionário tem as chaves 'agendamento_id', 'cliente',
        'servico', 'barbeiro' e 'horario'. A lista fica vazia se não há ninguém na fila.
    """
    query = """
        SELECT agendamento_id, cliente, servico, barbeiro, horario
        FROM vw_fila_atendimento
        WHERE data_agendamento = %s
        ORDER BY horario
    """
    cnx = connect()
    try:
        cursor = cnx.cursor(dictionary=True)
        cursor.execute(query, (data_agendamento,))
        return cursor.fetchall()
    finally:
        cnx.close()


def buscar_proximo_da_fila(data_agendamento):
    """Retorna o próximo agendamento da fila de atendimento em uma determinada data.

    Args:
        data_agendamento: Data a ser consultada, como objeto date ou string no formato
        'AAAA-MM-DD'.

    Returns:
        Um dicionário com os dados do próximo agendamento da fila (o de menor horário),
        no mesmo formato de listar_fila_atendimento, ou None se não há ninguém na fila
        para ser atendido.
    """
    fila = listar_fila_atendimento(data_agendamento)
    if len(fila) == 0:
        return None
    return fila[0]


def buscar_agendamento_por_id(agendamento_id: int):
    """Retorna um agendamento pelo ID.

    Args:
        agendamento_id: Identificador único do agendamento no banco de dados.

    Returns:
        Um dicionário com os dados do agendamento ('id', 'cliente_id', 'barbeiro_id',
        'servico_id', 'data_agendamento', 'horario', 'pagamento', 'observacao' e
        'status'), ou None se não existir nenhum agendamento no banco de dados com o
        ID desejado. 'data_agendamento' vem como date e 'horario' como timedelta.
    """

    query = """
        SELECT
            id,
            cliente_id,
            barbeiro_id,
            servico_id,
            data_agendamento,
            horario,
            pagamento,
            observacao,
            status
        FROM agendamento
        WHERE id=%s
    """
    cnx = connect()
    try:
        cursor = cnx.cursor(dictionary=True)
        cursor.execute(query, (agendamento_id,))
        return cursor.fetchone()
    finally:
        cnx.close()


def listar_todos_os_agendamentos():
    """Retorna todos os agendamentos cadastrados no banco de dados.

    Returns:
        Uma lista de dicionários com os dados de todos os agendamentos cadastrados, no
        mesmo formato de buscar_agendamento_por_id. A lista fica vazia se não há
        nenhum agendamento.
    """
    query = """
        SELECT
            id,
            cliente_id,
            barbeiro_id,
            servico_id,
            data_agendamento,
            horario,
            pagamento,
            observacao,
            status
        FROM agendamento
    """
    cnx = connect()
    try:
        cursor = cnx.cursor(dictionary=True)
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        cnx.close()


def existe_conflito_de_horario(barbeiro_id: int, data_agendamento, horario: str):
    """Verifica se um barbeiro já tem agendamento em uma data e horário.

    Args:
        barbeiro_id: Identificador único do barbeiro no banco de dados.
        data_agendamento: Data a ser consultada, como objeto date ou string no formato
        'AAAA-MM-DD'.
        horario: Horário a ser consultado, como objeto time ou string no formato
        'HH:MM'.

    Returns:
        True se o barbeiro já tem agendamento na data e horário, ou False se o horário
        está livre.
    """
    query = """
        SELECT id FROM agendamento
        WHERE barbeiro_id = %s AND data_agendamento = %s AND horario = %s
    """
    cnx = connect()
    try:
        cursor = cnx.cursor()
        cursor.execute(query, (barbeiro_id, data_agendamento, horario))
        return cursor.fetchone() is not None
    finally:
        cnx.close()


def atualizar_status_do_agendamento(agendamento_id: int, status: str):
    """Atualiza o status de um agendamento.

    Args:
        agendamento_id: Identificador único do agendamento no banco de dados.
        status: Novo status do agendamento: 'AGENDADO' ou 'ATENDIDO'.

    Returns:
        True se o status do agendamento foi alterado, ou False se nenhuma linha foi
        alterada (o agendamento não existe, ou já estava com o status informado).

    Raises:
        mysql.connector.IntegrityError: Se o status informado não for 'AGENDADO' nem
        'ATENDIDO' (viola o CHECK da tabela).
    """
    query = "UPDATE agendamento SET status = %s WHERE id = %s"
    cnx = connect()
    try:
        cursor = cnx.cursor()
        cursor.execute(query, (status, agendamento_id))
        cnx.commit()
        return cursor.rowcount > 0
    except Exception:
        cnx.rollback()
        raise
    finally:
        cnx.close()


def excluir_agendamento(agendamento_id: int):
    """Exclui um agendamento do banco de dados.

    Args:
        agendamento_id: Identificador único do agendamento no banco de dados.

    Returns:
        True se o agendamento existia e foi excluído, ou False se não existe nenhum
        agendamento no banco de dados com o ID informado.
    """
    query = "DELETE FROM agendamento WHERE id = %s"
    cnx = connect()
    try:
        cursor = cnx.cursor()
        cursor.execute(query, (agendamento_id,))
        cnx.commit()
        return cursor.rowcount > 0
    except Exception:
        cnx.rollback()
        raise
    finally:
        cnx.close()
