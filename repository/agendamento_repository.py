from connection import connect


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
        data_agendamento: Data a ser consultada, como objeto date ou string no formato
        'AAAA-MM-DD'.
        horario: Horário no formato 'H:MM'.
        pagamento: 'APOS_CORTE' ou 'PIX_ONLINE'.
        observacao: Texto livre, opcional, o valor default é None.

    Returns:
        O ID do novo barbeiro cadastrado, ou None se nenhuma linha foi inserida no
        banco de dados.
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
        Lista de dicionário com os horários ocupados. A lista fica vazia se não tem
        nenhum agendamento feito na data.
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
        A fila de atendimento (agendamentos ainda não atendidos) de um dia.
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


# TODO: def buscar_proximo_da_fila(data_agendamento):
