import customtkinter
from tkinter import ttk, messagebox
import tkinter as tk
import os
from datetime import datetime
import utils_estoque as utils

customtkinter.set_default_color_theme(os.path.join(os.path.dirname(__file__), "data", "basedTheme.json")
                                      if os.path.exists(os.path.join(os.path.dirname(__file__), "data", "basedTheme.json"))
                                      else None)
customtkinter.set_appearance_mode("dark")

def make_label(master, text, **kw):
    return customtkinter.CTkLabel(master, text=text, anchor="w", **kw)

class EstoqueApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Relatório do Estoque")
        self.root.geometry(self.center_geometry(1350, 800))
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # load state
        #self.settings = utils.load_settings()

        # Main layout: left filters, main area (table), right actions (which will be a frame that swaps content)
        self.left_frame = customtkinter.CTkFrame(root, width=200)
        self.left_frame.pack(side="left", fill="y", padx=8, pady=8)

        self.main_frame = customtkinter.CTkFrame(root)
        self.main_frame.pack(side="left", fill="both", expand=True, padx=8, pady=8)

        self.actions_frame = customtkinter.CTkFrame(root, width=300)
        self.actions_frame.pack(side="right", fill="x", padx=8, pady=8)

        # Build UI parts6
        self._build_filters()
        self._build_table()
        self._build_actions_stack()

        # Populate initial data
        self.refresh_table()
        self.update_recent_list()

        # Key bindings
        self.root.bind("<Escape>", self._handle_escape)
        self._setup_tooltip_support()

    def _handle_escape(self, event=None):
        current_page = [k for k, p in self.pages.items() if p.winfo_manager()]
        if current_page and current_page[0] != "home":
            if current_page[0] == "add_form":
                self.action_close_form()
            else:
                self.show_page("home")
        else:
            self.show_page("home")   # nunca fecha, sempre volta pro menu principal

    def center_geometry(self, w, h):
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        return f"{w}x{h}+{x}+{y}"

    # ---------------- Filters ----------------
    def _build_filters(self):
        make_label(self.left_frame, "Filtrar por:").pack(anchor="w", pady=(4, 6), padx=6)

        self.filter_vars = {"EH": tk.BooleanVar(value=True), "MVA": tk.BooleanVar(value=True)}
        cb_eh = customtkinter.CTkCheckBox(self.left_frame, text="Horizonte", variable=self.filter_vars["EH"],
                                         command=self.refresh_table, text_color="white")
        cb_mva = customtkinter.CTkCheckBox(self.left_frame, text="MVA", variable=self.filter_vars["MVA"],
                                          command=self.refresh_table, text_color="white")
        cb_eh.pack(anchor="w", padx=6, pady=2)
        cb_mva.pack(anchor="w", padx=6, pady=2)

        # filtros avançados: fornecedor / conferente / conferido status
        make_label(self.left_frame, "Fornecedor:").pack(anchor="w", padx=6, pady=(8, 0))
        self.filter_fornecedor_var = customtkinter.StringVar(value="Todas")
        self.filter_fornecedor_cb = customtkinter.CTkComboBox(self.left_frame, values=["Todas"] + self._supplier_names(),
                                                             variable=self.filter_fornecedor_var, state="readonly", justify="center")
        self.filter_fornecedor_cb.pack(fill="x", padx=6, pady=4)

        make_label(self.left_frame, "Conferente:").pack(anchor="w", padx=6, pady=(8, 0))
        self.filter_conferente_var = customtkinter.StringVar(value="Todos")
        self.filter_conferente_cb = customtkinter.CTkComboBox(self.left_frame, values=["Todos"] + self._conferente_names(),
                                                              variable=self.filter_conferente_var, state="readonly", justify="center")
        self.filter_conferente_cb.pack(fill="x", padx=6, pady=4)

        make_label(self.left_frame, "Status conferência:").pack(anchor="w", padx=6, pady=(8, 0))
        self.filter_conferido_var = tk.StringVar(value="Todas")
        self.combo_filtro_conferido = customtkinter.CTkComboBox(
            self.left_frame,
            values=["Todas", "Notas conferidas", "Notas não conferidas"],
            variable=self.filter_conferido_var,
            state="readonly",
            justify="center",
        )
        self.combo_filtro_conferido.pack(pady=4, padx=6, fill="x")


        # Filter buttons
        frame_filters = customtkinter.CTkFrame(self.left_frame)
        frame_filters.pack(fill="x", padx=6, pady=(10, 4))
        customtkinter.CTkButton(frame_filters, text="Aplicar filtros", command=self.refresh_table, hover_color="#2b81e2", fg_color="#4989d3").pack(expand=True, fill="x", padx=4, pady=4)
        customtkinter.CTkButton(frame_filters, text="Limpar filtros", command=self._clear_filters, hover_color="#2b81e2", fg_color="#4989d3").pack(expand=True, fill="x", padx=4, pady=4)
        
        # quick actions
        customtkinter.CTkButton(self.left_frame, text="Adicionar Nota", command=self.show_add_form).pack(pady=(12, 6), padx=6, fill="x")
        customtkinter.CTkButton(self.left_frame, text="Gerenciar Fornecedores", command=self.show_manage_suppliers).pack(pady=6, padx=6, fill="x")
        customtkinter.CTkButton(self.left_frame, text="Gerenciar Conferentes", command=self.show_manage_conferentes).pack(pady=6, padx=6, fill="x")
    
    def _clear_filters(self):
        self.filter_vars["EH"].set(True)
        self.filter_vars["MVA"].set(True)
        self.filter_fornecedor_var.set("Todas")
        self.filter_conferente_var.set("Todos")
        self.filter_conferido_var.set("Todas")
        self.refresh_table()
    
    # ---------------- Table ----------------
    def _build_table(self):
        cols = ("nf", "data", "fornecedor", "conferente", "cnpj", "conferido")
        headings = {
            "nf": "Nota Fiscal",
            "data": "Data",
            "fornecedor": "Fornecedor",
            "conferente": "Recebida por",
            "cnpj": "CNPJ",
            "conferido": "Conferência"
        }
        
        # Treeview (wrapped in CTk Frame to control sizing easily)
        container = customtkinter.CTkFrame(self.main_frame)
        container.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(container, columns=cols, show="headings", height=12)
        
        self.tooltip = None
        self.tree.bind("<Motion>", self._on_motion)
        self.tree.bind("<Leave>", lambda e: self._hide_tooltip())
        
        for c in cols:
            self.tree.heading(c, text=headings[c], command=lambda _c=c: self._sort_by_column(_c, False))
            self.tree.column(c, width=120, anchor="center", minwidth=80, stretch=True)

        self.tree.pack(fill="both", expand=True, side="left")
        
        vsb = customtkinter.CTkScrollbar(container, command=self.tree.yview)
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
        # repopulate tree from notes applying filters
        for it in self.tree.get_children():
            self.tree.delete(it)
        notes = utils.load_notes()  # list of dicts
        enabled_cnpjs = [k for k, v in self.filter_vars.items() if v.get()]

        filtro_fornecedor = self.filter_fornecedor_var.get()
        filtro_conferente = self.filter_conferente_var.get()
        filtro_conferido = self.filter_conferido_var.get()

        for n in notes:
            if n.get("cnpj") not in enabled_cnpjs:
                continue
            if filtro_fornecedor and filtro_fornecedor != "Todas" and n.get("fornecedor_name") != filtro_fornecedor:
                continue
            if filtro_conferente and filtro_conferente != "Todos" and n.get("conferente_name") != filtro_conferente:
                continue

            # --- filtro conferido (coluna 6) ---
            conferido_flag = n.get("conferido", False)
            if filtro_conferido == "Notas conferidas" and not conferido_flag:
                continue
            if filtro_conferido == "Notas não conferidas" and conferido_flag:
                continue

            data_display = n.get("data_chegada") or n.get("created_at", "")[:10]
            # convert data_display to DD-MM-YYYY for display if in ISO
            try:
                d = datetime.fromisoformat(data_display)
                data_display = d.strftime("%d-%m-%Y")
            except Exception:
                pass  # se já estiver no formato dd-mm-yyyy

            conferido_display = "✔" if conferido_flag else ""
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

    def _build_actions_stack(self):
        self.pages = {}

        # Top image present on all pages
        img_path = os.path.join(os.path.dirname(__file__), "data", "logo.png")
        if os.path.exists(img_path):
            try:
                from PIL import Image
                pil_img = Image.open(img_path)
                self.img_ref = customtkinter.CTkImage(pil_img, size=(200, 200))
                customtkinter.CTkLabel(self.actions_frame, image=self.img_ref, text="").pack(pady=8)
            except Exception:
                pass
        else:
            # small title if no image
            make_label(self.actions_frame, "Ações", font=("Segoe UI", 14, "bold")).pack(pady=8)
        
        # Container das páginas abaixo da imagem
        self.page_container = customtkinter.CTkFrame(self.actions_frame)
        self.page_container.pack(fill="both", expand=True)

        # Agora criamos as páginas dentro do container
        self.pages["home"] = customtkinter.CTkFrame(self.page_container)
        self.pages["add_form"] = customtkinter.CTkFrame(self.page_container)
        self.pages["manage_suppliers"] = customtkinter.CTkFrame(self.page_container)
        self.pages["manage_conferentes"] = customtkinter.CTkFrame(self.page_container)

        # construir conteúdos
        self._build_home(self.pages["home"])
        self._build_add_form(self.pages["add_form"])
        self._build_manage_suppliers(self.pages["manage_suppliers"])
        self._build_manage_conferentes(self.pages["manage_conferentes"])

        # Página inicial
        self.show_page("home")

    def _build_home(self, parent):
        self.recent_tree = ttk.Treeview(
            self.pages["home"],
            columns=("nf", "fornecedor", "cnpj", "conferente"),
            show="headings",
            height=6
        )

        # Cabeçalhos
        self.recent_tree.heading("nf", text="NF")
        self.recent_tree.heading("fornecedor", text="Fornecedor")
        self.recent_tree.heading("cnpj", text="CNPJ")
        self.recent_tree.heading("conferente", text="Conferente")

        # Larguras
        self.recent_tree.column("nf", width=80, anchor="center")
        self.recent_tree.column("fornecedor", width=120, anchor="center")
        self.recent_tree.column("cnpj", width=80, anchor="center")
        self.recent_tree.column("conferente", width=120, anchor="center")

        self.recent_tree.pack(fill="both", expand=True, padx=6, pady=6)

        customtkinter.CTkButton(parent, text="Atualizar tabela", command=self.refresh_table).pack(fill="x", padx=8, pady=6)

    # ---------------- Add form ----------------
    def _build_add_form(self, parent):
        make_label(parent, "Nº NF:").pack(anchor="center", padx=6, pady=(8, 0))
        vcmd = (parent.register(self._validate_nf), "%P")
        self.entry_nf = customtkinter.CTkEntry(
            parent, validate="key", 
            validatecommand=vcmd, 
            text_color="white", 
            justify="center",
            width=150
        )
        self.entry_nf.pack(fill="x", padx=6, pady=4)

        make_label(parent, "Fornecedor:").pack(anchor="center", padx=6, pady=(8, 0))
        self.supplier_var = customtkinter.StringVar()
        self.combobox_supplier = customtkinter.CTkComboBox(
            parent,
            values=self._supplier_names(),
            variable=self.supplier_var,
            text_color="white",
            justify="center",
            state="readonly",
            width=150
        )
        self.combobox_supplier.pack(fill="x", padx=6, pady=4)

        # ---------------- Data ----------------
        make_label(parent, "Data de Chegada:").pack(anchor="center", padx=6, pady=(8, 0))
        self.date_var = customtkinter.StringVar(value=utils.today_br())  # <-- dd-mm-yyyy
        self.entry_date = customtkinter.CTkEntry(
            parent, 
            textvariable=self.date_var, 
            text_color="white", 
            justify="center",
            width=150
        )
        self.entry_date.pack(fill="x", padx=6, pady=4)

        # ---------------- CNPJ ----------------
        make_label(parent, "CNPJ:").pack(anchor="center", padx=6, pady=(8, 0))
        self.cnpj_var = customtkinter.StringVar(value="")
        self.combo_cnpj = customtkinter.CTkComboBox(
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
        self.conferente_var = customtkinter.StringVar()
        self.combo_conferente = customtkinter.CTkComboBox(
            parent, 
            values=self._conferente_names(),
            variable=self.conferente_var, 
            text_color="white", 
            justify="center", 
            state="readonly",
            width=150
        )
        self.combo_conferente.pack(fill="x", padx=6, pady=4, anchor="center")
        
        btns = customtkinter.CTkFrame(parent)
        btns.pack(fill="x", padx=6, pady=10)
        self.btn_ok = customtkinter.CTkButton(btns, text="Adicionar Nota", command=self.on_add_ok)
        self.btn_ok.pack(expand=True, fill="x", padx=4, pady=4)
        self.btn_cancel_form = customtkinter.CTkButton(btns, text="Cancelar", command=self.action_close_form)
        self.btn_cancel_form.pack(expand=True, fill="x", padx=4, pady=4)

    def _validate_nf(self, newval):
        # allow only digits (1-9), dot and dash and empty
        if newval == "":
            return True
        for ch in newval:
            if not (ch.isdigit() or ch in ".-"):
                return False
        return True

    def _supplier_names(self):
        suppliers = utils.load_suppliers()
        return [s["name"] for s in suppliers]

    def _conferente_names(self):
        conferentes = utils.load_conferentes()
        return [c["name"] for c in conferentes]

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
            "cnpj": cnpj,
            "conferente_id": c.get("id"),
            "conferente_name": c.get("name"),
            "created_at": datetime.now().isoformat(),
            "conferido": False,
            "conferido_por": None,
            "conferido_em": None
        }

        # utils.save_note should append; if a note with same NF exists, utils module should handle update.
        utils.save_note(note)
        self.refresh_table()
        messagebox.showinfo("Sucesso", "Nota salva com sucesso.")
        self.show_page("home")

    def action_close_form(self):
        # If the user has disabled ask_on_close, just go home
        if not self.settings.get("ask_on_close", True):
            self.show_page("home")
            return

        # prevent opening multiple dialogs
        if hasattr(self, "_confirm_dialog") and self._confirm_dialog.winfo_exists():
            return

        dialog = customtkinter.CTkToplevel(self.root)
        dialog.resizable(False, False)
        self._confirm_dialog = dialog
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.title("Confirmar")
        dialog.geometry(self.center_geometry(360, 160))

        make_label(dialog, "Tem certeza que deseja cancelar?").pack(pady=(12, 6), padx=12)
        dont_var = tk.BooleanVar(value=False)
        cb = customtkinter.CTkCheckBox(dialog, text="Não me pergunte novamente", variable=dont_var)
        cb.pack()

        btn_frame = customtkinter.CTkFrame(dialog)
        btn_frame.pack(pady=10)

        def on_yes():
            if dont_var.get():
                self.settings["ask_on_close"] = False
                utils.save_settings(self.settings)
            dialog.destroy()
            self.show_page("home")

        def on_no():
            dialog.destroy()

        customtkinter.CTkButton(btn_frame, text="Sim", command=on_yes).pack(side="left", padx=6)
        customtkinter.CTkButton(btn_frame, text="Não", command=on_no).pack(side="left", padx=6)
        
    # ---------------- Manage suppliers ----------------
    def _build_manage_suppliers(self, parent):
        make_label(parent, "Fornecedores", font=("Segoe UI", 15, "bold")).pack(anchor="center", padx=6, pady=(6, 4))
        
        self.suppliers_box = customtkinter.CTkTextbox(parent, height=200, width=150, state="disabled", text_color="white")
        self.suppliers_box.pack(fill="both", expand=False, padx=6, pady=6)

        self.supplier_name_entry = customtkinter.CTkEntry(parent, placeholder_text="Digite o fornecedor", justify="center", fg_color="white")
        self.supplier_name_entry.pack(fill="x", padx=6, pady=(0,4))

        frame_btns = customtkinter.CTkFrame(parent)
        frame_btns.pack(fill="x", padx=6, pady=6)
        customtkinter.CTkButton(frame_btns, text="Adicionar", command=self.add_supplier).pack(expand=True, fill="x", padx=4, pady=4)
        customtkinter.CTkButton(frame_btns, text="Remover", command=self.remove_supplier).pack(expand=True, fill="x", padx=4, pady=4)

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

        dialog = customtkinter.CTkToplevel(self.root)
        dialog.resizable(False, False)
        dialog.title("Remover Fornecedor")
        dialog.geometry("360x140")
        dialog.grab_set()

        make_label(dialog, "Selecione o fornecedor:").pack(pady=(10, 5))

        var = customtkinter.StringVar(value="")
        combo = customtkinter.CTkComboBox(dialog, values=[f'{s["id"]} - {s["name"]}' for s in suppliers],
                                          variable=var, state="readonly", width=150, justify="center")
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

        customtkinter.CTkButton(dialog, text="Remover", command=confirm_remove).pack(pady=6)

    # ---------------- Manage conferentes ----------------
    
    def _build_manage_conferentes(self, parent):
        make_label(parent, "Conferentes", font=("Segoe UI", 15, "bold")).pack(anchor="center", padx=6, pady=(6, 4))
        self.conf_box = customtkinter.CTkTextbox(parent, height=200, width=150, state="disabled", text_color="white")
        self.conf_box.pack(fill="both", expand=False, padx=6, pady=6)

        self.conf_name_entry = customtkinter.CTkEntry(parent, placeholder_text="Digite o conferente", justify="center", fg_color="white")
        self.conf_name_entry.pack(fill="x", padx=6, pady=(0,4))

        frame_btns = customtkinter.CTkFrame(parent)
        frame_btns.pack(fill="x", padx=6, pady=6)
        customtkinter.CTkButton(frame_btns, text="Adicionar", command=self.add_conferente).pack(expand=True, fill="x", padx=4, pady=4)
        customtkinter.CTkButton(frame_btns, text="Remover", command=self.remove_conferente).pack(expand=True, fill="x", padx=4, pady=4)

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

        dialog = customtkinter.CTkToplevel(self.root)
        dialog.resizable(False, False)
        dialog.title("Remover Conferente")
        dialog.geometry("360x140")
        dialog.grab_set()

        make_label(dialog, "Selecione o conferente para remover:").pack(pady=(10, 5))

        var = customtkinter.StringVar(value="")
        combo = customtkinter.CTkComboBox(dialog, values=[f'{c["id"]} - {c["name"]}' for c in conferentes],
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

        customtkinter.CTkButton(dialog, text="Remover", command=confirm_remove).pack(pady=6)
    
    # ---------------- Tree context menu and actions ----------------
    
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
    
    def _get_note_by_iid(self, iid):
        vals = self.tree.item(iid)["values"]
        if not vals:
            return None
        nf = vals[0]
        notes = utils.load_notes()
        for n in notes:
            if str(n.get("nf_number")) == str(nf):
                return n
        return None
    
    def _save_notes_list(self, notes):
        # Try convenient functions on utils; fallback to generic save_all if present
        if hasattr(utils, "save_all_notes"):
            utils.save_all_notes(notes)
            return True
        # fallback: if utils exposes notes_path, write JSON directly
        if hasattr(utils, "notes_path"):
            import json
            with open(utils.notes_path(), "w", encoding="utf-8") as f:
                json.dump(notes, f, ensure_ascii=False, indent=2)
            return True
        # otherwise we can't persist
        return False
    
    def _mark_conferido(self, iid):
        n = self._get_note_by_iid(iid)
        if not n:
            return
        # dialog to choose conferente and date
        dialog = customtkinter.CTkToplevel(self.root)
        dialog.resizable(False, False)
        dialog.title("Marcar como conferido")
        dialog.geometry("360x250")
        dialog.grab_set()

        make_label(dialog, f"Nota: {n.get('nf_number')}").pack(pady=(8,4), padx=8)
        conf_var = customtkinter.StringVar(value=n.get("conferido_por") or utils.load_conferentes()[0]["name"] if utils.load_conferentes() else "")
        combo = customtkinter.CTkComboBox(dialog, values=self._conferente_names(), variable=conf_var, state="readonly", width=150, justify='center')
        combo.pack(pady=6)
        make_label(dialog, f"Data de conferência:").pack(pady=(8,0), padx=8)
        date_var = customtkinter.StringVar(value=datetime.now().strftime("%d-%m-%Y"))
        date_entry = customtkinter.CTkEntry(dialog, textvariable=date_var, width=150, text_color="white", justify="center")
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
            else:
                messagebox.showerror("Erro", "Nota não encontrada.")

        customtkinter.CTkButton(dialog, text="Confirmar", command=do_mark).pack(pady=8)
        customtkinter.CTkButton(dialog, text="Cancelar", command=dialog.destroy).pack()
    
    def _edit_line(self, iid):
        n = self._get_note_by_iid(iid)
        if not n:
            return
        dialog = customtkinter.CTkToplevel(self.root)
        dialog.resizable(False, False)
        dialog.title("Editar Nota")
        dialog.geometry("320x360")
        dialog.grab_set()

        make_label(dialog, "Nº NF:").pack(anchor="w", padx=8, pady=(8,0))
        nf_entry = customtkinter.CTkEntry(dialog, width=100, text_color="white", justify="center")
        nf_entry.insert(0, n.get("nf_number"))
        nf_entry.pack(fill="x", padx=8, pady=4)

        make_label(dialog, "Data de Chegada:").pack(anchor="w", padx=8, pady=(4,0))
        date_var = customtkinter.StringVar(value=n.get("data_chegada") or utils.today_br())
        date_entry = customtkinter.CTkEntry(dialog, textvariable=date_var, text_color="white", justify="center", width=100)
        date_entry.pack(fill="x", padx=8, pady=4)

        make_label(dialog, "Fornecedor:").pack(anchor="w", padx=8, pady=(4,0))
        sup_var = customtkinter.StringVar(value=n.get("fornecedor_name"))
        sup_combo = customtkinter.CTkComboBox(dialog, values=self._supplier_names(), variable=sup_var, state="readonly", text_color="white", justify="center", width=100)
        sup_combo.pack(fill="x", padx=8, pady=4)

        make_label(dialog, "Conferente:").pack(anchor="w", padx=8, pady=(4,0))
        conf_var = customtkinter.StringVar(value=n.get("conferente_name"))
        conf_combo = customtkinter.CTkComboBox(dialog, values=self._conferente_names(), variable=conf_var, state="readonly", text_color="white", justify="center", width=100)
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

        customtkinter.CTkButton(dialog, text="Salvar", command=do_save_edit).pack(pady=8)
        customtkinter.CTkButton(dialog, text="Cancelar", command=dialog.destroy).pack()
    
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
    
    # ---------------- Helpers ----------------
    
    def show_add_form(self):
        # refresh supplier/conferente values before show
        self.combobox_supplier.configure(values=self._supplier_names())
        self.combo_conferente.configure(values=self._conferente_names())
        self.date_var.set(utils.today_br())
        self.show_page("add_form")

    def show_manage_suppliers(self):
        self.refresh_suppliers_listbox()
        self.show_page("manage_suppliers")

    def show_manage_conferentes(self):
        self.refresh_conferentes_listbox()
        self.show_page("manage_conferentes")

    def update_recent_list(self):
        # Limpa antes
        for item in self.recent_tree.get_children():
            self.recent_tree.delete(item)

        notes = utils.load_notes()
        for n in reversed(notes[-5:]):  # mostra as últimas 8
            self.recent_tree.insert(
                "",
                "end",
                values=(
                    n.get("nf_number"),
                    n.get("fornecedor_name"),
                    n.get("cnpj"),
                    n.get("conferente_name")
                )
            )
    
    def show_page(self, page_key):
        for k, p in self.pages.items():
            p.pack_forget()
        self.pages[page_key].pack(fill="both", expand=True)
        # focus first widget for accessibility
        if page_key == "add_form":
            self.entry_nf.focus_set()
    
    def on_close(self):
        self.root.destroy()

    def _add_tooltip(self, iid, text):
        
        def on_enter(event, iid=iid, txt=text):
            x, y, _, _ = self.tree.bbox(iid, column="conferido")
            x += self.tree.winfo_rootx()
            y += self.tree.winfo_rooty()
            self.tooltip = tk.Toplevel(self.tree)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x+40}+{y}")
            tk.Label(self.tooltip, text=txt, background="black", foreground="white", padx=4, pady=2).pack()
        def on_leave(event):
            if hasattr(self, "tooltip"):
                self.tooltip.destroy()
                self.tooltip = None

    def _setup_tooltip_support(self):
        self.tooltip = None
        self.tree.bind("<Motion>", self._on_motion)
        self.tree.bind("<Leave>", lambda e: self._hide_tooltip())

    def _on_motion(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            self._hide_tooltip()
            return

        row_id = self.tree.identify_row(event.y)
        col_id = self.tree.identify_column(event.x)

        # Conferência é a 6ª coluna (#6)
        if not row_id or col_id != "#6":
            self._hide_tooltip()
            return

        values = self.tree.item(row_id, "values")
        if len(values) < 6 or values[5] != "✔":
            self._hide_tooltip()
            return

        nf_number = values[0]
        notes = utils.load_notes()
        note = next((n for n in notes if n["nf_number"] == nf_number), None)
        if not note:
            return

        texto = f'{note.get("conferido_por", "?")} em {note.get("conferido_em", "?")}'
        self._show_tooltip(event, texto)

    def _show_tooltip(self, event, text):
        if self.tooltip:
            self.tooltip.destroy()
        self.tooltip = tk.Toplevel(self.tree)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{event.x_root+15}+{event.y_root+15}")
        tk.Label(
            self.tooltip,
            text=text,
            background="black",
            foreground="white",
        padx=4,
        pady=2,
        font=("Segoe UI", 9)
    ).pack()

    def _hide_tooltip(self):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None


def main():
    from utils_estoque import check_for_updates
    root = customtkinter.CTk()
    check_for_updates(root)
    app = EstoqueApp(root)
    root.mainloop()
