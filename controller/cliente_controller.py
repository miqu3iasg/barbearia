"""Controller de clientes: valida com o model e persiste com o repository.

Convenção: erro de regra de negócio (dado inválido, não encontrado, conflito)
levanta ValueError com mensagem pronta pra mostrar pro usuário.
"""

from mysql.connector import IntegrityError

from model.cliente import Cliente
from repository import cliente_repository


def _normalizar_telefone(telefone) -> str:
    """Deixa só os dígitos, pra aceitar entradas como '(75) 99999-0000'."""
    return "".join(c for c in str(telefone or "") if c.isdigit())


def _montar_cliente(cliente_id, nome, telefone) -> Cliente:
    cliente = Cliente(cliente_id, (nome or "").strip(), _normalizar_telefone(telefone))
    cliente.validar_nome()  # levanta ValueError se estiver vazio
    if not cliente.validar_telefone():
        raise ValueError("O telefone do Cliente é obrigatório!")
    # mesma regra do CHECK da tabela (10 a 15 caracteres)
    if not 10 <= len(cliente.telefone) <= 15:
        raise ValueError("O telefone deve ter entre 10 e 15 dígitos.")
    return cliente


def buscar_cliente(cliente_id: int) -> dict:
    """Retorna o cliente ou levanta ValueError se ele não existir."""
    cliente = cliente_repository.buscar_cliente_por_id(cliente_id)
    if cliente is None:
        raise ValueError("Cliente não encontrado.")
    return cliente


def listar_clientes() -> list:
    """Retorna todos os clientes cadastrados."""
    return cliente_repository.listar_todos_os_clientes()


def cadastrar_cliente(nome: str, telefone: str) -> int:
    """Valida e cadastra um cliente. Retorna o ID do novo cliente."""
    cliente = _montar_cliente(None, nome, telefone)
    try:
        return cliente_repository.criar_cliente(cliente.nome, cliente.telefone)
    except IntegrityError:
        raise ValueError("Já existe um cliente cadastrado com esse telefone.") from None


def atualizar_cliente(cliente_id: int, nome: str, telefone: str) -> dict:
    """Valida e atualiza nome e telefone. Retorna o cliente atualizado."""
    buscar_cliente(cliente_id)  # garante que existe
    cliente = _montar_cliente(cliente_id, nome, telefone)
    try:
        # o retorno do repository é ignorado de propósito: o MySQL devolve
        # rowcount 0 quando os dados novos são iguais aos antigos
        cliente_repository.atualizar_cliente(
            cliente_id, cliente.nome, cliente.telefone
        )
    except IntegrityError:
        raise ValueError("Já existe outro cliente com esse telefone.") from None
    return buscar_cliente(cliente_id)


def excluir_cliente(cliente_id: int) -> None:
    """Exclui o cliente. Não deixa excluir quem já tem agendamento."""
    buscar_cliente(cliente_id)
    try:
        cliente_repository.excluir_cliente(cliente_id)
    except IntegrityError:
        raise ValueError(
            "Não é possível excluir: o cliente possui agendamentos."
        ) from None
