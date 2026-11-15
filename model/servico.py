class servico:
    def __init__(self, id, nome, preco):
        self.id = id
        self.nome = nome
        self.preco = preco

    def validar_nome(self):
        if self.id == "":
            return False
        else:
            return True

    def validar_preco(self):
        if self.preco > 0:
            return True
        else:
            return False

