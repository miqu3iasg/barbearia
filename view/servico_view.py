from tkinter import messagebox, ttk
import customtkinter as ctk


def _chamar(ctrl, funcao: str, *args):
    if isinstance(ctrl, dict):
        return ctrl[funcao](*args)
    return getattr(ctrl, funcao)(*args)


def _criar_mock_servico():
    dados = {
        "lista": [
            {"id": 1, "nome": "Degradê", "preco": 35.00},
            {"id": 2, "nome": "Social", "preco": 30.00},
            {"id": 3, "nome": "Corte na Tesoura", "preco": 40.00},
            {"id": 4, "nome": "Sobrancelha", "preco": 15.00},
            {"id": 5, "nome": "Barba", "preco": 25.00},
            {"id": 10, "nome": "Corte + Barba", "preco": 55.00},
        ],
        "proximo_id": 13,
    }

    def validar(nome: str, preco: float):
        nome_limpo = nome.strip()
        if not nome_limpo:
            raise ValueError("O nome do serviço é obrigatório.")
        if len(nome_limpo) > 50:
            raise ValueError("O nome do serviço deve ter no máximo 50 caracteres.")
        if preco <= 0:
            raise ValueError("O preço do serviço deve ser maior que zero.")

    def listar_todos_os_servicos():
        return list(dados["lista"])

    def criar_servico(nome: str, preco: float):
        validar(nome, preco)
        novo_id = dados["proximo_id"]
        dados["lista"].append(
            {"id": novo_id, "nome": nome.strip(), "preco": float(preco)}
        )
        dados["proximo_id"] += 1
        return novo_id

    def atualizar_servico(servico_id: int, nome: str, preco: float):
        validar(nome, preco)
        for servico in dados["lista"]:
            if servico["id"] == servico_id:
                servico["nome"] = nome.strip()
                servico["preco"] = float(preco)
                return True
        return False

    def excluir_servico(servico_id: int):
        for i, servico in enumerate(dados["lista"]):
            if servico["id"] == servico_id:
                dados["lista"].pop(i)
                return True
        return False

    return {
        "listar_todos_os_servicos": listar_todos_os_servicos,
        "criar_servico": criar_servico,
        "atualizar_servico": atualizar_servico,
        "excluir_servico": excluir_servico,
    }


def criar_tela_servicos(master, controller=None):
    ctrl = controller if controller is not None else _criar_mock_servico()
    estado = {"selecionado_id": None, "todos": []}

    frame = ctk.CTkFrame(master, fg_color="transparent")

    form_frame = ctk.CTkFrame(frame, corner_radius=8)
    form_frame.pack(fill="x", padx=4, pady=(4, 6))

    ctk.CTkLabel(
        form_frame,
        text="Cadastro de Serviços",
        font=ctk.CTkFont(size=14, weight="bold"),
    ).pack(anchor="w", padx=12, pady=(10, 6))

    ctk.CTkLabel(form_frame, text="Nome do serviço:").pack(anchor="w", padx=12)
    entry_nome = ctk.CTkEntry(form_frame, placeholder_text="Ex.: Corte + Barba")
    entry_nome.pack(fill="x", padx=12, pady=(2, 6))

    ctk.CTkLabel(form_frame, text="Preço (R$):").pack(anchor="w", padx=12)
    entry_preco = ctk.CTkEntry(form_frame, placeholder_text="Ex.: 45.00")
    entry_preco.pack(fill="x", padx=12, pady=(2, 8))

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
        text="Serviços Cadastrados",
        font=ctk.CTkFont(size=14, weight="bold"),
    ).pack(side="left")

    entry_busca = ctk.CTkEntry(
        lista_frame,
        placeholder_text="Buscar por serviço ou preço...",
    )
    entry_busca.pack(fill="x", padx=12, pady=(0, 8))

    tabela_container = ctk.CTkFrame(lista_frame, fg_color="transparent")
    tabela_container.pack(fill="both", expand=True, padx=12, pady=(0, 10))

    colunas = ("id", "nome", "preco")
    tabela = ttk.Treeview(
        tabela_container, columns=colunas, show="headings", selectmode="browse"
    )
    tabela.heading("id", text="ID")
    tabela.heading("nome", text="Serviço")
    tabela.heading("preco", text="Preço")

    tabela.column("id", width=38, anchor="center")
    tabela.column("nome", width=205, anchor="w")
    tabela.column("preco", width=95, anchor="center")

    scrollbar = ttk.Scrollbar(
        tabela_container, orient="vertical", command=tabela.yview
    )
    tabela.configure(yscrollcommand=scrollbar.set)

    tabela.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def extrair_campos(servico):
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

    def converter_preco(texto: str) -> float:
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

    def filtrar_tabela(_event=None):
        termo = entry_busca.get().strip().lower()
        for item in tabela.get_children():
            tabela.delete(item)

        for servico in estado["todos"]:
            sid, nome, preco = extrair_campos(servico)
            preco_formatado = f"R$ {preco:.2f}"
            if (
                not termo
                or termo in str(nome).lower()
                or termo in preco_formatado.lower()
            ):
                tabela.insert("", "end", values=(sid, nome, preco_formatado))

    def carregar_servicos():
        try:
            estado["todos"] = _chamar(ctrl, "listar_todos_os_servicos") or []
            filtrar_tabela()
        except Exception as erro:
            messagebox.showerror("Erro ao listar serviços", str(erro))

    def ao_selecionar_linha(_event):
        selecao = tabela.selection()
        if not selecao:
            return
        valores = tabela.item(selecao[0], "values")
        estado["selecionado_id"] = int(valores[0])

        entry_nome.delete(0, "end")
        entry_nome.insert(0, valores[1])

        preco_limpo = str(valores[2]).replace("R$", "").strip()
        entry_preco.delete(0, "end")
        entry_preco.insert(0, preco_limpo)

    def limpar_formulario():
        estado["selecionado_id"] = None
        entry_nome.delete(0, "end")
        entry_preco.delete(0, "end")
        for item in tabela.selection():
            tabela.selection_remove(item)

    def cadastrar():
        nome = entry_nome.get().strip()
        try:
            preco = converter_preco(entry_preco.get())
            _chamar(ctrl, "criar_servico", nome, preco)
            messagebox.showinfo("Sucesso", "Serviço cadastrado com sucesso!")
            limpar_formulario()
            carregar_servicos()
        except ValueError as erro:
            messagebox.showwarning("Atenção", str(erro))
        except Exception as erro:
            messagebox.showerror("Erro no banco de dados", str(erro))

    def atualizar():
        if estado["selecionado_id"] is None:
            messagebox.showwarning(
                "Atenção", "Selecione um serviço na tabela para alterar."
            )
            return

        nome = entry_nome.get().strip()
        try:
            preco = converter_preco(entry_preco.get())
            _chamar(ctrl, "atualizar_servico", estado["selecionado_id"], nome, preco)
            messagebox.showinfo("Sucesso", "Serviço atualizado com sucesso!")
            limpar_formulario()
            carregar_servicos()
        except ValueError as erro:
            messagebox.showwarning("Atenção", str(erro))
        except Exception as erro:
            messagebox.showerror("Erro no banco de dados", str(erro))

    def excluir():
        if estado["selecionado_id"] is None:
            messagebox.showwarning(
                "Atenção", "Selecione um serviço na tabela para excluir."
            )
            return

        confirmar = messagebox.askyesno(
            "Confirmar exclusão",
            f"Deseja mesmo excluir o serviço '{entry_nome.get().strip()}'?",
        )
        if not confirmar:
            return

        try:
            _chamar(ctrl, "excluir_servico", estado["selecionado_id"])
            messagebox.showinfo("Sucesso", "Serviço excluído com sucesso!")
            limpar_formulario()
            carregar_servicos()
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
        topo_lista, text="Atualizar", width=85, height=28, command=carregar_servicos
    ).pack(side="right")

    entry_busca.bind("<KeyRelease>", filtrar_tabela)
    tabela.bind("<<TreeviewSelect>>", ao_selecionar_linha)

    carregar_servicos()
    return frame