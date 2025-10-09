import customtkinter as ctk
import tkinter as tk
import os
import utils_estoque as utils
from system.filters_section import FiltersMixin
from system.table_section import TableMixin
from system.forms_section import FormsMixin
from system.suppliers_section import SuppliersMixin
from system.conferentes_section import ConferentesMixin
from system.settings_section import SettingsMixin
from system.actions_stack import ActionsMixin

ctk.set_default_color_theme(os.path.join(os.path.dirname(__file__), "data", "basedTheme.json")
                                      if os.path.exists(os.path.join(os.path.dirname(__file__), "data", "basedTheme.json"))
                                      else None)
ctk.set_appearance_mode("dark")

class EstoqueApp(FiltersMixin, TableMixin, FormsMixin, SuppliersMixin, ConferentesMixin, SettingsMixin, ActionsMixin):
    def __init__(self, root):
        self.root = root
        self.root.title("Relatório do Estoque")
        self.root.geometry(self.center_geometry(1450, 800))
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Main layout: left é os filtros, main area (table), right é as ações (que muda baseado no left)
        
        # ===== Scrollable Left Frame - versão corrigida =====
        LEFT_WIDTH = 200  # largura fixa desejada

        self.left_container = ctk.CTkFrame(root, width=LEFT_WIDTH)
        self.left_container.pack(side="left", fill="y", padx=8, pady=8)
        self.left_container.pack_propagate(False)

        self.left_canvas = tk.Canvas(
            self.left_container,
            bg="#1e1e1e",
            highlightthickness=0,
            borderwidth=0,
            width=LEFT_WIDTH - 8
        )
        self.left_canvas.pack(side="left", fill="y", expand=False)

        self.scrollbar_left = ctk.CTkScrollbar(
            self.left_container,
            command=self.left_canvas.yview
        )
        self.scrollbar_left.pack(side="right", fill="y")

        self.left_canvas.configure(yscrollcommand=self.scrollbar_left.set)

        # Frame com conteúdo interno
        self.left_frame = ctk.CTkFrame(self.left_canvas, fg_color="#252525")
        self.left_window = self.left_canvas.create_window((0, 0), window=self.left_frame, anchor="nw", width=LEFT_WIDTH - 16)

        # Recalcula região do scroll e evita "espaço fantasma" acima
        def _on_frame_configure(event):
            bbox = self.left_canvas.bbox("all")
            if bbox:
                # força o topo do scroll na posição 0
                x1, y1, x2, y2 = bbox
                if y1 < 0:
                    # ajusta se a área útil ficar deslocada pra cima
                    self.left_canvas.move(self.left_window, 0, -y1)
                    y1 = 0
                self.left_canvas.configure(scrollregion=(x1, y1, x2, y2))

        self.left_frame.bind("<Configure>", _on_frame_configure)

        # Ajusta largura do conteúdo quando o container mudar
        def _on_container_configure(event):
            try:
                sb_w = self.scrollbar_left.winfo_width() or 12
                canvas_w = max(LEFT_WIDTH - sb_w - 6, 100)
                self.left_canvas.itemconfig(self.left_window, width=canvas_w)
            except Exception:
                pass

        self.left_container.bind("<Configure>", _on_container_configure)

        # Scroll do mouse apenas quando o cursor estiver sobre o painel
        def _on_mousewheel(event):
            if os.name == "nt":
                delta = -1 * int(event.delta / 120)
            else:
                delta = -1 * int(event.delta or 0)
            self.left_canvas.yview_scroll(delta, "units")

        def _bind_mousewheel(event):
            self.left_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        def _unbind_mousewheel(event):
            self.left_canvas.unbind_all("<MouseWheel>")

        self.left_canvas.bind("<Enter>", _bind_mousewheel)
        self.left_canvas.bind("<Leave>", _unbind_mousewheel)
        # ===== fim Scrollable Left Frame =====

        self.main_frame = ctk.CTkFrame(root)
        self.main_frame.pack(side="left", fill="both", expand=True, padx=8, pady=8)
        
        self.search_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.search_frame.pack(fill="x", padx=6, pady=(0, 6))

        self.actions_frame = ctk.CTkFrame(root, width=300)
        self.actions_frame.pack(side="right", fill="x", padx=8, pady=8)

        # carrega configurações locais
        self.settings = utils.load_settings()
        
        # Importa MAC Address e checa tabela Sup
        self.mac = utils.get_mac_address()
        self.user = utils.get_or_create_user(utils.supabase, self.mac)

        # monta os componentes da interface
        self._build_filters()
        self._build_table()
        self._build_actions_stack()

        if not self.user:
            self.root.after(200, self._ask_name_non_modal)
        
        # preenche a tabela logo após a janela criar (melhora sensação de inicialização)
        self.root.after(60, self.refresh_table)
        self.root.after(120, self.update_recent_list)
        self.root.after(120, self.warning_month_filter)

        # Key bindings
        self.root.bind("<Escape>", self._handle_escape)
        self._setup_tooltip_support()
        self._bind_search_suggestions()
        utils.poll_notifications(self)
    
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
     
    def update_entry_width(self, *args):
        text = self.search_var.get()
        # largura base + multiplicador de caracteres
        new_width = 75 + len(text) * 8
        self.search_entry.configure(width=min(new_width, 400) - 50)
    
    # ---------------- Add form ----------------

    def _supplier_names(self):
        suppliers = utils.load_suppliers()
        return [s["name"] for s in suppliers]

    def _conferente_names(self):
        conferentes = utils.load_conferentes()
        return [c["name"] for c in conferentes]
      
    # ---------------- Tree context menu and actions ----------------
    
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
         
    def _search_notes(self):
        termo = self.search_entry.get().strip().lower()
        if not termo:
            self.refresh_table()
            return

        filtro_tipo = self.search_option.get()
        notes = utils.load_notes()

        # aplica os filtros normais primeiro
        notes = self._apply_filters(notes)

        # agora filtra pela pesquisa
        if filtro_tipo == "Nota Fiscal":
            notes = [n for n in notes if termo in str(n.get("nf_number", "")).lower()]
        elif filtro_tipo == "Fornecedor":
            notes = [n for n in notes if termo in str(n.get("fornecedor_name", "")).lower()]

        # repopula a tabela
        self._populate_table(notes)

    # ---------------- Helpers ----------------
    
    def _ask_name_non_modal(self):
        """Abre uma janelinha não-modal para perguntar o nome do usuário"""
        top = ctk.CTkToplevel(self.root)
        top.title("Identificação")
        top.geometry(self.center_geometry(200, 300))
        top.geometry("300x150")
        top.grab_set()  # opcional → mantém foco na janelinha, mas sem bloquear o mainloop

        label = ctk.CTkLabel(top, text="Digite seu nome:")
        label.pack(pady=(20, 10))

        entry = ctk.CTkEntry(top, width=220, text_color="white", justify="center")
        entry.pack(pady=5)

        def salvar():
            name = entry.get().strip() or "Usuário"
            resp = utils.supabase.table("users").insert({
                "mac": self.mac,
                "name": name
            }).execute()
            if resp.data:
                self.user = resp.data[0]
            top.destroy()

        btn = ctk.CTkButton(top, text="Salvar", command=salvar)
        btn.pack(pady=15)

        entry.focus()
    
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
   
    def on_close(self):
        self.root.destroy()

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

        values = self.tree.item(row_id, "values")
        if not row_id or not values:
            self._hide_tooltip()
            return

        # --- Tooltip de conferência (coluna 6) ---
        if col_id == "#6":
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
            return

        # --- Tooltip de data de emissão (coluna 2 - Data de Chegada) ---
        if col_id == "#2":
            nf_number = values[0]
            notes = utils.load_notes()
            note = next((n for n in notes if n["nf_number"] == nf_number), None)
            if not note:
                return
            data_emissao = note.get("data_emissao")
            if not data_emissao:
                self._hide_tooltip()
                return
            texto = f"Data de emissão: {data_emissao}"
            self._show_tooltip(event, texto)
            return

        # Se não for conferência nem data emissão → esconde
        self._hide_tooltip()

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

    def _bind_search_suggestions(self):
        self.search_entry.bind("<KeyRelease>", self._update_suggestions)
        self.search_entry.bind("<FocusOut>", lambda e: self.root.after(100, self._hide_suggestions))

    def _update_suggestions(self, event):
        termo = self.search_entry.get().strip().lower()
        filtro_tipo = self.search_option.get()

        notes = utils.load_notes()
        notes = self._apply_filters(notes)

        if filtro_tipo == "Nota Fiscal":
            valores = [str(n.get("nf_number", "")) for n in notes]
        else:
            valores = [str(n.get("fornecedor_name", "")) for n in notes]

        sugestoes = sorted(set([v for v in valores if termo in v.lower()]))[:8]

        self._hide_suggestions()
        if not termo or not sugestoes:
            return

        # criar janela flutuante logo abaixo do entry
        x = self.search_entry.winfo_rootx()
        y = self.search_entry.winfo_rooty() + self.search_entry.winfo_height()

        self.suggestion_win = tk.Toplevel(self.root)
        self.suggestion_win.wm_overrideredirect(True)  # sem bordas
        self.suggestion_win.geometry(f"+{x}+{y}")
        self.suggestion_win.configure(bg="#2b2b2b")  # fundo escuro

        for s in sugestoes:
            lbl = ctk.CTkLabel(
                self.suggestion_win,
                text=s,
                anchor="w",
                fg_color="transparent"
            )
            lbl.pack(fill="x", padx=4, pady=2)

            # ao clicar, seleciona
            lbl.bind("<Button-1>", lambda e, val=s: self._select_suggestion(val))

    def _select_suggestion(self, value):
        self.search_entry.delete(0, "end")
        self.search_entry.insert(0, value)
        self._hide_suggestions()
        self._search_notes()

    def _hide_suggestions(self):
        if hasattr(self, "suggestion_win") and self.suggestion_win.winfo_exists():
            self.suggestion_win.destroy()

if __name__ == "__main__":
    from utils_estoque import check_for_updates
    root = ctk.CTk()
    check_for_updates(root)
    app = EstoqueApp(root)
    root.mainloop()