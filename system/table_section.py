import customtkinter as ctk
import tkinter as tk
import utils_estoque as utils
from tkinter import ttk, messagebox
from datetime import datetime
from system.ui_components import Toast, make_label

class TableMixin: 
    def _build_table(self):

        cols = ("nf", "data", "fornecedor", "conferente", "cnpj", "conferido")
        headings = {
            "nf": "Nota Fiscal",
            "data": "Data de Chegada",
            "fornecedor": "Fornecedor",
            "conferente": "Recebida por",
            "cnpj": "CNPJ",
            "conferido": "Conferência"
        }
        
        # Treeview (wrapped in CTk Frame to control sizing easily)
        container = ctk.CTkFrame(self.main_frame)
        container.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(container, columns=cols, show="headings", height=12)
        
        self.tooltip = None
        self.tree.bind("<Motion>", self._on_motion)
        self.tree.bind("<Leave>", lambda e: self._hide_tooltip())
        
        for c in cols:
            self.tree.heading(c, text=headings[c], command=lambda _c=c: self._sort_by_column(_c, False))
            self.tree.column(c, width=130, anchor="center", minwidth=80, stretch=True)

        self.tree.pack(fill="both", expand=True, side="left")
        
        vsb = ctk.CTkScrollbar(container, command=self.tree.yview)
        self.tree.configure(yscroll=vsb.set)
        vsb.pack(side="right", fill="y")

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#1e1e1e", foreground="white", fieldbackground="#1e1e1e", rowheight=26, padding=0, font=("Segoe UI", 10, ))
        style.configure("Treeview.Heading", background="#2d2d2d", foreground="orange", font=("Segoe UI", 11, "bold"))
        
        # right-click menu on rows
        self.tree.bind("<Button-3>", self._on_tree_right_click)
        # double click to edit
        self.tree.bind("<Double-Button-1>", self._on_tree_double_click)

    def _populate_table(self, notes):
        """Limpa e popula a tabela com a lista de notas."""
        for it in self.tree.get_children():
            self.tree.delete(it)

        for n in notes:
            data_display = n.get("data_chegada") or n.get("created_at", "")[:10]
            try:
                d = datetime.strptime(data_display, "%Y-%m-%d")
                data_display = d.strftime("%d-%m-%Y")
            except Exception:
                pass

            conferido_display = "✔" if n.get("conferido", False) else ""
            self.tree.insert(
                "",
                "end",
                values=(
                    n.get("nf_number"),
                    data_display,
                    n.get("fornecedor_name"),
                    n.get("conferente_name"),
                    n.get("cnpj"),
                    conferido_display
                )
            )

        self.update_recent_list()

    def _sort_by_column(self, col, reverse):
        # get all rows data
        data = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        def try_cast(v):
            # try date dd-mm-yyyy, numbers etc
            try:
                return datetime.strptime(v, "%d-%m-%Y")
            except Exception:
                try:
                    return float(v.replace(".", "").replace(",", "."))
                except Exception:
                    return v.lower()
        data.sort(key=lambda t: try_cast(t[0]), reverse=reverse)
        for index, (val, k) in enumerate(data):
            self.tree.move(k, '', index)
        # reverse next time
        self.tree.heading(col, command=lambda: self._sort_by_column(col, not reverse))
    
    def refresh_table(self):
        for it in self.tree.get_children():
            self.tree.delete(it)

        notes = utils.load_notes()
        notes = self._apply_filters(notes)
        # >>> FILTRO DO MÊS ATUAL <<<
        if not self.settings.get("visualizar_todos_meses", False):
            mes_atual = datetime.now().month
            ano_atual = datetime.now().year
            notes = [
                n for n in notes
                if n.get("data_chegada")
                and datetime.strptime(n["data_chegada"], "%d-%m-%Y").month == mes_atual
                and datetime.strptime(n["data_chegada"], "%d-%m-%Y").year == ano_atual
            ]
        self._populate_table(notes)
        self.update_recent_list()
        self._update_conferente_counter()

    def _update_conferente_counter(self):
        """Atualiza o contador de notas conferidas respeitando os filtros aplicados."""
        notes = utils.load_notes()
        notes = self._apply_filters(notes)

        # Filtro do mês (mesmo que refresh_table)
        if not self.settings.get("visualizar_todos_meses", False):
            mes_atual = datetime.now().month
            ano_atual = datetime.now().year
            notes = [
                n for n in notes
                if n.get("data_chegada")
                and datetime.strptime(n["data_chegada"], "%d-%m-%Y").month == mes_atual
                and datetime.strptime(n["data_chegada"], "%d-%m-%Y").year == ano_atual
            ]

        # Considera apenas notas conferidas
        conferidas = [n for n in notes if n.get("conferido", False)]

        # Contagem por conferente
        contagem = {}
        for n in conferidas:
            nome = n.get("conferido_por") or n.get("conferente_name") or "Desconhecido"
            contagem[nome] = contagem.get(nome, 0) + 1

        if not contagem:
            texto = "Nenhuma nota conferida dentro do filtro atual."
        else:
            linhas = [f"{nome}: {qtd} notas" for nome, qtd in sorted(contagem.items())]
            texto = "Notas conferidas (filtros aplicados):\n" + "\n".join(linhas)

        if hasattr(self, "label_contador"):
            self.label_contador.configure(text=texto)

    def _on_tree_right_click(self, event):
        # identify clicked row
        iid = self.tree.identify_row(event.y)
        if not iid:
            return
        self.tree.selection_set(iid)
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Material Conferido", command=lambda: self._mark_conferido(iid))
        menu.add_command(label="Editar linha", command=lambda: self._edit_line(iid))
        menu.add_command(label="Remover linha", command=lambda: self._remove_line(iid))
        menu.tk_popup(event.x_root, event.y_root)
    
    def _on_tree_double_click(self, event):
        iid = self.tree.identify_row(event.y)
        if iid:
            self._edit_line(iid)
    
    def _remove_line(self, iid):
        n = self._get_note_by_iid(iid)
        if not n:
            return
        if not messagebox.askyesno("Remover", f"Remover completamente a nota {n.get('nf_number')} ?"):
            return
        notes = utils.load_notes()
        new_notes = [x for x in notes if str(x.get("nf_number")) != str(n.get("nf_number"))]
        ok = self._save_notes_list(new_notes)
        if not ok:
            messagebox.showwarning("Aviso", "Não foi possível salvar automaticamente. Atualize utils_estoque.")
        self.refresh_table()
        messagebox.showinfo("Sucesso", "Nota removida.")
    
    def _mark_conferido(self, iid):
        n = self._get_note_by_iid(iid)
        if not n:
            return
        
        if n.get("conferido", False):
            if messagebox.askyesno("Desmarcar", f"A nota {n['nf_number']} já está conferida.\nDeseja desmarcar?"):
                utils.update_note(n["id"], {"conferido": False})
                messagebox.showinfo("Sucesso", "Nota desmarcada como conferida.")
                self.refresh_table()
                return
            else:
                return
                
        # dialog to choose conferente and date
        dialog = ctk.CTkToplevel(self.root)
        dialog.resizable(False, False)
        dialog.title("Marcar como conferido")
        dialog.geometry(self.center_geometry(360, 250))
        dialog.grab_set()

        make_label(dialog, f"Nota: {n.get('nf_number')}").pack(pady=(8,4), padx=8)
        conf_var = ctk.StringVar(value=n.get("conferido_por") or utils.load_conferentes()[0]["name"] if utils.load_conferentes() else "")
        combo = ctk.CTkComboBox(dialog, values=self._conferente_names(), variable=conf_var, state="readonly", width=150, justify='center')
        combo.pack(pady=6)
        make_label(dialog, f"Data de conferência:").pack(pady=(8,0), padx=8)
        date_var = ctk.StringVar(value=datetime.now().strftime("%d-%m-%Y"))
        date_entry = ctk.CTkEntry(dialog, textvariable=date_var, width=150, text_color="white", justify="center")
        date_entry.pack(pady=4)
        
        def do_mark():    
            chosen = conf_var.get()
            d = date_var.get()
            try:
                datetime.strptime(d, "%d-%m-%Y")
            except Exception:
                messagebox.showwarning("Aviso", "Data inválida. Use DD-MM-YYYY.")
                return
            # update note in memory
            notes = utils.load_notes()
            updated = False
            for item in notes:
                if str(item.get("nf_number")) == str(n.get("nf_number")):
                    item["conferido"] = True
                    item["conferido_por"] = chosen
                    item["conferido_em"] = d
                    updated = True
                    break
            if updated:
                ok = self._save_notes_list(notes)
                if not ok:
                    messagebox.showwarning("Aviso", "Não foi possível salvar automaticamente. Atualize seu utils_estoque com save_all_notes/notes_path para persistência.")
                self.refresh_table()
                dialog.destroy()
                messagebox.showinfo("Sucesso", "Marcado como conferido.")
                Toast(self.root, f"Nota {n['nf_number']} conferida!")
            else:
                messagebox.showerror("Erro", "Nota não encontrada.")

        ctk.CTkButton(dialog, text="Confirmar", command=do_mark).pack(pady=8)
        ctk.CTkButton(dialog, text="Cancelar", command=dialog.destroy).pack()
    
    def _edit_line(self, iid):
        n = self._get_note_by_iid(iid)
        if not n:
            return
        dialog = ctk.CTkToplevel(self.root)
        dialog.resizable(False, False)
        dialog.title("Editar Nota")
        dialog.geometry(self.center_geometry(320, 420))
        dialog.grab_set()

        make_label(dialog, "Nº NF:").pack(anchor="w", padx=8, pady=(8,0))
        nf_entry = ctk.CTkEntry(dialog, width=100, text_color="white", justify="center")
        nf_entry.insert(0, n.get("nf_number"))
        nf_entry.pack(fill="x", padx=8, pady=4)

        make_label(dialog, "Data de Chegada:").pack(anchor="w", padx=8, pady=(4,0))
        date_var = ctk.StringVar(value=n.get("data_chegada") or utils.today_br())
        date_entry = ctk.CTkEntry(dialog, textvariable=date_var, text_color="white", justify="center", width=100)
        date_entry.pack(fill="x", padx=8, pady=4)
        
        make_label(dialog, "Data de Emissão:").pack(anchor="w", padx=8, pady=(4,0))
        date_emissao_var = ctk.StringVar(value=n.get("data_emissao") or "")
        date_emissao_entry = ctk.CTkEntry(dialog, textvariable=date_emissao_var, text_color="white", justify="center", width=100)
        date_emissao_entry.pack(fill="x", padx=8, pady=4)

        make_label(dialog, "Fornecedor:").pack(anchor="w", padx=8, pady=(4,0))
        sup_var = ctk.StringVar(value=n.get("fornecedor_name"))
        sup_combo = ctk.CTkComboBox(dialog, values=self._supplier_names(), variable=sup_var, state="readonly", text_color="white", justify="center", width=100)
        sup_combo.pack(fill="x", padx=8, pady=4)

        make_label(dialog, "Conferente:").pack(anchor="w", padx=8, pady=(4,0))
        conf_var = ctk.StringVar(value=n.get("conferente_name"))
        conf_combo = ctk.CTkComboBox(dialog, values=self._conferente_names(), variable=conf_var, state="readonly", text_color="white", justify="center", width=100)
        conf_combo.pack(fill="x", padx=8, pady=4)

        def do_save_edit():
            nf_new = nf_entry.get().strip()
            d = date_var.get().strip()
            try:
                datetime.strptime(d, "%d-%m-%Y")
            except Exception:
                messagebox.showwarning("Aviso", "Data inválida. Use DD-MM-YYYY.")
                return
            notes = utils.load_notes()
            edited = False
            for item in notes:
                if str(item.get("nf_number")) == str(n.get("nf_number")):
                    item["nf_number"] = nf_new
                    item["data_chegada"] = d
                    item["data_emissao"] = date_emissao_var.get().strip()
                    item["fornecedor_name"] = sup_var.get()
                    item["conferente_name"] = conf_var.get()
                    edited = True
                    break
            if edited:
                ok = self._save_notes_list(notes)
                if not ok:
                    messagebox.showwarning("Aviso", "Não foi possível salvar automaticamente. Atualize utils_estoque.")
                self.refresh_table()
                dialog.destroy()
                messagebox.showinfo("Sucesso", "Nota atualizada.")
            else:
                messagebox.showerror("Erro", "Nota não encontrada.")

        ctk.CTkButton(dialog, text="Salvar", command=do_save_edit).pack(pady=8)
        ctk.CTkButton(dialog, text="Cancelar", command=dialog.destroy).pack()

