from tkinter import messagebox, ttk
import customtkinter as ctk


class _MockServicoController:

    def __init__(self):
        self._servicos = [
            {"id": 1, "nome": "Degradê", "preco": 35.00},
            {"id": 2, "nome": "Social", "preco": 30.00},
            {"id": 3, "nome": "Corte na Tesoura", "preco": 40.00},
            {"id": 4, "nome": "Sobrancelha", "preco": 15.00},
            {"id": 5, "nome": "Barba", "preco": 25.00},
            {"id": 10, "nome": "Corte + Barba", "preco": 55.00},
        ]
        self._proximo_id = 13

    def listar_todos_os_servicos(self):
        return list(self._servicos)

    def criar_servico(self, nome: str, preco: float):
        self._validar(nome, preco)
        novo_id = self._proximo_id
        self._servicos.append(
            {"id": novo_id, "nome": nome.strip(), "preco": float(preco)}
        )
        self._proximo_id += 1
        return novo_id

    def atualizar_servico(self, servico_id: int, nome: str, preco: float):
        self._validar(nome, preco)
        for servico in self._servicos:
            if servico["id"] == servico_id:
                servico["nome"] = nome.strip()
                servico["preco"] = float(preco)
                return True
        return False

    def excluir_servico(self, servico_id: int):
        for i, servico in enumerate(self._servicos):
            if servico["id"] == servico_id:
                self._servicos.pop(i)
                return True
        return False

    @staticmethod
    def _validar(nome: str, preco: float):
        nome_limpo = nome.strip()
        if not nome_limpo:
            raise ValueError("O nome do serviço é obrigatório.")
        if len(nome_limpo) > 50:
            raise ValueError("O nome do serviço deve ter no máximo 50 caracteres.")
        if preco <= 0:
            raise ValueError("O preço do serviço deve ser maior que zero.")


class ServicoView(ctk.CTkFrame):

    def __init__(self, master, controller=None):
        super().__init__(master, fg_color="transparent")
        self.controller = (
            controller if controller is not None else _MockServicoController()
        )
        self.servico_selecionado_id: int | None = None
        self._todos_servicos: list = []

        self._construir_interface()
        self.carregar_servicos()

    def _construir_interface(self):
        form_frame = ctk.CTkFrame(self, corner_radius=8)
        form_frame.pack(fill="x", padx=4, pady=(4, 6))

        ctk.CTkLabel(
            form_frame,
            text="Cadastro de Serviços",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", padx=12, pady=(10, 6))

        ctk.CTkLabel(form_frame, text="Nome do serviço:").pack(anchor="w", padx=12)
        self.entry_nome = ctk.CTkEntry(
            form_frame, placeholder_text="Ex.: Corte + Barba"
        )
        self.entry_nome.pack(fill="x", padx=12, pady=(2, 6))

        ctk.CTkLabel(form_frame, text="Preço (R$):").pack(anchor="w", padx=12)
        self.entry_preco = ctk.CTkEntry(
            form_frame, placeholder_text="Ex.: 45.00"
        )
        self.entry_preco.pack(fill="x", padx=12, pady=(2, 8))

        botoes_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        botoes_frame.pack(fill="x", padx=12, pady=(0, 10))
        botoes_frame.grid_columnconfigure(0, weight=1)
        botoes_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            botoes_frame, text="Cadastrar", command=self._cadastrar
        ).grid(row=0, column=0, sticky="we", padx=(0, 4), pady=(0, 6))

        ctk.CTkButton(
            botoes_frame,
            text="Atualizar",
            fg_color="#2e7d32",
            hover_color="#1b5e20",
            command=self._atualizar,
        ).grid(row=0, column=1, sticky="we", padx=(4, 0), pady=(0, 6))

        ctk.CTkButton(
            botoes_frame,
            text="Excluir",
            fg_color="#c62828",
            hover_color="#8e0000",
            command=self._excluir,
        ).grid(row=1, column=0, sticky="we", padx=(0, 4))

        ctk.CTkButton(
            botoes_frame,
            text="Limpar",
            fg_color="#455a64",
            hover_color="#263238",
            command=self._limpar_formulario,
        ).grid(row=1, column=1, sticky="we", padx=(4, 0))

        lista_frame = ctk.CTkFrame(self, corner_radius=8)
        lista_frame.pack(fill="both", expand=True, padx=4, pady=(0, 4))

        topo_lista = ctk.CTkFrame(lista_frame, fg_color="transparent")
        topo_lista.pack(fill="x", padx=12, pady=(10, 6))

        ctk.CTkLabel(
            topo_lista,
            text="Serviços Cadastrados",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(side="left")

        ctk.CTkButton(
            topo_lista, text="Atualizar", width=85, height=28, command=self.carregar_servicos
        ).pack(side="right")

        self.entry_busca = ctk.CTkEntry(
            lista_frame,
            placeholder_text="Buscar por serviço ou preço...",
        )
        self.entry_busca.pack(fill="x", padx=12, pady=(0, 8))
        self.entry_busca.bind("<KeyRelease>", lambda _event: self._filtrar_tabela())

        tabela_container = ctk.CTkFrame(lista_frame, fg_color="transparent")
        tabela_container.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        colunas = ("id", "nome", "preco")
        self.tabela = ttk.Treeview(
            tabela_container, columns=colunas, show="headings", selectmode="browse"
        )
        self.tabela.heading("id", text="ID")
        self.tabela.heading("nome", text="Serviço")
        self.tabela.heading("preco", text="Preço")

        self.tabela.column("id", width=38, anchor="center")
        self.tabela.column("nome", width=205, anchor="w")
        self.tabela.column("preco", width=95, anchor="center")

        scrollbar = ttk.Scrollbar(
            tabela_container, orient="vertical", command=self.tabela.yview
        )
        self.tabela.configure(yscrollcommand=scrollbar.set)

        self.tabela.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tabela.bind("<<TreeviewSelect>>", self._ao_selecionar_linha)

    @staticmethod
    def _extrair_campos(servico) -> tuple:
        if isinstance(servico, dict):
            return (
                servico.get("id"),
                servico.get("nome", ""),
                float(servico.get("preco", 0)),
            )
        return (
            getattr(servico, "id", ""),
            getattr(servico, "nome", ""),
            float(getattr(servico, "preco", 0)),
        )

    @staticmethod
    def _converter_preco(texto: str) -> float:
        valor_limpo = texto.strip().replace("R$", "").replace(",", ".").strip()
        if not valor_limpo:
            raise ValueError("Informe o preço do serviço.")
        try:
            preco = float(valor_limpo)
        except ValueError as erro:
            raise ValueError("Digite um valor numérico válido para o preço.") from erro
        if preco <= 0:
            raise ValueError("O preço do serviço deve ser maior que zero.")
        return round(preco, 2)

    def carregar_servicos(self):
        try:
            self._todos_servicos = self.controller.listar_todos_os_servicos() or []
            self._filtrar_tabela()
        except Exception as erro:
            messagebox.showerror("Erro ao listar serviços", str(erro))

    def _filtrar_tabela(self):
        termo = self.entry_busca.get().strip().lower()
        for item in self.tabela.get_children():
            self.tabela.delete(item)

        for servico in self._todos_servicos:
            sid, nome, preco = self._extrair_campos(servico)
            preco_formatado = f"R$ {preco:.2f}"
            if (
                not termo
                or termo in str(nome).lower()
                or termo in preco_formatado.lower()
            ):
                self.tabela.insert("", "end", values=(sid, nome, preco_formatado))

    def _ao_selecionar_linha(self, _event):
        selecao = self.tabela.selection()
        if not selecao:
            return
        valores = self.tabela.item(selecao[0], "values")
        self.servico_selecionado_id = int(valores[0])

        self.entry_nome.delete(0, "end")
        self.entry_nome.insert(0, valores[1])

        preco_limpo = str(valores[2]).replace("R$", "").strip()
        self.entry_preco.delete(0, "end")
        self.entry_preco.insert(0, preco_limpo)

    def _limpar_formulario(self):
        self.servico_selecionado_id = None
        self.entry_nome.delete(0, "end")
        self.entry_preco.delete(0, "end")
        for item in self.tabela.selection():
            self.tabela.selection_remove(item)

    def _cadastrar(self):
        nome = self.entry_nome.get().strip()
        try:
            preco = self._converter_preco(self.entry_preco.get())
            self.controller.criar_servico(nome, preco)
            messagebox.showinfo("Sucesso", "Serviço cadastrado com sucesso!")
            self._limpar_formulario()
            self.carregar_servicos()
        except ValueError as erro:
            messagebox.showwarning("Atenção", str(erro))
        except Exception as erro:
            messagebox.showerror("Erro no banco de dados", str(erro))

    def _atualizar(self):
        if self.servico_selecionado_id is None:
            messagebox.showwarning(
                "Atenção", "Selecione um serviço na tabela para alterar."
            )
            return

        nome = self.entry_nome.get().strip()
        try:
            preco = self._converter_preco(self.entry_preco.get())
            self.controller.atualizar_servico(self.servico_selecionado_id, nome, preco)
            messagebox.showinfo("Sucesso", "Serviço atualizado com sucesso!")
            self._limpar_formulario()
            self.carregar_servicos()
        except ValueError as erro:
            messagebox.showwarning("Atenção", str(erro))
        except Exception as erro:
            messagebox.showerror("Erro no banco de dados", str(erro))

    def _excluir(self):
        if self.servico_selecionado_id is None:
            messagebox.showwarning(
                "Atenção", "Selecione um serviço na tabela para excluir."
            )
            return

        confirmar = messagebox.askyesno(
            "Confirmar exclusão",
            f"Deseja mesmo excluir o serviço '{self.entry_nome.get().strip()}'?",
        )
        if not confirmar:
            return

        try:
            self.controller.excluir_servico(self.servico_selecionado_id)
            messagebox.showinfo("Sucesso", "Serviço excluído com sucesso!")
            self._limpar_formulario()
            self.carregar_servicos()
        except ValueError as erro:
            messagebox.showwarning("Atenção", str(erro))
        except Exception as erro:
            messagebox.showerror("Erro no banco de dados", str(erro))