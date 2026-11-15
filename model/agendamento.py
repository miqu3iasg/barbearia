class agendamento:
    def __init__(
        self,
        id,
        cliente_id,
        barbeiro_id,
        servico_id,
        data_agendamento,
        horario,
        pagamento,
        observacao,
        status,
    ):
        self.id = id
        self.cliente_id = cliente_id
        self.barbeiro_id = barbeiro_id
        self.servico_id = servico_id
        self.data_agendamento = data_agendamento
        self.horario = horario
        self.pagamento = pagamento
        self.observacao = observacao
        self.status = status

    def validar_agendamento(self):
        if self.cliente_id == "" or self.barbeiro_id == "" or self.servico_id == "":
            return False
        else:
            True

    def validar_pagamento(self):
        if self.status == "AGENDADO" or self.status == "ATENDIDO":
            return True
        else:
            return False
