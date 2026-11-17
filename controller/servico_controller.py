"""Controller de serviços. Erros de regra de negócio levantam ValueError."""

from decimal import Decimal, InvalidOperation

from mysql.connector import IntegrityError

from model.servico import servico as Servico
from repository import servico_repository as repo


def _converter_preco(preco) -> Decimal:
    """Converte pra Decimal com 2 casas (aceita '35,50' e '35.50')."""
    try:
        valor = Decimal(str(preco).strip().replace(",", "."))
        if valor.is_finite():
            return valor.quantize(Decimal("0.01"))
    except InvalidOperation:
        pass
    raise ValueError("O preço deve ser um número.")


def _montar_servico(servico_id, nome, preco) -> Servico:
    servico = Servico(servico_id, (nome or "").strip(), _converter_preco(preco))
    if not servico.validar_nome():
        raise ValueError("O nome do Serviço é obrigatório!")
    if not servico.validar_preco():
        raise ValueError("O preço do Serviço deve ser maior que zero.")
    return servico


def buscar_servico(servico_id: int) -> dict:
    servico = repo.buscar_servico_por_id(servico_id)
    if servico is None:
        raise ValueError("Serviço não encontrado.")
    return servico


def listar_servicos() -> list:
    return repo.listar_todos_os_servicos()


def cadastrar_servico(nome: str, preco) -> int:
    servico = _montar_servico(None, nome, preco)
    try:
        return repo.criar_servico(servico.nome, servico.preco)
    except IntegrityError:
        raise ValueError("Já existe um serviço com esse nome.") from None


def atualizar_servico(servico_id: int, nome: str, preco) -> dict:
    buscar_servico(servico_id)
    servico = _montar_servico(servico_id, nome, preco)
    try:
        # retorno ignorado: o MySQL devolve rowcount 0 se nada mudou de fato
        repo.atualizar_servico(servico_id, servico.nome, servico.preco)
    except IntegrityError:
        raise ValueError("Já existe outro serviço com esse nome.") from None
    return buscar_servico(servico_id)


def excluir_servico(servico_id: int) -> None:
    buscar_servico(servico_id)
    try:
        repo.excluir_servico(servico_id)
    except IntegrityError:
        raise ValueError(
            "Não é possível excluir: o serviço possui agendamentos."
        ) from None
