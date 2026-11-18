class servico:
    def __init__(self, id, nome, preco):
        self.id = id
        self.nome = nome
        self.preco = preco

    def validar_nome(self):
        return self.nome != ""

    def validar_preco(self):
        return self.preco > 0
