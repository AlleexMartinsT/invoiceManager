import customtkinter as ctk
import utils_estoque as utils
from system.ui_components import make_label
from tkinter import messagebox

class SuppliersMixin:
    def _build_manage_suppliers(self, parent):
        make_label(parent, "Fornecedores", font=("Segoe UI", 15, "bold")).pack(anchor="center", padx=6, pady=(6, 4))

        self.suppliers_box = ctk.CTkTextbox(parent, height=200, width=150, state="disabled", text_color="white")
        self.suppliers_box.pack(fill="both", expand=False, padx=6, pady=6)
        self.supplier_name_entry = ctk.CTkEntry(parent, placeholder_text="Digite o fornecedor", justify="center", fg_color="white")
        self.supplier_name_entry.pack(fill="x", padx=6, pady=(0,4))
        frame_btns = ctk.CTkFrame(parent)
        frame_btns.pack(fill="x", padx=6, pady=6)
        ctk.CTkButton(frame_btns, text="Adicionar", command=self.add_supplier).pack(expand=True, fill="x", padx=4, pady=4)
        ctk.CTkButton(frame_btns, text="Remover", command=self.remove_supplier).pack(expand=True, fill="x", padx=4, pady=4)
        self.refresh_suppliers_listbox()

    def refresh_suppliers_listbox(self):
        self.suppliers_box.configure(state="normal")
        self.suppliers_box.delete("1.0", "end")
        suppliers = utils.load_suppliers()
        # reindex IDs sequentially for display (if utility available try to call utils.reindex_suppliers)
        try:
            utils.reindex_suppliers()
            suppliers = utils.load_suppliers()
        except Exception:
            # if not available, just display as-is; user asked numbering isn't critical
            pass
        for s in suppliers:
            self.suppliers_box.insert("end", f'{s["name"]}\n')
        self.suppliers_box.configure(state="disabled")

    def add_supplier(self):
        name = self.supplier_name_entry.get().strip()
        if not name:
            messagebox.showwarning("Aviso", "Digite o nome do fornecedor.")
            return
        utils.add_supplier(name)
        self.supplier_name_entry.delete(0, "end")
        self.refresh_suppliers_listbox()
        self.combobox_supplier.configure(values=self._supplier_names())
        self.filter_fornecedor_cb.configure(values=["Todas"] + self._supplier_names())

    def remove_supplier(self):
        suppliers = utils.load_suppliers()
        if not suppliers:
            messagebox.showinfo("Info", "Nenhum fornecedor cadastrado.")
            return

        dialog = ctk.CTkToplevel(self.root)
        dialog.resizable(False, False)
        dialog.title("Remover Fornecedor")
        dialog.geometry(self.center_geometry(360, 140))
        dialog.grab_set()

        make_label(dialog, "Selecione o fornecedor:").pack(pady=(10, 5))

        var = ctk.StringVar(value="")
        combo = ctk.CTkComboBox(dialog, values=[f'{s["name"]}' for s in suppliers],
                                          variable=var, state="readonly", width=150, justify="center", height=150)
        combo.pack(pady=10)

        def confirm_remove():
            val = var.get()
            if not val:
                return
            sid = int(val.split(" - ", 1)[0])
            utils.remove_supplier(sid)
            # try to reindex to close gaps
            try:
                utils.reindex_suppliers()
            except Exception:
                pass
            self.refresh_suppliers_listbox()
            self.combobox_supplier.configure(values=self._supplier_names())
            self.filter_fornecedor_cb.configure(values=["Todas"] + self._supplier_names())
            dialog.destroy()
            messagebox.showinfo("Sucesso", "Fornecedor removido com sucesso.")

        ctk.CTkButton(dialog, text="Remover", command=confirm_remove).pack(pady=6)
