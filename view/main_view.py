import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import customtkinter as ctk

from view.agendamento_view import AgendamentoView
from view.barbeiro_view import BarbeiroView
from view.cliente_view import ClienteView
from view.servico_view import ServicoView


class MainView(ctk.CTk):

    def __init__(self, controllers: dict | None = None):
        super().__init__()

        self.controllers = controllers or {}

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("Barbearia")
        largura = 420
        altura = 780
        pos_x = (self.winfo_screenwidth() - largura) // 2
        pos_y = (self.winfo_screenheight() - altura) // 2
        self.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")
        self.minsize(380, 680)

        self._construir_layout()

    def _construir_layout(self):
        header = ctk.CTkFrame(self, height=50, corner_radius=0)
        header.pack(fill="x", side="top")

        titulo = ctk.CTkLabel(
            header,
            text="BARBEARIA — AGENDA",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        titulo.pack(pady=12)

        self.tabview = ctk.CTkTabview(self, corner_radius=8)
        self.tabview.pack(fill="both", expand=True, padx=8, pady=(4, 10))

        self.tab_agendamentos = self.tabview.add("Agenda")
        self.tab_clientes = self.tabview.add("Clientes")
        self.tab_barbeiros = self.tabview.add("Barbeiros")
        self.tab_servicos = self.tabview.add("Serviços")

        self.agendamento_view = AgendamentoView(
            self.tab_agendamentos,
            controllers=self.controllers,
            controller=self.controllers.get("agendamento"),
        )
        self.agendamento_view.pack(fill="both", expand=True)

        self.cliente_view = ClienteView(
            self.tab_clientes, controller=self.controllers.get("cliente")
        )
        self.cliente_view.pack(fill="both", expand=True)

        self.barbeiro_view = BarbeiroView(
            self.tab_barbeiros, controller=self.controllers.get("barbeiro")
        )
        self.barbeiro_view.pack(fill="both", expand=True)

        self.servico_view = ServicoView(
            self.tab_servicos, controller=self.controllers.get("servico")
        )
        self.servico_view.pack(fill="both", expand=True)


if __name__ == "__main__":
    app = MainView()
    app.mainloop()