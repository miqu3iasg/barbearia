class barbeiro:
    def __init__(self, id, nome, status):
        self.id = id
        self.nome = nome
        self.status = status

    def verificar_nome(self):
        if self.nome == "":
            raise ValueError("O nome do Barbeiro é obrigatório!")
        else:
            return True

    def verificar_disponibilidade(self):
        if self.status == "Disponível":
            return True
        else:
            return False

