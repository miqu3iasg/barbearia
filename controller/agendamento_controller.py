"""Controller de agendamentos. Erros de regra de negócio levantam ValueError."""

from datetime import date, datetime, time, timedelta

from mysql.connector import IntegrityError

from model.agendamento import agendamento as Agendamento
from repository import (
    agendamento_repository as repo,
    barbeiro_repository,
    cliente_repository,
    servico_repository,
)

# Grade da barbearia: 09:00 até 17:30, de 30 em 30 min. Ajuste se precisar.
HORARIOS_ATENDIMENTO = [f"{h:02d}:{m:02d}" for h in range(9, 18) for m in (0, 30)]


def _para_date(valor) -> date:
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    try:
        return datetime.strptime(str(valor).strip(), "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Data inválida. Use o formato AAAA-MM-DD.") from None


def _para_time(valor) -> time:
    if isinstance(valor, time):
        return valor.replace(second=0, microsecond=0)
    try:
        return datetime.strptime(str(valor).strip()[:5], "%H:%M").time()
    except ValueError:
        raise ValueError("Horário inválido. Use o formato HH:MM.") from None


def formatar_horario(valor) -> str:
    """Converte o TIME do MySQL (timedelta) ou time em 'HH:MM'."""
    if isinstance(valor, timedelta):
        minutos = int(valor.total_seconds()) // 60
        return f"{minutos // 60:02d}:{minutos % 60:02d}"
    return str(valor)[:5]


def buscar_agendamento(agendamento_id: int) -> dict:
    agendamento = repo.buscar_agendamento_por_id(agendamento_id)
    if agendamento is None:
        raise ValueError("Agendamento não encontrado.")
    return agendamento


def listar_agendamentos() -> list:
    return repo.listar_todos_os_agendamentos()


def listar_horarios_livres(barbeiro_id: int, data_agendamento) -> list:
    """Horários ('HH:MM') livres do barbeiro na data, sem os que já passaram."""
    if barbeiro_repository.buscar_barbeiro_por_id(barbeiro_id) is None:
        raise ValueError("Barbeiro não encontrado.")
    data = _para_date(data_agendamento)
    agora = datetime.now()
    if data < agora.date():
        return []

    ocupados = {
        formatar_horario(h) for h in repo.listar_horarios_ocupados(barbeiro_id, data)
    }
    livres = [h for h in HORARIOS_ATENDIMENTO if h not in ocupados]
    if data == agora.date():
        livres = [h for h in livres if h > agora.strftime("%H:%M")]
    return livres


def ver_fila_do_dia(data_agendamento) -> list:
    return repo.listar_fila_atendimento(_para_date(data_agendamento))


def proximo_da_fila(data_agendamento):
    """Próximo da fila do dia, ou None se não houver ninguém."""
    return repo.buscar_proximo_da_fila(_para_date(data_agendamento))


def agendar(
    cliente_id: int,
    barbeiro_id: int,
    servico_id: int,
    data_agendamento,
    horario,
    pagamento: str,
    observacao: str = None,
) -> int:
    """Valida e cria um agendamento. Retorna o ID do novo agendamento."""
    if cliente_repository.buscar_cliente_por_id(cliente_id) is None:
        raise ValueError("Cliente não encontrado.")
    if barbeiro_repository.buscar_barbeiro_por_id(barbeiro_id) is None:
        raise ValueError("Barbeiro não encontrado.")
    if servico_repository.buscar_servico_por_id(servico_id) is None:
        raise ValueError("Serviço não encontrado.")

    data, hora = _para_date(data_agendamento), _para_time(horario)
    if datetime.combine(data, hora) < datetime.now():
        raise ValueError("Não é possível agendar em um horário que já passou.")

    observacao = (observacao or "").strip() or None
    if observacao and len(observacao) > 255:
        raise ValueError("A observação deve ter no máximo 255 caracteres.")

    pagamento = (pagamento or "").strip().upper()
    modelo = Agendamento(
        None, cliente_id, barbeiro_id, servico_id,
        data, hora, pagamento, observacao, "AGENDADO",
    )
    if not modelo.validar_agendamento():
        raise ValueError("Cliente, barbeiro e serviço são obrigatórios.")
    if not modelo.validar_pagamento():
        raise ValueError("Pagamento inválido. Use 'APOS_CORTE' ou 'PIX_ONLINE'.")

    if repo.existe_conflito_de_horario(barbeiro_id, data, hora):
        raise ValueError("Esse barbeiro já tem agendamento nesse horário.")
    try:
        return repo.criar_agendamento(
            cliente_id, barbeiro_id, servico_id, data, hora, pagamento, observacao
        )
    except IntegrityError:  # dois clientes pegaram o mesmo horário ao mesmo tempo
        raise ValueError("Esse horário acabou de ser ocupado. Escolha outro.") from None


def concluir_atendimento(agendamento_id: int) -> dict:
    """Marca o agendamento como ATENDIDO (ele sai da fila)."""
    if buscar_agendamento(agendamento_id)["status"] == "ATENDIDO":
        raise ValueError("Esse agendamento já foi atendido.")
    repo.atualizar_status_do_agendamento(agendamento_id, "ATENDIDO")
    return buscar_agendamento(agendamento_id)


def cancelar_agendamento(agendamento_id: int) -> None:
    """Cancela (exclui) um agendamento que ainda não foi atendido."""
    if buscar_agendamento(agendamento_id)["status"] == "ATENDIDO":
        raise ValueError("Não é possível cancelar um agendamento já atendido.")
    repo.excluir_agendamento(agendamento_id)
