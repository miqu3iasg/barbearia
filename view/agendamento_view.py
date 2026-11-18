from datetime import date, timedelta
from tkinter import messagebox, ttk

import customtkinter as ctk

from controller import (
    agendamento_controller,
    barbeiro_controller,
    cliente_controller,
    servico_controller,
)


def criar_tela_agendamentos(master, controllers=None, controller=None):
    ctrls = {
        "agendamento": controller or agendamento_controller,
        "cliente": cliente_controller,
        "barbeiro": barbeiro_controller,
        "servico": servico_controller,
    }
    if controllers:
        ctrls.update(controllers)

    mapas = {"clientes": {}, "barbeiros": {}, "servicos": {}}

    def executar(dominio: str, metodo: str, *args, **kwargs):
        ctrl = ctrls.get(dominio)
        if isinstance(ctrl, dict) and metodo in ctrl:
            return ctrl[metodo](*args, **kwargs)
        if ctrl is not None and hasattr(ctrl, metodo):
            return getattr(ctrl, metodo)(*args, **kwargs)
        raise AttributeError(f"Função '{metodo}' não encontrada em '{dominio}'.")

    def campo(item, chave: str, padrao=""):
        if isinstance(item, dict):
            return item.get(chave, padrao)
        return getattr(item, chave, padrao)

    def normalizar_hora(valor) -> str:
        if isinstance(valor, timedelta):
            minutos = int(valor.total_seconds()) // 60
            return f"{minutos // 60:02d}:{minutos % 60:02d}"
        texto = str(valor).strip()
        partes = texto.split(":")
        if len(partes) >= 2:
            return f"{partes[0].zfill(2)}:{partes[1].zfill(2)}"
        return texto

    frame = ctk.CTkScrollableFrame(master, fg_color="transparent")

    form_frame = ctk.CTkFrame(frame, corner_radius=8)
    form_frame.pack(fill="x", padx=4, pady=(4, 8))

    topo_form = ctk.CTkFrame(form_frame, fg_color="transparent")
    topo_form.pack(fill="x", padx=12, pady=(10, 6))

    ctk.CTkLabel(
        topo_form,
        text="Novo Agendamento",
        font=ctk.CTkFont(size=14, weight="bold"),
    ).pack(side="left")

    ctk.CTkLabel(form_frame, text="Cliente:").pack(anchor="w", padx=12)
    option_cliente = ctk.CTkOptionMenu(form_frame, values=["Carregando..."])
    option_cliente.pack(fill="x", padx=12, pady=(2, 6))

    ctk.CTkLabel(form_frame, text="Barbeiro:").pack(anchor="w", padx=12)
    option_barbeiro = ctk.CTkOptionMenu(form_frame, values=["Carregando..."])
    option_barbeiro.pack(fill="x", padx=12, pady=(2, 6))

    ctk.CTkLabel(form_frame, text="Serviço:").pack(anchor="w", padx=12)
    option_servico = ctk.CTkOptionMenu(form_frame, values=["Carregando..."])
    option_servico.pack(fill="x", padx=12, pady=(2, 6))

    linha_data_hora = ctk.CTkFrame(form_frame, fg_color="transparent")
    linha_data_hora.pack(fill="x", padx=12, pady=(2, 6))
    linha_data_hora.grid_columnconfigure(0, weight=1)
    linha_data_hora.grid_columnconfigure(1, weight=1)

    ctk.CTkLabel(linha_data_hora, text="Data (AAAA-MM-DD):").grid(
        row=0, column=0, sticky="w", padx=(0, 4)
    )
    ctk.CTkLabel(linha_data_hora, text="Horário livre:").grid(
        row=0, column=1, sticky="w", padx=(4, 0)
    )

    entry_data = ctk.CTkEntry(linha_data_hora, placeholder_text="2026-11-18")
    entry_data.insert(0, date.today().isoformat())
    entry_data.grid(row=1, column=0, sticky="we", padx=(0, 4), pady=(2, 0))

    horarios_iniciais = list(agendamento_controller.HORARIOS_ATENDIMENTO)
    option_horario = ctk.CTkOptionMenu(linha_data_hora, values=horarios_iniciais)
    option_horario.grid(row=1, column=1, sticky="we", padx=(4, 0), pady=(2, 0))

    ctk.CTkLabel(form_frame, text="Forma de pagamento:").pack(anchor="w", padx=12)
    option_pagamento = ctk.CTkOptionMenu(
        form_frame, values=["APOS_CORTE", "PIX_ONLINE"]
    )
    option_pagamento.pack(fill="x", padx=12, pady=(2, 6))

    ctk.CTkLabel(form_frame, text="Observação (opcional):").pack(anchor="w", padx=12)
    entry_observacao = ctk.CTkEntry(
        form_frame, placeholder_text="Ex.: Navalhado na zero"
    )
    entry_observacao.pack(fill="x", padx=12, pady=(2, 10))

    botoes_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
    botoes_frame.pack(fill="x", padx=12, pady=(0, 12))
    botoes_frame.grid_columnconfigure(0, weight=2)
    botoes_frame.grid_columnconfigure(1, weight=1)

    fila_frame = ctk.CTkFrame(frame, corner_radius=8)
    fila_frame.pack(fill="both", expand=True, padx=4, pady=(0, 6))

    topo_fila = ctk.CTkFrame(fila_frame, fg_color="transparent")
    topo_fila.pack(fill="x", padx=12, pady=(10, 6))

    ctk.CTkLabel(
        topo_fila,
        text="Fila de Atendimento",
        font=ctk.CTkFont(size=14, weight="bold"),
    ).pack(side="left")

    filtro_fila = ctk.CTkFrame(fila_frame, fg_color="transparent")
    filtro_fila.pack(fill="x", padx=12, pady=(0, 8))

    entry_data_fila = ctk.CTkEntry(
        filtro_fila, placeholder_text="Data da fila (AAAA-MM-DD)"
    )
    entry_data_fila.insert(0, date.today().isoformat())
    entry_data_fila.pack(side="left", fill="x", expand=True, padx=(0, 6))

    tabela_container = ctk.CTkFrame(fila_frame, fg_color="transparent")
    tabela_container.pack(fill="both", expand=True, padx=12, pady=(0, 8))

    colunas = ("horario", "cliente", "servico", "barbeiro")
    tabela = ttk.Treeview(
        tabela_container,
        columns=colunas,
        show="headings",
        selectmode="browse",
        height=6,
    )
    tabela.heading("horario", text="Hora")
    tabela.heading("cliente", text="Cliente")
    tabela.heading("servico", text="Serviço")
    tabela.heading("barbeiro", text="Barbeiro")

    tabela.column("horario", width=52, anchor="center")
    tabela.column("cliente", width=110, anchor="w")
    tabela.column("servico", width=95, anchor="w")
    tabela.column("barbeiro", width=80, anchor="w")

    scrollbar = ttk.Scrollbar(tabela_container, orient="vertical", command=tabela.yview)
    tabela.configure(yscrollcommand=scrollbar.set)

    tabela.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    acoes_fila = ctk.CTkFrame(fila_frame, fg_color="transparent")
    acoes_fila.pack(fill="x", padx=12, pady=(0, 10))
    acoes_fila.grid_columnconfigure(0, weight=1)
    acoes_fila.grid_columnconfigure(1, weight=1)

    def atualizar_horarios_livres(_event=None):
        barbeiro_label = option_barbeiro.get()
        barbeiro_id = mapas["barbeiros"].get(barbeiro_label)
        data_str = entry_data.get().strip()

        if barbeiro_id is None or not data_str:
            option_horario.configure(values=horarios_iniciais)
            option_horario.set(horarios_iniciais[0])
            return

        try:
            date.fromisoformat(data_str)
            livres = (
                executar("agendamento", "listar_horarios_livres", barbeiro_id, data_str)
                or []
            )
            if livres:
                option_horario.configure(values=livres)
                option_horario.set(livres[0])
            else:
                option_horario.configure(values=["Sem horários"])
                option_horario.set("Sem horários")
        except ValueError:
            pass
        except Exception as erro:
            messagebox.showerror("Erro ao consultar horários", str(erro))

    def carregar_opcoes():
        try:
            clientes = executar("cliente", "listar_clientes") or []
            mapas["clientes"] = {}
            for c in clientes:
                cid = int(campo(c, "id"))
                nome = campo(c, "nome", "")
                mapas["clientes"][f"{cid} - {nome}"] = cid

            if mapas["clientes"]:
                opcoes_c = list(mapas["clientes"].keys())
                option_cliente.configure(values=opcoes_c)
                if option_cliente.get() not in mapas["clientes"]:
                    option_cliente.set(opcoes_c[0])
            else:
                option_cliente.configure(values=["Nenhum cliente"])
                option_cliente.set("Nenhum cliente")

            barbeiros = executar("barbeiro", "listar_barbeiros") or []
            mapas["barbeiros"] = {}
            for b in barbeiros:
                bid = int(campo(b, "id"))
                nome = campo(b, "nome", "")
                mapas["barbeiros"][f"{bid} - {nome}"] = bid

            if mapas["barbeiros"]:
                opcoes_b = list(mapas["barbeiros"].keys())
                option_barbeiro.configure(values=opcoes_b)
                if option_barbeiro.get() not in mapas["barbeiros"]:
                    option_barbeiro.set(opcoes_b[0])
            else:
                option_barbeiro.configure(values=["Nenhum barbeiro"])
                option_barbeiro.set("Nenhum barbeiro")

            servicos = executar("servico", "listar_servicos") or []
            mapas["servicos"] = {}
            for s in servicos:
                sid = int(campo(s, "id"))
                nome = campo(s, "nome", "")
                preco = float(campo(s, "preco", 0))
                mapas["servicos"][f"{sid} - {nome} (R$ {preco:.2f})"] = sid

            if mapas["servicos"]:
                opcoes_s = list(mapas["servicos"].keys())
                option_servico.configure(values=opcoes_s)
                if option_servico.get() not in mapas["servicos"]:
                    option_servico.set(opcoes_s[0])
            else:
                option_servico.configure(values=["Nenhum serviço"])
                option_servico.set("Nenhum serviço")

            atualizar_horarios_livres()
        except Exception as erro:
            messagebox.showerror("Erro ao carregar dados", str(erro))

    def carregar_fila(_event=None):
        data_str = entry_data_fila.get().strip()
        try:
            date.fromisoformat(data_str)
        except ValueError:
            messagebox.showwarning(
                "Atenção", "Informe a data da fila no formato AAAA-MM-DD."
            )
            return

        try:
            fila = executar("agendamento", "ver_fila_do_dia", data_str) or []
            for item in tabela.get_children():
                tabela.delete(item)

            for ag in fila:
                ag_id = campo(ag, "id", None)
                if ag_id is None:
                    ag_id = campo(ag, "agendamento_id", None)
                horario = normalizar_hora(campo(ag, "horario", ""))
                cliente = campo(ag, "cliente", "")
                servico = campo(ag, "servico", "")
                barbeiro = campo(ag, "barbeiro", "")
                if ag_id is not None:
                    tabela.insert(
                        "",
                        "end",
                        iid=str(ag_id),
                        values=(horario, cliente, servico, barbeiro),
                    )
                else:
                    tabela.insert(
                        "", "end", values=(horario, cliente, servico, barbeiro)
                    )
        except Exception as erro:
            messagebox.showerror("Erro ao carregar fila", str(erro))

    def _id_fila_selecionado():
        selecao = tabela.selection()
        if not selecao:
            messagebox.showwarning(
                "Atenção", "Selecione um atendimento na fila primeiro."
            )
            return None
        item_id = selecao[0]
        if not str(item_id).isdigit():
            messagebox.showwarning(
                "Atenção", "Não foi possível identificar o ID deste agendamento."
            )
            return None
        return int(item_id)

    def concluir_selecionado():
        ag_id = _id_fila_selecionado()
        if ag_id is None:
            return
        try:
            executar("agendamento", "concluir_atendimento", ag_id)
            messagebox.showinfo("Sucesso", "Atendimento concluído!")
            carregar_fila()
        except ValueError as erro:
            messagebox.showwarning("Atenção", str(erro))
        except Exception as erro:
            messagebox.showerror("Erro no banco de dados", str(erro))

    def cancelar_selecionado():
        ag_id = _id_fila_selecionado()
        if ag_id is None:
            return
        confirmar = messagebox.askyesno(
            "Confirmar cancelamento",
            "Deseja mesmo cancelar este agendamento?",
        )
        if not confirmar:
            return
        try:
            executar("agendamento", "cancelar_agendamento", ag_id)
            messagebox.showinfo("Sucesso", "Agendamento cancelado!")
            carregar_fila()
            atualizar_horarios_livres()
        except ValueError as erro:
            messagebox.showwarning("Atenção", str(erro))
        except Exception as erro:
            messagebox.showerror("Erro no banco de dados", str(erro))

    def limpar_formulario():
        entry_data.delete(0, "end")
        entry_data.insert(0, date.today().isoformat())
        option_pagamento.set("APOS_CORTE")
        entry_observacao.delete(0, "end")
        atualizar_horarios_livres()

    def agendar():
        cliente_id = mapas["clientes"].get(option_cliente.get())
        barbeiro_id = mapas["barbeiros"].get(option_barbeiro.get())
        servico_id = mapas["servicos"].get(option_servico.get())
        data_str = entry_data.get().strip()
        horario = option_horario.get()
        pagamento = option_pagamento.get()
        obs_texto = entry_observacao.get().strip()
        observacao = obs_texto if obs_texto else None

        if cliente_id is None or barbeiro_id is None or servico_id is None:
            messagebox.showwarning(
                "Atenção", "Selecione cliente, barbeiro e serviço válidos."
            )
            return

        try:
            date.fromisoformat(data_str)
        except ValueError:
            messagebox.showwarning(
                "Atenção", "Data inválida. Use o formato AAAA-MM-DD."
            )
            return

        if not horario or horario == "Sem horários":
            messagebox.showwarning(
                "Atenção", "Não há horários livres disponíveis para esta data."
            )
            return

        try:
            executar(
                "agendamento",
                "agendar",
                cliente_id,
                barbeiro_id,
                servico_id,
                data_str,
                horario,
                pagamento,
                observacao,
            )
            messagebox.showinfo("Sucesso", "Agendamento registrado com sucesso!")
            entry_data_fila.delete(0, "end")
            entry_data_fila.insert(0, data_str)
            limpar_formulario()
            carregar_fila()
        except ValueError as erro:
            messagebox.showwarning("Atenção", str(erro))
        except Exception as erro:
            messagebox.showerror("Erro no banco de dados", str(erro))

    def recarregar_tudo():
        carregar_opcoes()
        carregar_fila()

    ctk.CTkButton(
        topo_form,
        text="Recarregar",
        width=85,
        height=26,
        command=carregar_opcoes,
    ).pack(side="right")

    option_barbeiro.configure(command=atualizar_horarios_livres)
    entry_data.bind("<FocusOut>", atualizar_horarios_livres)
    entry_data.bind("<Return>", atualizar_horarios_livres)

    ctk.CTkButton(botoes_frame, text="Confirmar Agendamento", command=agendar).grid(
        row=0, column=0, sticky="we", padx=(0, 4)
    )
    ctk.CTkButton(
        botoes_frame,
        text="Limpar",
        fg_color="#455a64",
        hover_color="#263238",
        command=limpar_formulario,
    ).grid(row=0, column=1, sticky="we", padx=(4, 0))

    ctk.CTkButton(
        topo_fila,
        text="Atualizar",
        width=85,
        height=26,
        command=carregar_fila,
    ).pack(side="right")

    entry_data_fila.bind("<Return>", carregar_fila)
    ctk.CTkButton(
        filtro_fila,
        text="Filtrar Dia",
        width=90,
        command=carregar_fila,
    ).pack(side="right")

    ctk.CTkButton(
        acoes_fila,
        text="Concluir Atendimento",
        fg_color="#2e7d32",
        hover_color="#1b5e20",
        command=concluir_selecionado,
    ).grid(row=0, column=0, sticky="we", padx=(0, 4))
    ctk.CTkButton(
        acoes_fila,
        text="Cancelar Agendamento",
        fg_color="#c62828",
        hover_color="#8e0000",
        command=cancelar_selecionado,
    ).grid(row=0, column=1, sticky="we", padx=(4, 0))

    frame.recarregar_tudo = recarregar_tudo

    carregar_opcoes()
    carregar_fila()
    return frame
