import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import customtkinter as ctk

from view.agendamento_view import criar_tela_agendamentos
from view.barbeiro_view import criar_tela_barbeiros
from view.cliente_view import criar_tela_clientes
from view.servico_view import criar_tela_servicos


def criar_janela_principal(controllers: dict | None = None):
    ctrls = controllers or {}

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.title("Barbearia")
    largura = 420
    altura = 780
    pos_x = (app.winfo_screenwidth() - largura) // 2
    pos_y = (app.winfo_screenheight() - altura) // 2
    app.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")
    app.minsize(380, 680)

    header = ctk.CTkFrame(app, height=50, corner_radius=0)
    header.pack(fill="x", side="top")

    titulo = ctk.CTkLabel(
        header,
        text="BARBEARIA — AGENDA",
        font=ctk.CTkFont(size=16, weight="bold"),
    )
    titulo.pack(pady=12)

    tabview = ctk.CTkTabview(app, corner_radius=8)
    tabview.pack(fill="both", expand=True, padx=8, pady=(4, 10))

    tab_agendamentos = tabview.add("Agenda")
    tab_clientes = tabview.add("Clientes")
    tab_barbeiros = tabview.add("Barbeiros")
    tab_servicos = tabview.add("Serviços")

    tela_agendamentos = criar_tela_agendamentos(
        tab_agendamentos,
        controllers=ctrls,
        controller=ctrls.get("agendamento"),
    )
    tela_agendamentos.pack(fill="both", expand=True)

    tela_clientes = criar_tela_clientes(
        tab_clientes, controller=ctrls.get("cliente")
    )
    tela_clientes.pack(fill="both", expand=True)

    tela_barbeiros = criar_tela_barbeiros(
        tab_barbeiros, controller=ctrls.get("barbeiro")
    )
    tela_barbeiros.pack(fill="both", expand=True)

    tela_servicos = criar_tela_servicos(
        tab_servicos, controller=ctrls.get("servico")
    )
    tela_servicos.pack(fill="both", expand=True)

    return app


if __name__ == "__main__":
    janela = criar_janela_principal()
    janela.mainloop()