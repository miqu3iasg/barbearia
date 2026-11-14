import os
import time
from collections import deque
from datetime import date

LARGURA = 58

# --------------------- dados iniciais ---------------------

servicos = [
    "Degradê",
    "Social",
    "Corte na Tesoura",
    "Sobrancelha",
    "Barba",
    "Pigmentação",
    "Nevou",
    "Reflexo",
    "Alisamento",
    "Corte + Barba",
    "Corte + Sobrancelha",
    "Corte + Barba + Sobrancelha",
]

horarios = [
    "8:00",
    "9:00",
    "10:00",
    "11:00",
    "14:00",
    "15:00",
    "16:00",
    "17:00",
    "18:00",
]

barbeiros = [
    {"id": 1, "nome": "Wild", "status": "Disponível"},
    {"id": 2, "nome": "Alexandre de Moraes", "status": "Disponível"},
    {"id": 3, "nome": "Ximbinha", "status": "Disponível"},
    {"id": 5, "nome": "Cleito Rasta", "status": "Disponível"},
]

clientes = {}
agendamentos = {}

agenda_barbeiros = {}
fila_agendamentos = deque()

proximo_id_cliente = 1
proximo_id_agendamento = 1


# --------------- funções de suporte (utilitários) ---------------

# telas


def limpar_tela():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def cabecalho(titulo):
    limpar_tela()
    print("=" * LARGURA)
    print(titulo.center(LARGURA))
    print("=" * LARGURA)


def rodape():
    print("-" * LARGURA)


def pausar():
    input("\nPressione ENTER para continuar...")


def tela_boas_vindas():
    limpar_tela()
    print("=" * LARGURA)
    print("SISTEMA BARBEARIA".center(LARGURA))
    print("=" * LARGURA)

    frases = [
        "Iniciando o sistema...",
        "Carregando clientes e barbeiros...",
        "Preparando a agenda do dia...",
    ]
    for frase in frases:
        print(frase)
        time.sleep(0.35)

    print("\nTudo pronto!")
    time.sleep(0.5)


# mensagens


def sucesso(msg):
    print(f"\n[OK] {msg}")


def erro(msg):
    print(f"\n[ERRO] {msg}")


def info(msg):
    print(f"\n[INFO] {msg}")


# validações e buscas


def ler_id(mensagem):
    valor = input(mensagem).strip()

    if valor.isdigit():
        return int(valor)
    else:
        erro("Digite apenas números para o ID.")
        return None


def eh_data_valida(texto):
    partes = texto.split("/")

    if len(partes) != 3:
        return False

    dia_texto, mes_texto, ano_texto = partes[0], partes[1], partes[2]

    if not dia_texto.isdigit() or not mes_texto.isdigit() or not ano_texto.isdigit():
        return False

    dia = int(dia_texto)
    mes = int(mes_texto)
    ano = int(ano_texto)

    if dia < 1 or dia > 31:
        return False

    if mes < 1 or mes > 12:
        return False

    if ano < 2000 or ano > 2100:
        return False

    return True


def eh_data_passada(texto):
    partes = texto.split("/")
    dia = int(partes[0])
    mes = int(partes[1])
    ano = int(partes[2])

    hoje = date.today()
    data_informada = (ano, mes, dia)
    data_hoje = (hoje.year, hoje.month, hoje.day)

    return data_informada < data_hoje


def escolher_da_lista(itens, pergunta):
    numero = 1
    for item in itens:
        print(f"{numero} - {item}")
        numero += 1

    escolha = input(pergunta)

    if not escolha.isdigit():
        return None

    indice = int(escolha)

    if indice < 1 or indice > len(itens):
        return None

    return itens[indice - 1]


def buscar_barbeiro(id_barbeiro):
    for b in barbeiros:
        if b["id"] == id_barbeiro:
            return b
    return None


def escolher_barbeiro(lista_barbeiros, pergunta):
    if len(lista_barbeiros) == 0:
        return None

    for b in lista_barbeiros:
        print(f"{b['id']} - {b['nome']}")

    id_escolhido = ler_id(pergunta)

    if id_escolhido is None:
        return None

    for b in lista_barbeiros:
        if b["id"] == id_escolhido:
            return b

    return None


# ------------------------- barbeiros -------------------------


def atualizar_status_barbeiro():
    cabecalho("Atualizar Status do Barbeiro")

    for b in barbeiros:
        print(f"{b['id']} - {b['nome']} | Status: {b['status']}")

    id_busca = ler_id("\nDigite o ID do barbeiro: ")
    if id_busca is None:
        pausar()
        return

    barbeiro = buscar_barbeiro(id_busca)
    if barbeiro is None:
        erro("Barbeiro não encontrado.")
        pausar()
        return

    print("Novo status:")
    print("1 - Disponível")
    print("2 - Ocupado")
    opcao = input("Escolha uma opção: ")

    if opcao == "1":
        barbeiro["status"] = "Disponível"
        sucesso("Status atualizado para Disponível.")
    elif opcao == "2":
        barbeiro["status"] = "Ocupado"
        sucesso("Status atualizado para Ocupado.")
    else:
        erro("Opção inválida.")
    pausar()


def listar_barbeiros():
    cabecalho("Lista de Barbeiros")

    for b in barbeiros:
        print(f"ID: {b['id']} | Nome: {b['nome']} | Status: {b['status']}")

    rodape()
    pausar()


def menu_barbeiros():
    while True:
        cabecalho("Área de Barbeiros")
        print("1 - Atualizar status do barbeiro")
        print("2 - Listar barbeiros")
        print("0 - Voltar")
        rodape()
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            atualizar_status_barbeiro()
        elif opcao == "2":
            listar_barbeiros()
        elif opcao == "0":
            break
        else:
            erro("Opção inválida.")
            pausar()


# ------------------------- clientes -------------------------


def cadastrar_cliente():
    global proximo_id_cliente
    cabecalho("Cadastrar Cliente")

    nome = input("Nome do cliente: ")
    telefone = input("Telefone do cliente: ")
    clientes[proximo_id_cliente] = {"nome": nome, "telefone": telefone}

    sucesso(f"Cliente cadastrado com sucesso! ID: {proximo_id_cliente}")
    id_cadastrado = proximo_id_cliente
    proximo_id_cliente += 1
    pausar()
    return id_cadastrado


def listar_clientes():
    cabecalho("Lista de Clientes")

    if len(clientes) == 0:
        info("Nenhum cliente cadastrado.")
        pausar()
        return

    for id_cliente, c in clientes.items():
        print(f"ID: {id_cliente} | Nome: {c['nome']} | Telefone: {c['telefone']}")

    rodape()
    pausar()


def menu_clientes():
    while True:
        cabecalho("Área de Clientes")
        print("1 - Cadastrar cliente")
        print("2 - Listar clientes")
        print("0 - Voltar")
        rodape()
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            cadastrar_cliente()
        elif opcao == "2":
            listar_clientes()
        elif opcao == "0":
            break
        else:
            erro("Opção inválida.")
            pausar()


# ------------------------ agendamentos ------------------------


def mostrar_fila_agendamentos():
    if len(fila_agendamentos) == 0:
        info("Nenhum agendamento na fila ainda. O seu será o 1º.")
        return

    print("\nFila de agendamentos do dia:")
    for posicao, ag in enumerate(fila_agendamentos, start=1):
        print(f"{posicao}º - {ag['nome']} | {ag['servico']} às {ag['horario']}")

    print(f"\nO novo agendamento será o {len(fila_agendamentos) + 1}º da fila.")


def agendamento_corte():
    global proximo_id_agendamento
    cabecalho("Novo Agendamento")

    mostrar_fila_agendamentos()

    print("\nClientes cadastrados:")
    if len(clientes) == 0:
        info("Nenhum cliente cadastrado ainda.")
    else:
        for id_cliente, c in clientes.items():
            print(f"{id_cliente} - {c['nome']}")

    id_cliente_escolhido = ler_id("\nDigite o ID do cliente: ")

    if id_cliente_escolhido is None:
        erro("ID inválido. Agendamento cancelado.")
        pausar()
        return

    cliente_escolhido = clientes.get(id_cliente_escolhido)

    if cliente_escolhido is None:
        resposta = (
            input("Cliente não encontrado. Deseja cadastrar um novo cliente? (S/N): ")
            .strip()
            .upper()
        )

        if resposta == "S":
            id_cliente_escolhido = cadastrar_cliente()
            cliente_escolhido = clientes[id_cliente_escolhido]
            cabecalho("Novo Agendamento")
        else:
            info("Agendamento encerrado.")
            pausar()
            return

    nome_cliente = cliente_escolhido["nome"]

    data = input(
        "\nDigite a data do corte (formato DD/MM/AAAA) ou deixe em branco para hoje: "
    ).strip()

    if data == "":
        hoje = date.today()
        data = f"{hoje.day:02d}/{hoje.month:02d}/{hoje.year}"

    if not eh_data_valida(data):
        erro("Data inválida. Use o formato DD/MM/AAAA. Agendamento cancelado.")
        pausar()
        return

    if eh_data_passada(data):
        erro("Não é possível agendar em uma data que já passou. Agendamento cancelado.")
        pausar()
        return

    barbeiros_disponiveis = []
    for b in barbeiros:
        if b["status"] == "Disponível":
            barbeiros_disponiveis.append(b)

    if len(barbeiros_disponiveis) == 0:
        info("Nenhum barbeiro disponível no momento.")
        pausar()
        return

    print("\nBarbeiros disponíveis:")
    barbeiro_escolhido = escolher_barbeiro(
        barbeiros_disponiveis, "Escolha o barbeiro pelo ID: "
    )

    if barbeiro_escolhido is None:
        erro("Barbeiro inválido. Agendamento cancelado.")
        pausar()
        return

    if barbeiro_escolhido["id"] in agenda_barbeiros:
        if data in agenda_barbeiros[barbeiro_escolhido["id"]]:
            horarios_ocupados = agenda_barbeiros[barbeiro_escolhido["id"]][data]
        else:
            horarios_ocupados = []
    else:
        horarios_ocupados = []

    horarios_livres = []
    for horario in horarios:
        if horario not in horarios_ocupados:
            horarios_livres.append(horario)

    print(f"\nHorários de {barbeiro_escolhido['nome']} para o dia {data}:")

    if len(horarios_ocupados) == 0:
        print("Ocupados: nenhum")
    else:
        print("Ocupados:", ", ".join(horarios_ocupados))

    if len(horarios_livres) == 0:
        info("Esse barbeiro não tem mais horários disponíveis nesse dia.")
        pausar()
        return

    print("Disponíveis:", ", ".join(horarios_livres))

    horario_escolhido = escolher_da_lista(
        horarios_livres, "\nEscolha o horário (número): "
    )

    if horario_escolhido is None:
        erro("Horário inválido. Agendamento cancelado.")
        pausar()
        return

    observacao = input("Alguma observação? ")

    print("\nServiços disponíveis:")
    servico = escolher_da_lista(servicos, "Escolha o serviço (número): ")

    if servico is None:
        erro("Serviço inválido. Agendamento cancelado.")
        pausar()
        return

    print("1 - Pagamento será efetuado após o corte?")
    print("2 - Pagamento será adiantado online?")

    pagamento = input("Escolha uma opção: ")

    if pagamento == "1":
        print("Pagamento será efetuado após o corte!")
    else:
        print("Chave pix disponível abaixo!")
        print("Chave pix: 10311469540")

    agendamentos[proximo_id_agendamento] = {
        "cliente": nome_cliente,
        "cliente_id": id_cliente_escolhido,
        "data": data,
        "barbeiro": barbeiro_escolhido["nome"],
        "horario": horario_escolhido,
        "servico": servico,
        "pagamento": pagamento,
        "observacao": observacao,
    }

    if barbeiro_escolhido["id"] not in agenda_barbeiros:
        agenda_barbeiros[barbeiro_escolhido["id"]] = {}

    if data not in agenda_barbeiros[barbeiro_escolhido["id"]]:
        agenda_barbeiros[barbeiro_escolhido["id"]][data] = []

    agenda_barbeiros[barbeiro_escolhido["id"]][data].append(horario_escolhido)

    fila_agendamentos.append(
        {"nome": nome_cliente, "servico": servico, "horario": horario_escolhido}
    )

    sucesso(
        f"Seu corte foi agendado com sucesso! ID do agendamento: {proximo_id_agendamento}"
    )
    proximo_id_agendamento += 1
    pausar()


def listar_agendamentos():
    cabecalho("Agendamentos Marcados")

    if len(agendamentos) == 0:
        info("Nenhum agendamento cadastrado.")
        pausar()
        return

    for id_agendamento, ag in agendamentos.items():
        print(
            f"ID: {id_agendamento} | Cliente: {ag['cliente']} | Data: {ag['data']} | "
            f"Barbeiro: {ag['barbeiro']} | Horário: {ag['horario']} | Serviço: {ag['servico']}"
        )

    rodape()
    pausar()


def atender_proximo_cliente():
    cabecalho("Atender Próximo Cliente")

    if len(fila_agendamentos) == 0:
        info("Não há ninguém na fila no momento.")
        pausar()
        return

    print("Fila de agendamentos do dia:")
    for posicao, ag in enumerate(fila_agendamentos, start=1):
        print(f"{posicao}º - {ag['nome']} | {ag['servico']} às {ag['horario']}")

    print()
    atendido = fila_agendamentos.popleft()

    sucesso(
        f"Atendendo {atendido['nome']} | Serviço: {atendido['servico']} | "
        f"Horário: {atendido['horario']}"
    )
    pausar()


def menu_agendamentos():
    while True:
        cabecalho("Área de Agendamentos")
        print("1 - Novo agendamento")
        print("2 - Listar agendamentos")
        print("3 - Atender próximo cliente da fila")
        print("0 - Voltar")
        rodape()
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            agendamento_corte()
        elif opcao == "2":
            listar_agendamentos()
        elif opcao == "3":
            atender_proximo_cliente()
        elif opcao == "0":
            break
        else:
            erro("Opção inválida.")
            pausar()


# --------------------- programa principal ---------------------


def menu_principal():
    tela_boas_vindas()

    while True:
        cabecalho("Sistema Barbearia")
        print("1 - Clientes")
        print("2 - Barbeiros")
        print("3 - Agendamentos")
        print("0 - Sair")
        rodape()
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            menu_clientes()
        elif opcao == "2":
            menu_barbeiros()
        elif opcao == "3":
            menu_agendamentos()
        elif opcao == "0":
            cabecalho("Até logo!")
            print("Encerrando o sistema...")
            break
        else:
            erro("Opção inválida.")
            pausar()


if __name__ == "__main__":
    menu_principal()
