class Cliente:
    def __init__(self, id, nome, telefone):
        self.id = id
        self.nome = nome
        self.telefone = telefone

    def validar_nome(self):

        if self.nome == "":
            raise ValueError("O nome do Cliente é obrigatório!")
        else:
            return True

    def validar_telefone(self):
        if self.telefone == "":
            return False
        else:
            return True
