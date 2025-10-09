import customtkinter as ctk
import utils_estoque as utils
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from system.ui_components import make_label, pad_values, Toast

class FormsMixin:    
    def on_add_ok(self):
        
        nf = self.entry_nf.get().strip()
        nf = str(nf).lstrip('0')
        
        if not nf:
            messagebox.showwarning("Aviso", "Preencha o campo Nº NF.")
            return
        
        fornecedor = self.supplier_var.get()
        conferente = self.conferente_var.get()
        
        if not fornecedor or not conferente:
            messagebox.showwarning("Aviso", "Selecione fornecedor e conferente.")
            return
        
        data_chegada = self.date_var.get().strip() or utils.today_br()
        data_emissao = self.date_emissao_var.get().strip() or ""
        
        max_length = 10
        if len(data_chegada) > max_length or (len(data_emissao) > max_length and data_emissao):
            messagebox.showwarning("Aviso", f"A data não pode ter mais que {max_length} caracteres.")
            return
        try:
            datetime.strptime(data_chegada, "%d-%m-%Y")
        except Exception:
            messagebox.showwarning("Aviso", "Data inválida. Use DD-MM-YYYY.")
            return
        
        cnpj = self.cnpj_var.get()

        suppliers = utils.load_suppliers()
        s = next((x for x in suppliers if x["name"] == fornecedor), {"id": None, "name": fornecedor})
        conferentes = utils.load_conferentes()
        c = next((x for x in conferentes if x["name"] == conferente), {"id": None, "name": conferente})

        note = {
            "nf_number": nf,
            "fornecedor_id": s.get("id"),
            "fornecedor_name": s.get("name"),
            "data_chegada": data_chegada,
            "data_emissao": data_emissao,
            "cnpj": cnpj,
            "conferente_id": c.get("id"),
            "conferente_name": c.get("name"),
            "created_at": datetime.now().isoformat(),
            "conferido": False,
            "conferido_por": None,
            "conferido_em": None
        }

        notes = utils.load_notes()
        nf_number = nf.strip()
        
        # verifica duplicata
        if any(n.get("nf_number") == nf_number for n in notes):
            messagebox.showwarning("Duplicado", f"A nota {nf_number} já existe!")
            return

        # utils.save_note should append; if a note with same NF exists, utils module should handle update.
        utils.save_note(note)
        self.refresh_table()
        messagebox.showinfo("Sucesso", "Nota salva com sucesso.")
        utils.update_note(c["id"], {"conferido": True, "modified_by": self.user["name"]})
        Toast(self.root, f"Nota {nf['nf_number']} adicionada por {nf.get('modified_by', 'Desconhecido')}")
        self.show_page("home")

    def action_close_form(self):
        # If the user has disabled ask_on_close, just go home
        if not self.settings.get("ask_on_close", True):
            self.show_page("home")
            return

        # prevent opening multiple dialogs
        if hasattr(self, "_confirm_dialog") and self._confirm_dialog.winfo_exists():
            return

        dialog = ctk.CTkToplevel(self.root)
        dialog.resizable(False, False)
        self._confirm_dialog = dialog
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.title("Confirmar")
        dialog.geometry(self.center_geometry(360, 160))

        make_label(dialog, "Tem certeza que deseja cancelar?").pack(pady=(12, 6), padx=12)
        dont_var = tk.BooleanVar(value=False)
        cb = ctk.CTkCheckBox(dialog, text="Não me pergunte novamente", variable=dont_var)
        cb.pack()

        btn_frame = ctk.CTkFrame(dialog)
        btn_frame.pack(pady=10)

        def on_yes():
            if dont_var.get():
                self.settings["ask_on_close"] = False
                utils.save_settings(self.settings)
            dialog.destroy()
            self.show_page("home")

        def on_no():
            dialog.destroy()

        ctk.CTkButton(btn_frame, text="Sim", command=on_yes).pack(side="left", padx=6)
        ctk.CTkButton(btn_frame, text="Não", command=on_no).pack(side="left", padx=6)
  
    def _validate_nf(self, newval):
        # allow only digits (1-9), dot and dash and empty
        if newval == "":
            return True
        for ch in newval:
            if not (ch.isdigit() or ch in ".-"):
                return False
        return True

    def _build_add_form(self, parent):
           make_label(parent, "Nº NF:").pack(anchor="center", padx=6, pady=(8, 0))
           vcmd = (parent.register(self._validate_nf), "%P")
           self.entry_nf = ctk.CTkEntry(
               parent, validate="key", 
               validatecommand=vcmd, 
               text_color="white", 
               justify="center",
               width=150
           )
           self.entry_nf.pack(fill="x", padx=6, pady=4)

           make_label(parent, "Fornecedor:").pack(anchor="center", padx=6, pady=(8, 0))
           self.supplier_var = ctk.StringVar()
           self.combobox_supplier = ctk.CTkComboBox(
               parent,
               values=pad_values(self._supplier_names()),
               variable=self.supplier_var,
               text_color="white",
               justify="center",
               state="readonly",
               width=150
           )
           self.combobox_supplier.pack(fill="x", padx=6, pady=4)

           # ---------------- Data ----------------
           make_label(parent, "Data de Chegada:").pack(anchor="center", padx=6, pady=(8, 0))
           self.date_var = ctk.StringVar(value=utils.today_br())  # <-- dd-mm-yyyy
           self.entry_date = ctk.CTkEntry(
               parent, 
               textvariable=self.date_var, 
               text_color="white", 
               justify="center",
               width=150
           )
           self.entry_date.pack(fill="x", padx=6, pady=4)

           #----------------- Data de Emissão ----------------
           make_label(parent, "Data de Emissão:").pack(anchor="center", padx=6, pady=(8, 0))
           self.date_emissao_var = ctk.StringVar(value="")  # <-- dd-mm-yyyy
           self.entry_date_emissao = ctk.CTkEntry(
               parent, 
               textvariable=self.date_emissao_var, 
               text_color="white", 
               justify="center",
               width=150
           )
           self.entry_date_emissao.pack(fill="x", padx=6, pady=4)

           # ---------------- CNPJ ----------------
           make_label(parent, "CNPJ:").pack(anchor="center", padx=6, pady=(8, 0))
           self.cnpj_var = ctk.StringVar(value="")
           self.combo_cnpj = ctk.CTkComboBox(
               parent, 
               values=["EH", "MVA"], 
               variable=self.cnpj_var, 
               text_color="white", 
               justify="center", 
               state="readonly",
               width=150
           )
           self.combo_cnpj.pack(fill="x", padx=6, pady=4)

           # ---------------- Conferente ----------------
           make_label(parent, "Recebida por:").pack(anchor="center", padx=6, pady=(8, 0))
           self.conferente_var = ctk.StringVar()
           self.combo_conferente = ctk.CTkComboBox(
               parent, 
               values=pad_values(self._conferente_names()),
               variable=self.conferente_var, 
               text_color="white", 
               justify="center", 
               state="readonly",
               width=150
           )
           self.combo_conferente.pack(fill="x", padx=6, pady=4, anchor="center")

           btns = ctk.CTkFrame(parent)
           btns.pack(fill="x", padx=6, pady=10)
           self.btn_ok = ctk.CTkButton(btns, text="Adicionar Nota", command=self.on_add_ok)
           self.btn_ok.pack(expand=True, fill="x", padx=4, pady=4)
           self.btn_cancel_form = ctk.CTkButton(btns, text="Cancelar", command=self.action_close_form)
           self.btn_cancel_form.pack(expand=True, fill="x", padx=4, pady=4)