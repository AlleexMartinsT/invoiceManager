import utils_estoque as utils
import customtkinter as ctk
from system.ui_components import make_label
from tkinter import messagebox

class ConferentesMixin:       
    def _build_manage_conferentes(self, parent):
        make_label(parent, "Conferentes", font=("Segoe UI", 15, "bold")).pack(anchor="center", padx=6, pady=(6, 4))
        self.conf_box = ctk.CTkTextbox(parent, height=200, width=150, state="disabled", text_color="white")
        self.conf_box.pack(fill="both", expand=False, padx=6, pady=6)

        self.conf_name_entry = ctk.CTkEntry(parent, placeholder_text="Digite o conferente", justify="center", fg_color="white")
        self.conf_name_entry.pack(fill="x", padx=6, pady=(0,4))

        frame_btns = ctk.CTkFrame(parent)
        frame_btns.pack(fill="x", padx=6, pady=6)
        ctk.CTkButton(frame_btns, text="Adicionar", command=self.add_conferente).pack(expand=True, fill="x", padx=4, pady=4)
        ctk.CTkButton(frame_btns, text="Remover", command=self.remove_conferente).pack(expand=True, fill="x", padx=4, pady=4)

        self.refresh_conferentes_listbox()

    def refresh_conferentes_listbox(self):
        self.conf_box.configure(state="normal")
        self.conf_box.delete("1.0", "end")
        conferentes = utils.load_conferentes()
        try:
            utils.reindex_conferentes()
            conferentes = utils.load_conferentes()
        except Exception:
            pass
        for c in conferentes:
            self.conf_box.insert("end", f'{c["name"]}\n')
        self.conf_box.configure(state="disabled")

    def add_conferente(self):
        name = self.conf_name_entry.get().strip()
        if not name:
            messagebox.showwarning("Aviso", "Digite o nome do conferente.")
            return
        utils.add_conferente(name)
        self.conf_name_entry.delete(0, "end")
        self.refresh_conferentes_listbox()
        self.combo_conferente.configure(values=self._conferente_names())
        self.filter_conferente_cb.configure(values=["Todos"] + self._conferente_names())

    def remove_conferente(self):
        conferentes = utils.load_conferentes()
        if not conferentes:
            messagebox.showinfo("Info", "Nenhum conferente cadastrado.")
            return

        dialog = ctk.CTkToplevel(self.root)
        dialog.resizable(False, False)
        dialog.title("Remover Conferente")
        dialog.geometry(self.center_geometry(360, 140))
        dialog.grab_set()

        make_label(dialog, "Selecione o conferente para remover:").pack(pady=(10, 5))

        var = ctk.StringVar(value="")
        combo = ctk.CTkComboBox(dialog, values=[f'{c["name"]}' for c in conferentes],
                                          variable=var, state="readonly", width=150)
        combo.pack(pady=10)

        def confirm_remove():
            val = var.get()
            if not val:
                return
            cid = int(val.split(" - ", 1)[0])
            utils.remove_conferente(cid)
            try:
                utils.reindex_conferentes()
            except Exception:
                pass
            self.refresh_conferentes_listbox()
            self.combo_conferente.configure(values=self._conferente_names())
            self.filter_conferente_cb.configure(values=["Todos"] + self._conferente_names())
            dialog.destroy()
            messagebox.showinfo("Sucesso", "Conferente removido com sucesso.")

        ctk.CTkButton(dialog, text="Remover", command=confirm_remove).pack(pady=6)
 