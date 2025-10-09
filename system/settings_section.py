import customtkinter as ctk
import utils_estoque as utils
import tkinter as tk
from system.ui_components import make_label

class SettingsMixin:
    def _build_settings_page(self, parent):
        make_label(parent, "Configurações", font=("Segoe UI", 15, "bold")).pack(pady=(10, 6))
        self.var_all_months = tk.BooleanVar(value=self.settings.get("visualizar_todos_meses", False))
        cb = ctk.CTkCheckBox(
            parent,
            text="Visualizar todos os meses deste ano",
            text_color="white",
            variable=self.var_all_months,
            command=self._toggle_all_months
        )
        cb.pack(anchor="w", padx=12, pady=6)
        ctk.CTkButton(parent, text="Voltar", command=lambda: self.show_page("home")).pack(pady=20)

    def _toggle_all_months(self):
        self.settings["visualizar_todos_meses"] = self.var_all_months.get()
        utils.save_settings(self.settings)
        self.refresh_table()
    
    def show_settings_page(self):
        # cria nova janela
        win = ctk.CTkToplevel(self.root)
        win.title("Configurações")
        win.geometry(self.center_geometry(350,200))  # largura x altura, ajuste como quiser
        win.grab_set()  # bloqueia interação com a janela principal até fechar
        win.focus()

        make_label(win, "Configurações", font=("Segoe UI", 15, "bold")).pack(pady=(10, 6))

        self.var_all_months = tk.BooleanVar(value=self.settings.get("visualizar_todos_meses", False))
        cb = ctk.CTkCheckBox(
            win,
            text="Visualizar todos os meses deste ano",
            variable=self.var_all_months,
            command=self._toggle_all_months,
            text_color="white"
        )
        cb.pack(anchor="center", padx=12, pady=6)

        ctk.CTkButton(win, text="Fechar", command=win.destroy).pack(pady=20)
