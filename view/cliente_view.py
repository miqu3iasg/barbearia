from tkinter import messagebox, ttk
import customtkinter as ctk


class _MockClienteController:
    """Simulador em memória usado apenas enquanto o Controller real não é conectado."""

    def __init__(self):
        self._clientes = [
            {"id": 1, "nome": "João Silva", "telefone": "11999998888"},
            {"id": 2, "nome": "Carlos Souza", "telefone": "11988887777"},
        ]
        self._proximo_id = 3

    def listar_todos_os_clientes(self):
        return list(self._clientes)

    def criar_cliente(self, nome: str, telefone: str):
        self._validar(nome, telefone)
        novo_id = self._proximo_id
        self._clientes.append(
            {"id": novo_id, "nome": nome.strip(), "telefone": telefone.strip()}
        )
        self._proximo_id += 1
        return novo_id

    def atualizar_cliente(self, cliente_id: int, nome: str, telefone: str):
        self._validar(nome, telefone)
        for cliente in self._clientes:
            if cliente["id"] == cliente_id:
                cliente["nome"] = nome.strip()
                cliente["telefone"] = telefone.strip()
                return True
        return False

    def excluir_cliente(self, cliente_id: int):
        for i, cliente in enumerate(self._clientes):
            if cliente["id"] == cliente_id:
                self._clientes.pop(i)
                return True
        return False

    @staticmethod
    def _validar(nome: str, telefone: str):
        if not nome.strip():
            raise ValueError("O nome do cliente é obrigatório.")
        tel = telefone.strip()
        if not tel.isdigit() or not (10 <= len(tel) <= 15):
            raise ValueError("O telefone deve conter apenas números (10 a 15 dígitos).")


class ClienteView(ctk.CTkFrame):
    """Tela de gerenciamento (CRUD) de clientes em CustomTkinter."""

    def __init__(self, master, controller=None):
        super().__init__(master, fg_color="transparent")
        self.controller = controller if controller is not None else _MockClienteController()
        self.cliente_selecionado_id: int | None = None
        self._todos_clientes: list = []

        self._construir_interface()
        self.carregar_clientes()

    def _construir_interface(self):
        # --- Bloco superior: Formulário ---
        form_frame = ctk.CTkFrame(self, corner_radius=8)
        form_frame.pack(fill="x", padx=10, pady=(10, 8))

        ctk.CTkLabel(
            form_frame,
            text="Cadastro e Edição de Clientes",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).grid(row=0, column=0, columnspan=4, sticky="w", padx=15, pady=(12, 8))

        ctk.CTkLabel(form_frame, text="Nome completo:").grid(
            row=1, column=0, sticky="w", padx=(15, 6), pady=6
        )
        self.entry_nome = ctk.CTkEntry(
            form_frame, placeholder_text="Ex.: Lucas Almeida", width=280
        )
        self.entry_nome.grid(row=1, column=1, sticky="we", padx=(0, 15), pady=6)

        ctk.CTkLabel(form_frame, text="Telefone (DDD + número):").grid(
            row=1, column=2, sticky="w", padx=(0, 6), pady=6
        )
        self.entry_telefone = ctk.CTkEntry(
            form_frame, placeholder_text="Ex.: 11987654321", width=200
        )
        self.entry_telefone.grid(row=1, column=3, sticky="we", padx=(0, 15), pady=6)

        form_frame.grid_columnconfigure(1, weight=2)
        form_frame.grid_columnconfigure(3, weight=1)

        # Botões de ação do CRUD
        botoes_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        botoes_frame.grid(row=2, column=0, columnspan=4, sticky="w", padx=15, pady=(8, 14))

        ctk.CTkButton(
            botoes_frame, text="Cadastrar", width=120, command=self._cadastrar
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            botoes_frame,
            text="Atualizar",
            width=120,
            fg_color="#2e7d32",
            hover_color="#1b5e20",
            command=self._atualizar,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            botoes_frame,
            text="Excluir",
            width=120,
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

        # --- Bloco inferior: Busca e Listagem ---
        lista_frame = ctk.CTkFrame(self, corner_radius=8)
        lista_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        topo_lista = ctk.CTkFrame(lista_frame, fg_color="transparent")
        topo_lista.pack(fill="x", padx=15, pady=(12, 8))

        ctk.CTkLabel(
            topo_lista,
            text="Clientes Cadastrados",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(side="left")

        self.entry_busca = ctk.CTkEntry(
            topo_lista,
            placeholder_text="Buscar por nome ou telefone...",
            width=260,
        )
        self.entry_busca.pack(side="right", padx=(8, 0))
        self.entry_busca.bind("<KeyRelease>", lambda _event: self._filtrar_tabela())

        ctk.CTkButton(
            topo_lista, text="Atualizar Lista", width=120, command=self.carregar_clientes
        ).pack(side="right")

        # Tabela (ttk.Treeview estilizada para o tema escuro)
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Treeview",
            background="#2b2b2b",
            foreground="#f5f5f5",
            fieldbackground="#2b2b2b",
            rowheight=28,
            borderwidth=0,
        )
        style.configure(
            "Treeview.Heading",
            background="#1f538d",
            foreground="white",
            font=("Sans", 10, "bold"),
        )
        style.map("Treeview", background=[("selected", "#144870")])

        tabela_container = ctk.CTkFrame(lista_frame, fg_color="transparent")
        tabela_container.pack(fill="both", expand=True, padx=15, pady=(0, 14))

        colunas = ("id", "nome", "telefone")
        self.tabela = ttk.Treeview(
            tabela_container, columns=colunas, show="headings", selectmode="browse"
        )
        self.tabela.heading("id", text="ID")
        self.tabela.heading("nome", text="Nome")
        self.tabela.heading("telefone", text="Telefone")

        self.tabela.column("id", width=70, anchor="center")
        self.tabela.column("nome", width=420, anchor="w")
        self.tabela.column("telefone", width=220, anchor="center")

        scrollbar = ttk.Scrollbar(
            tabela_container, orient="vertical", command=self.tabela.yview
        )
        self.tabela.configure(yscrollcommand=scrollbar.set)

        self.tabela.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tabela.bind("<<TreeviewSelect>>", self._ao_selecionar_linha)

    @staticmethod
    def _extrair_campos(cliente) -> tuple:
        """Lê tanto dicionários quanto objetos Model (Cliente)."""
        if isinstance(cliente, dict):
            return cliente.get("id"), cliente.get("nome", ""), cliente.get("telefone", "")
        return (
            getattr(cliente, "id", ""),
            getattr(cliente, "nome", ""),
            getattr(cliente, "telefone", ""),
        )

    def carregar_clientes(self):
        try:
            self._todos_clientes = self.controller.listar_todos_os_clientes() or []
            self._filtrar_tabela()
        except Exception as erro:
            messagebox.showerror("Erro ao listar clientes", str(erro))

    def _filtrar_tabela(self):
        termo = self.entry_busca.get().strip().lower()
        for item in self.tabela.get_children():
            self.tabela.delete(item)

        for cliente in self._todos_clientes:
            cid, nome, telefone = self._extrair_campos(cliente)
            if not termo or termo in str(nome).lower() or termo in str(telefone).lower():
                self.tabela.insert("", "end", values=(cid, nome, telefone))

    def _ao_selecionar_linha(self, _event):
        selecao = self.tabela.selection()
        if not selecao:
            return
        valores = self.tabela.item(selecao[0], "values")
        self.cliente_selecionado_id = int(valores[0])

        self.entry_nome.delete(0, "end")
        self.entry_nome.insert(0, valores[1])

        self.entry_telefone.delete(0, "end")
        self.entry_telefone.insert(0, valores[2])

    def _limpar_formulario(self):
        self.cliente_selecionado_id = None
        self.entry_nome.delete(0, "end")
        self.entry_telefone.delete(0, "end")
        for item in self.tabela.selection():
            self.tabela.selection_remove(item)

    def _cadastrar(self):
        nome = self.entry_nome.get().strip()
        telefone = self.entry_telefone.get().strip()
        try:
            self.controller.criar_cliente(nome, telefone)
            messagebox.showinfo("Sucesso", "Cliente cadastrado com sucesso!")
            self._limpar_formulario()
            self.carregar_clientes()
        except ValueError as erro:
            messagebox.showwarning("Atenção", str(erro))
        except Exception as erro:
            messagebox.showerror("Erro no banco de dados", str(erro))

    def _atualizar(self):
        if self.cliente_selecionado_id is None:
            messagebox.showwarning("Atenção", "Selecione um cliente na tabela para alterar.")
            return

        nome = self.entry_nome.get().strip()
        telefone = self.entry_telefone.get().strip()
        try:
            self.controller.atualizar_cliente(self.cliente_selecionado_id, nome, telefone)
            messagebox.showinfo("Sucesso", "Dados do cliente atualizados!")
            self._limpar_formulario()
            self.carregar_clientes()
        except ValueError as erro:
            messagebox.showwarning("Atenção", str(erro))
        except Exception as erro:
            messagebox.showerror("Erro no banco de dados", str(erro))

    def _excluir(self):
        if self.cliente_selecionado_id is None:
            messagebox.showwarning("Atenção", "Selecione um cliente na tabela para excluir.")
            return

        confirmar = messagebox.askyesno(
            "Confirmar exclusão",
            f"Deseja mesmo excluir o cliente '{self.entry_nome.get().strip()}'?",
        )
        if not confirmar:
            return

        try:
            self.controller.excluir_cliente(self.cliente_selecionado_id)
            messagebox.showinfo("Sucesso", "Cliente excluído com sucesso!")
            self._limpar_formulario()
            self.carregar_clientes()
        except ValueError as erro:
            messagebox.showwarning("Atenção", str(erro))
        except Exception as erro:
            messagebox.showerror("Erro no banco de dados", str(erro))