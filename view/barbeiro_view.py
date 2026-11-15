from tkinter import messagebox, ttk
import customtkinter as ctk


def _chamar(ctrl, funcao: str, *args):
    if isinstance(ctrl, dict):
        return ctrl[funcao](*args)
    return getattr(ctrl, funcao)(*args)


def _tem_funcao(ctrl, funcao: str) -> bool:
    if isinstance(ctrl, dict):
        return funcao in ctrl
    return hasattr(ctrl, funcao)


def _criar_mock_barbeiro():
    dados = {
        "lista": [
            {"id": 1, "nome": "Wild", "status": "Disponível"},
            {"id": 2, "nome": "Alexandre de Moraes", "status": "Disponível"},
            {"id": 3, "nome": "Ximbinha", "status": "Disponível"},
            {"id": 4, "nome": "Cleito Rasta", "status": "Disponível"},
        ],
        "proximo_id": 5,
    }

    def validar(nome: str, status: str):
        if not nome.strip():
            raise ValueError("O nome do barbeiro é obrigatório.")
        if status not in ("Disponível", "Ocupado"):
            raise ValueError("Status inválido. Escolha 'Disponível' ou 'Ocupado'.")

    def listar_todos_os_barbeiros():
        return list(dados["lista"])

    def criar_barbeiro(nome: str, status: str = "Disponível"):
        validar(nome, status)
        novo_id = dados["proximo_id"]
        dados["lista"].append({"id": novo_id, "nome": nome.strip(), "status": status})
        dados["proximo_id"] += 1
        return novo_id

    def atualizar_barbeiro(barbeiro_id: int, nome: str, status: str):
        validar(nome, status)
        for barbeiro in dados["lista"]:
            if barbeiro["id"] == barbeiro_id:
                barbeiro["nome"] = nome.strip()
                barbeiro["status"] = status
                return True
        return False

    def atualizar_status_do_barbeiro(barbeiro_id: int, status: str):
        if status not in ("Disponível", "Ocupado"):
            raise ValueError("Status inválido. Use 'Disponível' ou 'Ocupado'.")
        for barbeiro in dados["lista"]:
            if barbeiro["id"] == barbeiro_id:
                barbeiro["status"] = status
                return True
        return False

    def excluir_barbeiro(barbeiro_id: int):
        for i, barbeiro in enumerate(dados["lista"]):
            if barbeiro["id"] == barbeiro_id:
                dados["lista"].pop(i)
                return True
        return False

    return {
        "listar_todos_os_barbeiros": listar_todos_os_barbeiros,
        "criar_barbeiro": criar_barbeiro,
        "atualizar_barbeiro": atualizar_barbeiro,
        "atualizar_status_do_barbeiro": atualizar_status_do_barbeiro,
        "excluir_barbeiro": excluir_barbeiro,
    }


def criar_tela_barbeiros(master, controller=None):
    ctrl = controller if controller is not None else _criar_mock_barbeiro()
    estado = {"selecionado_id": None, "todos": []}

    frame = ctk.CTkFrame(master, fg_color="transparent")

    form_frame = ctk.CTkFrame(frame, corner_radius=8)
    form_frame.pack(fill="x", padx=4, pady=(4, 6))

    ctk.CTkLabel(
        form_frame,
        text="Cadastro de Barbeiros",
        font=ctk.CTkFont(size=14, weight="bold"),
    ).pack(anchor="w", padx=12, pady=(10, 6))

    ctk.CTkLabel(form_frame, text="Nome do barbeiro:").pack(anchor="w", padx=12)
    entry_nome = ctk.CTkEntry(form_frame, placeholder_text="Ex.: Marcos Navalha")
    entry_nome.pack(fill="x", padx=12, pady=(2, 6))

    ctk.CTkLabel(form_frame, text="Status:").pack(anchor="w", padx=12)
    option_status = ctk.CTkOptionMenu(
        form_frame,
        values=["Disponível", "Ocupado"],
    )
    option_status.set("Disponível")
    option_status.pack(fill="x", padx=12, pady=(2, 8))

    botoes_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
    botoes_frame.pack(fill="x", padx=12, pady=(0, 10))
    botoes_frame.grid_columnconfigure(0, weight=1)
    botoes_frame.grid_columnconfigure(1, weight=1)

    lista_frame = ctk.CTkFrame(frame, corner_radius=8)
    lista_frame.pack(fill="both", expand=True, padx=4, pady=(0, 4))

    topo_lista = ctk.CTkFrame(lista_frame, fg_color="transparent")
    topo_lista.pack(fill="x", padx=12, pady=(10, 6))

    ctk.CTkLabel(
        topo_lista,
        text="Barbeiros Cadastrados",
        font=ctk.CTkFont(size=14, weight="bold"),
    ).pack(side="left")

    entry_busca = ctk.CTkEntry(
        lista_frame,
        placeholder_text="Buscar por nome ou status...",
    )
    entry_busca.pack(fill="x", padx=12, pady=(0, 8))

    tabela_container = ctk.CTkFrame(lista_frame, fg_color="transparent")
    tabela_container.pack(fill="both", expand=True, padx=12, pady=(0, 10))

    colunas = ("id", "nome", "status")
    tabela = ttk.Treeview(
        tabela_container, columns=colunas, show="headings", selectmode="browse"
    )
    tabela.heading("id", text="ID")
    tabela.heading("nome", text="Nome")
    tabela.heading("status", text="Status")

    tabela.column("id", width=38, anchor="center")
    tabela.column("nome", width=195, anchor="w")
    tabela.column("status", width=105, anchor="center")

    scrollbar = ttk.Scrollbar(
        tabela_container, orient="vertical", command=tabela.yview
    )
    tabela.configure(yscrollcommand=scrollbar.set)

    tabela.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def extrair_campos(barbeiro):
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

    def filtrar_tabela(_event=None):
        termo = entry_busca.get().strip().lower()
        for item in tabela.get_children():
            tabela.delete(item)

        for barbeiro in estado["todos"]:
            bid, nome, status = extrair_campos(barbeiro)
            if not termo or termo in str(nome).lower() or termo in str(status).lower():
                tabela.insert("", "end", values=(bid, nome, status))

    def carregar_barbeiros():
        try:
            estado["todos"] = _chamar(ctrl, "listar_todos_os_barbeiros") or []
            filtrar_tabela()
        except Exception as erro:
            messagebox.showerror("Erro ao listar barbeiros", str(erro))

    def ao_selecionar_linha(_event):
        selecao = tabela.selection()
        if not selecao:
            return
        valores = tabela.item(selecao[0], "values")
        estado["selecionado_id"] = int(valores[0])

        entry_nome.delete(0, "end")
        entry_nome.insert(0, valores[1])

        option_status.set(valores[2])

    def limpar_formulario():
        estado["selecionado_id"] = None
        entry_nome.delete(0, "end")
        option_status.set("Disponível")
        for item in tabela.selection():
            tabela.selection_remove(item)

    def cadastrar():
        nome = entry_nome.get().strip()
        status = option_status.get()
        try:
            _chamar(ctrl, "criar_barbeiro", nome, status)
            messagebox.showinfo("Sucesso", "Barbeiro cadastrado com sucesso!")
            limpar_formulario()
            carregar_barbeiros()
        except ValueError as erro:
            messagebox.showwarning("Atenção", str(erro))
        except Exception as erro:
            messagebox.showerror("Erro no banco de dados", str(erro))

    def atualizar():
        if estado["selecionado_id"] is None:
            messagebox.showwarning(
                "Atenção", "Selecione um barbeiro na tabela para alterar."
            )
            return

        nome = entry_nome.get().strip()
        status = option_status.get()
        try:
            _chamar(ctrl, "atualizar_barbeiro", estado["selecionado_id"], nome, status)
            messagebox.showinfo("Sucesso", "Dados do barbeiro atualizados!")
            limpar_formulario()
            carregar_barbeiros()
        except ValueError as erro:
            messagebox.showwarning("Atenção", str(erro))
        except Exception as erro:
            messagebox.showerror("Erro no banco de dados", str(erro))

    def alternar_status():
        if estado["selecionado_id"] is None:
            messagebox.showwarning(
                "Atenção", "Selecione um barbeiro na tabela para alternar o status."
            )
            return

        status_atual = option_status.get()
        novo_status = "Ocupado" if status_atual == "Disponível" else "Disponível"
        try:
            if _tem_funcao(ctrl, "atualizar_status_do_barbeiro"):
                _chamar(
                    ctrl,
                    "atualizar_status_do_barbeiro",
                    estado["selecionado_id"],
                    novo_status,
                )
            else:
                _chamar(
                    ctrl,
                    "atualizar_barbeiro",
                    estado["selecionado_id"],
                    entry_nome.get().strip(),
                    novo_status,
                )
            messagebox.showinfo("Sucesso", f"Status alterado para '{novo_status}'!")
            limpar_formulario()
            carregar_barbeiros()
        except ValueError as erro:
            messagebox.showwarning("Atenção", str(erro))
        except Exception as erro:
            messagebox.showerror("Erro no banco de dados", str(erro))

    def excluir():
        if estado["selecionado_id"] is None:
            messagebox.showwarning(
                "Atenção", "Selecione um barbeiro na tabela para excluir."
            )
            return

        confirmar = messagebox.askyesno(
            "Confirmar exclusão",
            f"Deseja mesmo excluir o barbeiro '{entry_nome.get().strip()}'?",
        )
        if not confirmar:
            return

        try:
            _chamar(ctrl, "excluir_barbeiro", estado["selecionado_id"])
            messagebox.showinfo("Sucesso", "Barbeiro excluído com sucesso!")
            limpar_formulario()
            carregar_barbeiros()
        except ValueError as erro:
            messagebox.showwarning("Atenção", str(erro))
        except Exception as erro:
            messagebox.showerror("Erro no banco de dados", str(erro))

    ctk.CTkButton(botoes_frame, text="Cadastrar", command=cadastrar).grid(
        row=0, column=0, sticky="we", padx=(0, 4), pady=(0, 6)
    )
    ctk.CTkButton(
        botoes_frame,
        text="Atualizar",
        fg_color="#2e7d32",
        hover_color="#1b5e20",
        command=atualizar,
    ).grid(row=0, column=1, sticky="we", padx=(4, 0), pady=(0, 6))
    ctk.CTkButton(
        botoes_frame,
        text="Excluir",
        fg_color="#c62828",
        hover_color="#8e0000",
        command=excluir,
    ).grid(row=1, column=0, sticky="we", padx=(0, 4), pady=(0, 6))
    ctk.CTkButton(
        botoes_frame,
        text="Limpar",
        fg_color="#455a64",
        hover_color="#263238",
        command=limpar_formulario,
    ).grid(row=1, column=1, sticky="we", padx=(4, 0), pady=(0, 6))
    ctk.CTkButton(
        botoes_frame,
        text="Alternar Status (Disponível / Ocupado)",
        fg_color="#ef6c00",
        hover_color="#e65100",
        command=alternar_status,
    ).grid(row=2, column=0, columnspan=2, sticky="we")

    ctk.CTkButton(
        topo_lista, text="Atualizar", width=85, height=28, command=carregar_barbeiros
    ).pack(side="right")

    entry_busca.bind("<KeyRelease>", filtrar_tabela)
    tabela.bind("<<TreeviewSelect>>", ao_selecionar_linha)

    carregar_barbeiros()
    return frame