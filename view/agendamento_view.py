from datetime import date
from tkinter import messagebox, ttk
import customtkinter as ctk


class _MockAgendamentoController:

    def __init__(self):
        self._clientes = [
            {"id": 1, "nome": "João Silva", "telefone": "11999998888"},
            {"id": 2, "nome": "Carlos Souza", "telefone": "11988887777"},
        ]
        self._barbeiros = [
            {"id": 1, "nome": "Wild", "status": "Disponível"},
            {"id": 2, "nome": "Alexandre de Moraes", "status": "Disponível"},
            {"id": 3, "nome": "Ximbinha", "status": "Disponível"},
            {"id": 4, "nome": "Cleito Rasta", "status": "Disponível"},
        ]
        self._servicos = [
            {"id": 1, "nome": "Degradê", "preco": 35.00},
            {"id": 2, "nome": "Social", "preco": 30.00},
            {"id": 5, "nome": "Barba", "preco": 25.00},
            {"id": 10, "nome": "Corte + Barba", "preco": 55.00},
        ]
        hoje = date.today().isoformat()
        self._agendamentos = [
            {
                "agendamento_id": 1,
                "cliente_id": 1,
                "cliente": "João Silva",
                "barbeiro_id": 1,
                "barbeiro": "Wild",
                "servico_id": 1,
                "servico": "Degradê",
                "data_agendamento": hoje,
                "horario": "09:00",
                "pagamento": "APOS_CORTE",
                "observacao": None,
            }
        ]
        self._proximo_id = 2

    def listar_todos_os_clientes(self):
        return list(self._clientes)

    def listar_todos_os_barbeiros(self):
        return list(self._barbeiros)

    def listar_todos_os_servicos(self):
        return list(self._servicos)

    def listar_horarios_ocupados(self, barbeiro_id: int, data_agendamento: str):
        return [
            ag["horario"]
            for ag in self._agendamentos
            if ag["barbeiro_id"] == barbeiro_id
            and str(ag["data_agendamento"]) == str(data_agendamento)
        ]

    def listar_fila_atendimento(self, data_agendamento: str):
        fila = [
            {
                "agendamento_id": ag["agendamento_id"],
                "cliente": ag["cliente"],
                "servico": ag["servico"],
                "barbeiro": ag["barbeiro"],
                "horario": ag["horario"],
            }
            for ag in self._agendamentos
            if str(ag["data_agendamento"]) == str(data_agendamento)
        ]
        return sorted(fila, key=lambda item: item["horario"])

    def criar_agendamento(
        self,
        cliente_id: int,
        barbeiro_id: int,
        servico_id: int,
        data_agendamento: str,
        horario: str,
        pagamento: str,
        observacao: str | None = None,
    ):
        if pagamento not in ("APOS_CORTE", "PIX_ONLINE"):
            raise ValueError("Forma de pagamento inválida.")
        if horario in self.listar_horarios_ocupados(barbeiro_id, data_agendamento):
            raise ValueError("Este barbeiro já possui agendamento nesse horário.")

        cliente_nome = next(
            (c["nome"] for c in self._clientes if c["id"] == cliente_id), "Cliente"
        )
        barbeiro_nome = next(
            (b["nome"] for b in self._barbeiros if b["id"] == barbeiro_id), "Barbeiro"
        )
        servico_nome = next(
            (s["nome"] for s in self._servicos if s["id"] == servico_id), "Serviço"
        )

        novo_id = self._proximo_id
        self._agendamentos.append(
            {
                "agendamento_id": novo_id,
                "cliente_id": cliente_id,
                "cliente": cliente_nome,
                "barbeiro_id": barbeiro_id,
                "barbeiro": barbeiro_nome,
                "servico_id": servico_id,
                "servico": servico_nome,
                "data_agendamento": data_agendamento,
                "horario": horario,
                "pagamento": pagamento,
                "observacao": observacao,
            }
        )
        self._proximo_id += 1
        return novo_id


class AgendamentoView(ctk.CTkScrollableFrame):

    HORARIOS_PADRAO = [
        "08:00",
        "09:00",
        "10:00",
        "11:00",
        "13:00",
        "14:00",
        "15:00",
        "16:00",
        "17:00",
        "18:00",
        "19:00",
    ]

    def __init__(self, master, controllers: dict | None = None, controller=None):
        super().__init__(master, fg_color="transparent")
        self.controllers = controllers or {}
        self.controller_principal = controller
        self._mock = _MockAgendamentoController()

        self._mapa_clientes: dict[str, int] = {}
        self._mapa_barbeiros: dict[str, int] = {}
        self._mapa_servicos: dict[str, int] = {}

        self._construir_interface()
        self.carregar_opcoes()
        self.carregar_fila()

    def _executar(self, dominio: str, metodo: str, *args, **kwargs):
        ctrl = self.controllers.get(dominio)
        if ctrl is not None and hasattr(ctrl, metodo):
            return getattr(ctrl, metodo)(*args, **kwargs)
        if self.controller_principal is not None and hasattr(
            self.controller_principal, metodo
        ):
            return getattr(self.controller_principal, metodo)(*args, **kwargs)
        return getattr(self._mock, metodo)(*args, **kwargs)

    @staticmethod
    def _campo(item, chave: str, padrao=""):
        if isinstance(item, dict):
            return item.get(chave, padrao)
        return getattr(item, chave, padrao)

    @staticmethod
    def _normalizar_hora(valor) -> str:
        texto = str(valor).strip()
        partes = texto.split(":")
        if len(partes) >= 2:
            return f"{partes[0].zfill(2)}:{partes[1].zfill(2)}"
        return texto

    def _construir_interface(self):
        form_frame = ctk.CTkFrame(self, corner_radius=8)
        form_frame.pack(fill="x", padx=4, pady=(4, 8))

        topo_form = ctk.CTkFrame(form_frame, fg_color="transparent")
        topo_form.pack(fill="x", padx=12, pady=(10, 6))

        ctk.CTkLabel(
            topo_form,
            text="Novo Agendamento",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(side="left")

        ctk.CTkButton(
            topo_form,
            text="Recarregar",
            width=85,
            height=26,
            command=self.carregar_opcoes,
        ).pack(side="right")

        ctk.CTkLabel(form_frame, text="Cliente:").pack(anchor="w", padx=12)
        self.option_cliente = ctk.CTkOptionMenu(form_frame, values=["Carregando..."])
        self.option_cliente.pack(fill="x", padx=12, pady=(2, 6))

        ctk.CTkLabel(form_frame, text="Barbeiro:").pack(anchor="w", padx=12)
        self.option_barbeiro = ctk.CTkOptionMenu(
            form_frame,
            values=["Carregando..."],
            command=lambda _val: self.atualizar_horarios_livres(),
        )
        self.option_barbeiro.pack(fill="x", padx=12, pady=(2, 6))

        ctk.CTkLabel(form_frame, text="Serviço:").pack(anchor="w", padx=12)
        self.option_servico = ctk.CTkOptionMenu(form_frame, values=["Carregando..."])
        self.option_servico.pack(fill="x", padx=12, pady=(2, 6))

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

        self.entry_data = ctk.CTkEntry(linha_data_hora, placeholder_text="2026-11-15")
        self.entry_data.insert(0, date.today().isoformat())
        self.entry_data.grid(row=1, column=0, sticky="we", padx=(0, 4), pady=(2, 0))
        self.entry_data.bind(
            "<FocusOut>", lambda _event: self.atualizar_horarios_livres()
        )

        self.option_horario = ctk.CTkOptionMenu(
            linha_data_hora, values=self.HORARIOS_PADRAO
        )
        self.option_horario.grid(row=1, column=1, sticky="we", padx=(4, 0), pady=(2, 0))

        ctk.CTkLabel(form_frame, text="Forma de pagamento:").pack(anchor="w", padx=12)
        self.option_pagamento = ctk.CTkOptionMenu(
            form_frame, values=["APOS_CORTE", "PIX_ONLINE"]
        )
        self.option_pagamento.pack(fill="x", padx=12, pady=(2, 6))

        ctk.CTkLabel(form_frame, text="Observação (opcional):").pack(
            anchor="w", padx=12
        )
        self.entry_observacao = ctk.CTkEntry(
            form_frame, placeholder_text="Ex.: Navalhado na zero"
        )
        self.entry_observacao.pack(fill="x", padx=12, pady=(2, 10))

        botoes_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        botoes_frame.pack(fill="x", padx=12, pady=(0, 12))
        botoes_frame.grid_columnconfigure(0, weight=2)
        botoes_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            botoes_frame, text="Confirmar Agendamento", command=self._agendar
        ).grid(row=0, column=0, sticky="we", padx=(0, 4))

        ctk.CTkButton(
            botoes_frame,
            text="Limpar",
            fg_color="#455a64",
            hover_color="#263238",
            command=self._limpar_formulario,
        ).grid(row=0, column=1, sticky="we", padx=(4, 0))

        fila_frame = ctk.CTkFrame(self, corner_radius=8)
        fila_frame.pack(fill="both", expand=True, padx=4, pady=(0, 6))

        topo_fila = ctk.CTkFrame(fila_frame, fg_color="transparent")
        topo_fila.pack(fill="x", padx=12, pady=(10, 6))

        ctk.CTkLabel(
            topo_fila,
            text="Fila de Atendimento",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(side="left")

        ctk.CTkButton(
            topo_fila,
            text="Atualizar",
            width=85,
            height=26,
            command=self.carregar_fila,
        ).pack(side="right")

        filtro_fila = ctk.CTkFrame(fila_frame, fg_color="transparent")
        filtro_fila.pack(fill="x", padx=12, pady=(0, 8))

        self.entry_data_fila = ctk.CTkEntry(
            filtro_fila, placeholder_text="Data da fila (AAAA-MM-DD)"
        )
        self.entry_data_fila.insert(0, date.today().isoformat())
        self.entry_data_fila.pack(side="left", fill="x", expand=True, padx=(0, 6))

        ctk.CTkButton(
            filtro_fila,
            text="Filtrar Dia",
            width=90,
            command=self.carregar_fila,
        ).pack(side="right")

        tabela_container = ctk.CTkFrame(fila_frame, fg_color="transparent")
        tabela_container.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        colunas = ("horario", "cliente", "servico", "barbeiro")
        self.tabela = ttk.Treeview(
            tabela_container,
            columns=colunas,
            show="headings",
            selectmode="browse",
            height=7,
        )
        self.tabela.heading("horario", text="Hora")
        self.tabela.heading("cliente", text="Cliente")
        self.tabela.heading("servico", text="Serviço")
        self.tabela.heading("barbeiro", text="Barbeiro")

        self.tabela.column("horario", width=52, anchor="center")
        self.tabela.column("cliente", width=110, anchor="w")
        self.tabela.column("servico", width=95, anchor="w")
        self.tabela.column("barbeiro", width=80, anchor="w")

        scrollbar = ttk.Scrollbar(
            tabela_container, orient="vertical", command=self.tabela.yview
        )
        self.tabela.configure(yscrollcommand=scrollbar.set)

        self.tabela.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def carregar_opcoes(self):
        try:
            clientes = self._executar("cliente", "listar_todos_os_clientes") or []
            self._mapa_clientes = {}
            for c in clientes:
                cid = int(self._campo(c, "id"))
                nome = self._campo(c, "nome", "")
                self._mapa_clientes[f"{cid} - {nome}"] = cid

            if self._mapa_clientes:
                opcoes_c = list(self._mapa_clientes.keys())
                self.option_cliente.configure(values=opcoes_c)
                self.option_cliente.set(opcoes_c[0])
            else:
                self.option_cliente.configure(values=["Nenhum cliente"])
                self.option_cliente.set("Nenhum cliente")

            barbeiros = self._executar("barbeiro", "listar_todos_os_barbeiros") or []
            self._mapa_barbeiros = {}
            for b in barbeiros:
                bid = int(self._campo(b, "id"))
                nome = self._campo(b, "nome", "")
                self._mapa_barbeiros[f"{bid} - {nome}"] = bid

            if self._mapa_barbeiros:
                opcoes_b = list(self._mapa_barbeiros.keys())
                self.option_barbeiro.configure(values=opcoes_b)
                self.option_barbeiro.set(opcoes_b[0])
            else:
                self.option_barbeiro.configure(values=["Nenhum barbeiro"])
                self.option_barbeiro.set("Nenhum barbeiro")

            servicos = self._executar("servico", "listar_todos_os_servicos") or []
            self._mapa_servicos = {}
            for s in servicos:
                sid = int(self._campo(s, "id"))
                nome = self._campo(s, "nome", "")
                preco = float(self._campo(s, "preco", 0))
                self._mapa_servicos[f"{sid} - {nome} (R$ {preco:.2f})"] = sid

            if self._mapa_servicos:
                opcoes_s = list(self._mapa_servicos.keys())
                self.option_servico.configure(values=opcoes_s)
                self.option_servico.set(opcoes_s[0])
            else:
                self.option_servico.configure(values=["Nenhum serviço"])
                self.option_servico.set("Nenhum serviço")

            self.atualizar_horarios_livres()
        except Exception as erro:
            messagebox.showerror("Erro ao carregar dados", str(erro))

    def atualizar_horarios_livres(self):
        barbeiro_label = self.option_barbeiro.get()
        barbeiro_id = self._mapa_barbeiros.get(barbeiro_label)
        data_str = self.entry_data.get().strip()

        if barbeiro_id is None or not data_str:
            self.option_horario.configure(values=self.HORARIOS_PADRAO)
            self.option_horario.set(self.HORARIOS_PADRAO[0])
            return

        try:
            date.fromisoformat(data_str)
            ocupados_bruto = (
                self._executar(
                    "agendamento", "listar_horarios_ocupados", barbeiro_id, data_str
                )
                or []
            )
            ocupados = {self._normalizar_hora(h) for h in ocupados_bruto}
            livres = [h for h in self.HORARIOS_PADRAO if h not in ocupados]

            if livres:
                self.option_horario.configure(values=livres)
                self.option_horario.set(livres[0])
            else:
                self.option_horario.configure(values=["Sem horários"])
                self.option_horario.set("Sem horários")
        except ValueError:
            pass
        except Exception as erro:
            messagebox.showerror("Erro ao consultar horários", str(erro))

    def carregar_fila(self):
        data_str = self.entry_data_fila.get().strip()
        try:
            date.fromisoformat(data_str)
        except ValueError:
            messagebox.showwarning(
                "Atenção", "Informe a data da fila no formato AAAA-MM-DD."
            )
            return

        try:
            fila = (
                self._executar("agendamento", "listar_fila_atendimento", data_str) or []
            )
            for item in self.tabela.get_children():
                self.tabela.delete(item)

            for ag in fila:
                horario = self._normalizar_hora(self._campo(ag, "horario", ""))
                cliente = self._campo(ag, "cliente", "")
                servico = self._campo(ag, "servico", "")
                barbeiro = self._campo(ag, "barbeiro", "")
                self.tabela.insert(
                    "", "end", values=(horario, cliente, servico, barbeiro)
                )
        except Exception as erro:
            messagebox.showerror("Erro ao carregar fila", str(erro))

    def _limpar_formulario(self):
        self.entry_data.delete(0, "end")
        self.entry_data.insert(0, date.today().isoformat())
        self.option_pagamento.set("APOS_CORTE")
        self.entry_observacao.delete(0, "end")
        self.atualizar_horarios_livres()

    def _agendar(self):
        cliente_id = self._mapa_clientes.get(self.option_cliente.get())
        barbeiro_id = self._mapa_barbeiros.get(self.option_barbeiro.get())
        servico_id = self._mapa_servicos.get(self.option_servico.get())
        data_str = self.entry_data.get().strip()
        horario = self.option_horario.get()
        pagamento = self.option_pagamento.get()
        obs_texto = self.entry_observacao.get().strip()
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
            self._executar(
                "agendamento",
                "criar_agendamento",
                cliente_id,
                barbeiro_id,
                servico_id,
                data_str,
                horario,
                pagamento,
                observacao,
            )
            messagebox.showinfo("Sucesso", "Agendamento registrado com sucesso!")
            self.entry_data_fila.delete(0, "end")
            self.entry_data_fila.insert(0, data_str)
            self._limpar_formulario()
            self.carregar_fila()
        except ValueError as erro:
            messagebox.showwarning("Atenção", str(erro))
        except Exception as erro:
            messagebox.showerror("Erro no banco de dados", str(erro))