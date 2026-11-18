from mysql.connector import IntegrityError

from model.barbeiro import barbeiro as Barbeiro
from repository import barbeiro_repository as repo

STATUS_VALIDOS = ("Disponível", "Ocupado")


def _montar_barbeiro(barbeiro_id, nome, status) -> Barbeiro:
    barbeiro = Barbeiro(barbeiro_id, (nome or "").strip(), status)
    barbeiro.verificar_nome()

    if barbeiro.status not in STATUS_VALIDOS:
        raise ValueError("Status inválido. Use 'Disponível' ou 'Ocupado'.")
    return barbeiro


def buscar_barbeiro(barbeiro_id: int) -> dict:
    barbeiro = repo.buscar_barbeiro_por_id(barbeiro_id)
    if barbeiro is None:
        raise ValueError("Barbeiro não encontrado.")
    return barbeiro


def listar_barbeiros() -> list:
    return repo.listar_todos_os_barbeiros()


def listar_barbeiros_disponiveis() -> list:
    return [
        b
        for b in repo.listar_todos_os_barbeiros()
        if Barbeiro(b["id"], b["nome"], b["status"]).verificar_disponibilidade()
    ]


def cadastrar_barbeiro(nome: str, status: str = "Disponível") -> int:
    barbeiro = _montar_barbeiro(None, nome, status)
    return repo.criar_barbeiro(barbeiro.nome, barbeiro.status)


def atualizar_barbeiro(barbeiro_id: int, nome: str, status: str) -> dict:
    buscar_barbeiro(barbeiro_id)

    barbeiro = _montar_barbeiro(barbeiro_id, nome, status)

    repo.atualizar_barbeiro(barbeiro_id, barbeiro.nome, barbeiro.status)
    return buscar_barbeiro(barbeiro_id)


def atualizar_status_barbeiro(barbeiro_id: int, status: str) -> dict:
    atual = buscar_barbeiro(barbeiro_id)
    barbeiro = _montar_barbeiro(barbeiro_id, atual["nome"], status)

    repo.atualizar_status_do_barbeiro(barbeiro_id, barbeiro.status)
    return buscar_barbeiro(barbeiro_id)


def excluir_barbeiro(barbeiro_id: int) -> None:
    buscar_barbeiro(barbeiro_id)

    try:
        repo.excluir_barbeiro(barbeiro_id)
    except IntegrityError:
        raise ValueError(
            "Não é possível excluir: o barbeiro possui agendamentos."
        ) from None
