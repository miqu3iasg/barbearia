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
        if (
            self.cliente_id in (None, "")
            or self.barbeiro_id in (None, "")
            or self.servico_id in (None, "")
        ):
            return False
        return True

    def validar_pagamento(self):
        return self.pagamento in ("APOS_CORTE", "PIX_ONLINE")
