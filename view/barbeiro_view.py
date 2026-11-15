from tkinter import messagebox, ttk
import customtkinter as ctk


class _MockBarbeiroController:

    def __init__(self):
        self._barbeiros = [
            {"id": 1, "nome": "Wild", "status": "Disponível"},
            {"id": 2, "nome": "Alexandre de Moraes", "status": "Disponível"},
            {"id": 3, "nome": "Ximbinha", "status": "Disponível"},
            {"id": 4, "nome": "Cleito Rasta", "status": "Disponível"},
        ]
        self._proximo_id = 5

    def listar_todos_os_barbeiros(self):
        return list(self._barbeiros)

    def criar_barbeiro(self, nome: str, status: str = "Disponível"):
        self._validar(nome, status)
        novo_id = self._proximo_id
        self._barbeiros.append(
            {"id": novo_id, "nome": nome.strip(), "status": status}
        )
        self._proximo_id += 1
        return novo_id

    def atualizar_barbeiro(self, barbeiro_id: int, nome: str, status: str):
        self._validar(nome, status)
        for barbeiro in self._barbeiros:
            if barbeiro["id"] == barbeiro_id:
                barbeiro["nome"] = nome.strip()
                barbeiro["status"] = status
                return True
        return False

    def atualizar_status_do_barbeiro(self, barbeiro_id: int, status: str):
        if status not in ("Disponível", "Ocupado"):
            raise ValueError("Status inválido. Use 'Disponível' ou 'Ocupado'.")
        for barbeiro in self._barbeiros:
            if barbeiro["id"] == barbeiro_id:
                barbeiro["status"] = status
                return True
        return False

    def excluir_barbeiro(self, barbeiro_id: int):
        for i, barbeiro in enumerate(self._barbeiros):
            if barbeiro["id"] == barbeiro_id:
                self._barbeiros.pop(i)
                return True
        return False

    @staticmethod
    def _validar(nome: str, status: str):
        if not nome.strip():
            raise ValueError("O nome do barbeiro é obrigatório.")
        if status not in ("Disponível", "Ocupado"):
            raise ValueError("Status inválido. Escolha 'Disponível' ou 'Ocupado'.")


class BarbeiroView(ctk.CTkFrame):

    def __init__(self, master, controller=None):
        super().__init__(master, fg_color="transparent")
        self.controller = (
            controller if controller is not None else _MockBarbeiroController()
        )
        self.barbeiro_selecionado_id: int | None = None
        self._todos_barbeiros: list = []

        self._construir_interface()
        self.carregar_barbeiros()

    def _construir_interface(self):
        form_frame = ctk.CTkFrame(self, corner_radius=8)
        form_frame.pack(fill="x", padx=10, pady=(10, 8))

        ctk.CTkLabel(
            form_frame,
            text="Cadastro e Disponibilidade de Barbeiros",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).grid(row=0, column=0, columnspan=4, sticky="w", padx=15, pady=(12, 8))

        ctk.CTkLabel(form_frame, text="Nome do barbeiro:").grid(
            row=1, column=0, sticky="w", padx=(15, 6), pady=6
        )
        self.entry_nome = ctk.CTkEntry(
            form_frame, placeholder_text="Ex.: Marcos Navalha", width=280
        )
        self.entry_nome.grid(row=1, column=1, sticky="we", padx=(0, 15), pady=6)

        ctk.CTkLabel(form_frame, text="Status:").grid(
            row=1, column=2, sticky="w", padx=(0, 6), pady=6
        )
        self.option_status = ctk.CTkOptionMenu(
            form_frame,
            values=["Disponível", "Ocupado"],
            width=180,
        )
        self.option_status.set("Disponível")
        self.option_status.grid(row=1, column=3, sticky="w", padx=(0, 15), pady=6)

        form_frame.grid_columnconfigure(1, weight=2)
        form_frame.grid_columnconfigure(3, weight=1)

        botoes_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        botoes_frame.grid(row=2, column=0, columnspan=4, sticky="w", padx=15, pady=(8, 14))

        ctk.CTkButton(
            botoes_frame, text="Cadastrar", width=115, command=self._cadastrar
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            botoes_frame,
            text="Atualizar",
            width=115,
            fg_color="#2e7d32",
            hover_color="#1b5e20",
            command=self._atualizar,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            botoes_frame,
            text="Alternar Status",
            width=130,
            fg_color="#ef6c00",
            hover_color="#e65100",
            command=self._alternar_status,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            botoes_frame,
            text="Excluir",
            width=115,
            fg_color="#c62828",
            hover_color="#8e0000",
            command=self._excluir,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            botoes_frame,
            text="Limpar Campos",
            width=120,
            fg_color="#455a64",
            hover_color="#263238",
            command=self._limpar_formulario,
        ).pack(side="left")

        lista_frame = ctk.CTkFrame(self, corner_radius=8)
        lista_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        topo_lista = ctk.CTkFrame(lista_frame, fg_color="transparent")
        topo_lista.pack(fill="x", padx=15, pady=(12, 8))

        ctk.CTkLabel(
            topo_lista,
            text="Barbeiros Cadastrados",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(side="left")

        self.entry_busca = ctk.CTkEntry(
            topo_lista,
            placeholder_text="Buscar por nome ou status...",
            width=260,
        )
        self.entry_busca.pack(side="right", padx=(8, 0))
        self.entry_busca.bind("<KeyRelease>", lambda _event: self._filtrar_tabela())

        ctk.CTkButton(
            topo_lista, text="Atualizar Lista", width=120, command=self.carregar_barbeiros
        ).pack(side="right")

        tabela_container = ctk.CTkFrame(lista_frame, fg_color="transparent")
        tabela_container.pack(fill="both", expand=True, padx=15, pady=(0, 14))

        colunas = ("id", "nome", "status")
        self.tabela = ttk.Treeview(
            tabela_container, columns=colunas, show="headings", selectmode="browse"
        )
        self.tabela.heading("id", text="ID")
        self.tabela.heading("nome", text="Nome")
        self.tabela.heading("status", text="Status")

        self.tabela.column("id", width=70, anchor="center")
        self.tabela.column("nome", width=440, anchor="w")
        self.tabela.column("status", width=200, anchor="center")

        scrollbar = ttk.Scrollbar(
            tabela_container, orient="vertical", command=self.tabela.yview
        )
        self.tabela.configure(yscrollcommand=scrollbar.set)

        self.tabela.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tabela.bind("<<TreeviewSelect>>", self._ao_selecionar_linha)

    @staticmethod
    def _extrair_campos(barbeiro) -> tuple:
        if isinstance(barbeiro, dict):
            return (
                barbeiro.get("id"),
                barbeiro.get("nome", ""),
                barbeiro.get("status", "Disponível"),
            )
        return (
            getattr(barbeiro, "id", ""),
            getattr(barbeiro, "nome", ""),
            getattr(barbeiro, "status", "Disponível"),
        )

    def carregar_barbeiros(self):
        try:
            self._todos_barbeiros = self.controller.listar_todos_os_barbeiros() or []
            self._filtrar_tabela()
        except Exception as erro:
            messagebox.showerror("Erro ao listar barbeiros", str(erro))

    def _filtrar_tabela(self):
        termo = self.entry_busca.get().strip().lower()
        for item in self.tabela.get_children():
            self.tabela.delete(item)

        for barbeiro in self._todos_barbeiros:
            bid, nome, status = self._extrair_campos(barbeiro)
            if not termo or termo in str(nome).lower() or termo in str(status).lower():
                self.tabela.insert("", "end", values=(bid, nome, status))

    def _ao_selecionar_linha(self, _event):
        selecao = self.tabela.selection()
        if not selecao:
            return
        valores = self.tabela.item(selecao[0], "values")
        self.barbeiro_selecionado_id = int(valores[0])

        self.entry_nome.delete(0, "end")
        self.entry_nome.insert(0, valores[1])

        self.option_status.set(valores[2])

    def _limpar_formulario(self):
        self.barbeiro_selecionado_id = None
        self.entry_nome.delete(0, "end")
        self.option_status.set("Disponível")
        for item in self.tabela.selection():
            self.tabela.selection_remove(item)

    def _cadastrar(self):
        nome = self.entry_nome.get().strip()
        status = self.option_status.get()
        try:
            self.controller.criar_barbeiro(nome, status)
            messagebox.showinfo("Sucesso", "Barbeiro cadastrado com sucesso!")
            self._limpar_formulario()
            self.carregar_barbeiros()
        except ValueError as erro:
            messagebox.showwarning("Atenção", str(erro))
        except Exception as erro:
            messagebox.showerror("Erro no banco de dados", str(erro))

    def _atualizar(self):
        if self.barbeiro_selecionado_id is None:
            messagebox.showwarning(
                "Atenção", "Selecione um barbeiro na tabela para alterar."
            )
            return

        nome = self.entry_nome.get().strip()
        status = self.option_status.get()
        try:
            self.controller.atualizar_barbeiro(
                self.barbeiro_selecionado_id, nome, status
            )
            messagebox.showinfo("Sucesso", "Dados do barbeiro atualizados!")
            self._limpar_formulario()
            self.carregar_barbeiros()
        except ValueError as erro:
            messagebox.showwarning("Atenção", str(erro))
        except Exception as erro:
            messagebox.showerror("Erro no banco de dados", str(erro))

    def _alternar_status(self):
        if self.barbeiro_selecionado_id is None:
            messagebox.showwarning(
                "Atenção", "Selecione um barbeiro na tabela para alternar o status."
            )
            return

        status_atual = self.option_status.get()
        novo_status = "Ocupado" if status_atual == "Disponível" else "Disponível"
        try:
            if hasattr(self.controller, "atualizar_status_do_barbeiro"):
                self.controller.atualizar_status_do_barbeiro(
                    self.barbeiro_selecionado_id, novo_status
                )
            else:
                self.controller.atualizar_barbeiro(
                    self.barbeiro_selecionado_id,
                    self.entry_nome.get().strip(),
                    novo_status,
                )
            messagebox.showinfo(
                "Sucesso", f"Status alterado para '{novo_status}'!"
            )
            self._limpar_formulario()
            self.carregar_barbeiros()
        except ValueError as erro:
            messagebox.showwarning("Atenção", str(erro))
        except Exception as erro:
            messagebox.showerror("Erro no banco de dados", str(erro))

    def _excluir(self):
        if self.barbeiro_selecionado_id is None:
            messagebox.showwarning(
                "Atenção", "Selecione um barbeiro na tabela para excluir."
            )
            return

        confirmar = messagebox.askyesno(
            "Confirmar exclusão",
            f"Deseja mesmo excluir o barbeiro '{self.entry_nome.get().strip()}'?",
        )
        if not confirmar:
            return

        try:
            self.controller.excluir_barbeiro(self.barbeiro_selecionado_id)
            messagebox.showinfo("Sucesso", "Barbeiro excluído com sucesso!")
            self._limpar_formulario()
            self.carregar_barbeiros()
        except ValueError as erro:
            messagebox.showwarning("Atenção", str(erro))
        except Exception as erro:
            messagebox.showerror("Erro no banco de dados", str(erro))