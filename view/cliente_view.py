from tkinter import messagebox, ttk

import customtkinter as ctk

from controller import cliente_controller


def _chamar(ctrl, funcao: str, *args):
    if isinstance(ctrl, dict):
        return ctrl[funcao](*args)
    return getattr(ctrl, funcao)(*args)


def criar_tela_clientes(master, controller=None):
    ctrl = controller if controller is not None else cliente_controller
    estado = {"selecionado_id": None, "todos": []}

    frame = ctk.CTkFrame(master, fg_color="transparent")

    form_frame = ctk.CTkFrame(frame, corner_radius=8)
    form_frame.pack(fill="x", padx=4, pady=(4, 6))

    ctk.CTkLabel(
        form_frame,
        text="Cadastro de Clientes",
        font=ctk.CTkFont(size=14, weight="bold"),
    ).pack(anchor="w", padx=12, pady=(10, 6))

    ctk.CTkLabel(form_frame, text="Nome completo:").pack(anchor="w", padx=12)
    entry_nome = ctk.CTkEntry(form_frame, placeholder_text="Ex.: Lucas Almeida")
    entry_nome.pack(fill="x", padx=12, pady=(2, 6))

    ctk.CTkLabel(form_frame, text="Telefone (DDD + número):").pack(anchor="w", padx=12)
    entry_telefone = ctk.CTkEntry(form_frame, placeholder_text="Ex.: 11987654321")
    entry_telefone.pack(fill="x", padx=12, pady=(2, 8))

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
        text="Clientes Cadastrados",
        font=ctk.CTkFont(size=14, weight="bold"),
    ).pack(side="left")

    entry_busca = ctk.CTkEntry(
        lista_frame,
        placeholder_text="Buscar por nome ou telefone...",
    )
    entry_busca.pack(fill="x", padx=12, pady=(0, 8))

    style = ttk.Style()
    style.theme_use("default")
    style.configure(
        "Treeview",
        background="#2b2b2b",
        foreground="#f5f5f5",
        fieldbackground="#2b2b2b",
        rowheight=26,
        borderwidth=0,
    )
    style.configure(
        "Treeview.Heading",
        background="#1f538d",
        foreground="white",
        font=("Sans", 9, "bold"),
    )
    style.map("Treeview", background=[("selected", "#144870")])

    tabela_container = ctk.CTkFrame(lista_frame, fg_color="transparent")
    tabela_container.pack(fill="both", expand=True, padx=12, pady=(0, 10))

    colunas = ("id", "nome", "telefone")
    tabela = ttk.Treeview(
        tabela_container, columns=colunas, show="headings", selectmode="browse"
    )
    tabela.heading("id", text="ID")
    tabela.heading("nome", text="Nome")
    tabela.heading("telefone", text="Telefone")

    tabela.column("id", width=38, anchor="center")
    tabela.column("nome", width=185, anchor="w")
    tabela.column("telefone", width=115, anchor="center")

    scrollbar = ttk.Scrollbar(tabela_container, orient="vertical", command=tabela.yview)
    tabela.configure(yscrollcommand=scrollbar.set)

    tabela.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def extrair_campos(cliente):
        if isinstance(cliente, dict):
            return (
                cliente.get("id"),
                cliente.get("nome", ""),
                cliente.get("telefone", ""),
            )
        return (
            getattr(cliente, "id", ""),
            getattr(cliente, "nome", ""),
            getattr(cliente, "telefone", ""),
        )

    def filtrar_tabela(_event=None):
        termo = entry_busca.get().strip().lower()
        for item in tabela.get_children():
            tabela.delete(item)

        for cliente in estado["todos"]:
            cid, nome, telefone = extrair_campos(cliente)
            if (
                not termo
                or termo in str(nome).lower()
                or termo in str(telefone).lower()
            ):
                tabela.insert("", "end", values=(cid, nome, telefone))

    def carregar_clientes():
        try:
            estado["todos"] = _chamar(ctrl, "listar_clientes") or []
            filtrar_tabela()
        except Exception as erro:
            messagebox.showerror("Erro ao listar clientes", str(erro))

    def ao_selecionar_linha(_event):
        selecao = tabela.selection()
        if not selecao:
            return
        valores = tabela.item(selecao[0], "values")
        estado["selecionado_id"] = int(valores[0])

        entry_nome.delete(0, "end")
        entry_nome.insert(0, valores[1])

        entry_telefone.delete(0, "end")
        entry_telefone.insert(0, valores[2])

    def limpar_formulario():
        estado["selecionado_id"] = None
        entry_nome.delete(0, "end")
        entry_telefone.delete(0, "end")
        for item in tabela.selection():
            tabela.selection_remove(item)

    def cadastrar():
        nome = entry_nome.get().strip()
        telefone = entry_telefone.get().strip()
        try:
            _chamar(ctrl, "cadastrar_cliente", nome, telefone)
            messagebox.showinfo("Sucesso", "Cliente cadastrado com sucesso!")
            limpar_formulario()
            carregar_clientes()
        except ValueError as erro:
            messagebox.showwarning("Atenção", str(erro))
        except Exception as erro:
            messagebox.showerror("Erro no banco de dados", str(erro))

    def atualizar():
        if estado["selecionado_id"] is None:
            messagebox.showwarning(
                "Atenção", "Selecione um cliente na tabela para alterar."
            )
            return

        nome = entry_nome.get().strip()
        telefone = entry_telefone.get().strip()
        try:
            _chamar(ctrl, "atualizar_cliente", estado["selecionado_id"], nome, telefone)
            messagebox.showinfo("Sucesso", "Dados do cliente atualizados!")
            limpar_formulario()
            carregar_clientes()
        except ValueError as erro:
            messagebox.showwarning("Atenção", str(erro))
        except Exception as erro:
            messagebox.showerror("Erro no banco de dados", str(erro))

    def excluir():
        if estado["selecionado_id"] is None:
            messagebox.showwarning(
                "Atenção", "Selecione um cliente na tabela para excluir."
            )
            return

        confirmar = messagebox.askyesno(
            "Confirmar exclusão",
            f"Deseja mesmo excluir o cliente '{entry_nome.get().strip()}'?",
        )
        if not confirmar:
            return

        try:
            _chamar(ctrl, "excluir_cliente", estado["selecionado_id"])
            messagebox.showinfo("Sucesso", "Cliente excluído com sucesso!")
            limpar_formulario()
            carregar_clientes()
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
    ).grid(row=1, column=0, sticky="we", padx=(0, 4))
    ctk.CTkButton(
        botoes_frame,
        text="Limpar",
        fg_color="#455a64",
        hover_color="#263238",
        command=limpar_formulario,
    ).grid(row=1, column=1, sticky="we", padx=(4, 0))

    ctk.CTkButton(
        topo_lista, text="Atualizar", width=85, height=28, command=carregar_clientes
    ).pack(side="right")

    entry_busca.bind("<KeyRelease>", filtrar_tabela)
    tabela.bind("<<TreeviewSelect>>", ao_selecionar_linha)

    carregar_clientes()
    return frame
