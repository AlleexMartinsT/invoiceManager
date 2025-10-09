import customtkinter as ctk
from tkinter import messagebox
from system.ui_components import make_label
import tkinter as tk
from datetime import datetime

class FiltersMixin:  
    def _build_filters(self):
        
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self.update_entry_width)
        
        self.search_entry = ctk.CTkEntry(
            self.search_frame,
            placeholder_text="Pesquisar...",
            text_color="white",
            justify="left",
            textvariable=self.search_var,
            width=30,
            corner_radius=6,
            border_color="#F5F2F2"
        )
        self.search_entry.pack(side="left", padx=(0, 6))

        self.search_option = ctk.StringVar(value="Nota Fiscal")
        self.search_combo = ctk.CTkComboBox(
            self.search_frame,
            values=["NF", "Fornecedor"],
            variable=self.search_option,
            state="readonly",
            width=120,
            justify='center',
            corner_radius=6,
            border_width=1
        )
        self.search_combo.pack(side="left", padx=(0, 6))

        self.btn_search = ctk.CTkButton(
            self.search_frame,
            text="Buscar",
            command=self._search_notes,
            width=80,
            fg_color="#4989d3",
            hover_color="#2b81e2"
        )
        self.btn_search.pack(side="left", padx=(0, 6))

        self.btn_clear_search = ctk.CTkButton(
            self.search_frame,
            text="Limpar",
            command=self.refresh_table,
            width=80,
            fg_color="#777777",
            hover_color="#555555"
        )
        self.btn_clear_search.pack(side="left")
        
        make_label(self.left_frame, "Filtrar por:").pack(anchor="w", pady=(4, 6), padx=6)

        # estado dos painéis (inicialmente fechados)
        self.cnpj_expanded = False
        self.adv_expanded = False
        self.data_expanded = False
        
        # --- Header toggle DATA ---
        self.btn_toggle_data = ctk.CTkButton(
            self.left_frame,
            text="▶ Filtros de Datas",
            anchor="w",
            command=self.toggle_data_filters,
            fg_color="#5ECC97",
            hover_color="#6DEDAF",
            corner_radius=6
        )
        self.btn_toggle_data.pack(fill="x", padx=6, pady=(4, 2))

        self.data_content_frame = ctk.CTkFrame(
            self.left_frame,
            fg_color="#2a2a2a",
            border_color="#F5F2F2",
            border_width=2,
            corner_radius=8
            )
        
        # ======== BLOCO: FILTRO POR DATA DE CHEGADA ========
        make_label(self.data_content_frame, "Data de Chegada", font=("Segoe UI", 14, "bold")).pack(anchor="center", padx=6, pady=(8, 0))

        make_label(self.data_content_frame, "De:").pack(anchor="w", padx=6, pady=(4, 0))
        from tkcalendar import DateEntry

        self.date_from = DateEntry(
            self.data_content_frame,
            date_pattern="dd/MM/yyyy",
            width=12,
            background="black",
            foreground="white",
            borderwidth=2,
            year=datetime.now().year,
            month=datetime.now().month,
            day=datetime.now().day
        )
        self.date_from.pack(fill="x", padx=6, pady=4)

        make_label(self.data_content_frame, "Até:").pack(anchor="w", padx=6, pady=(4, 0))
        self.date_to = DateEntry(
            self.data_content_frame,
            date_pattern="dd/MM/yyyy",
            width=12,
            background="black",
            foreground="white",
            borderwidth=2,
            year=datetime.now().year,
            month=datetime.now().month,
            day=datetime.now().day
        )
        self.date_to.pack(fill="x", padx=6, pady=4) 
        
        self.btn_apply_chegada = ctk.CTkButton(
            self.data_content_frame,
            text="Aplicar filtro",
            command=lambda: self.apply_date_filter("chegada"),
            fg_color="#4989d3",
            hover_color="#2b81e2"
        )
        self.btn_apply_chegada.pack(fill="x", padx=6, pady=(6, 2))

        self.btn_clear_chegada = ctk.CTkButton(
            self.data_content_frame,
            text="Limpar filtro", 
            command=lambda: self.clear_date_filter("chegada"),
            fg_color="#777777",
            hover_color="#555555"
        )
        self.btn_clear_chegada.pack(fill="x", padx=6, pady=(0, 10))

        make_label(self.data_content_frame, "Data de Conferência", font=("Segoe UI", 14, "bold")).pack(anchor="center", padx=6, pady=(10, 0))

        make_label(self.data_content_frame, "De:").pack(anchor="w", padx=6, pady=(4, 0))
        self.date_conf_from = DateEntry(
            self.data_content_frame,
            date_pattern="dd/MM/yyyy",
            width=12,
            background="black",
            foreground="white",
            borderwidth=2,
            year=datetime.now().year,
            month=datetime.now().month,
            day=datetime.now().day
        )
        self.date_conf_from.pack(fill="x", padx=6, pady=4)

        make_label(self.data_content_frame, "Até:").pack(anchor="w", padx=6, pady=(4, 0))
        self.date_conf_to = DateEntry(
            self.data_content_frame,
            date_pattern="dd/MM/yyyy",
            width=12,
            background="black",
            foreground="white",
            borderwidth=2,
            year=datetime.now().year,
            month=datetime.now().month,
            day=datetime.now().day
        )
        self.date_conf_to.pack(fill="x", padx=6, pady=4)

        self.btn_apply_conf = ctk.CTkButton(
            self.data_content_frame,
            text="Aplicar filtro", # Conferencia
            command=lambda: self.apply_date_filter("conferencia"),
            fg_color="#4989d3",
            hover_color="#2b81e2"
        )
        self.btn_apply_conf.pack(fill="x", padx=6, pady=(6, 2))

        self.btn_clear_conf = ctk.CTkButton(
            self.data_content_frame,
            text="Limpar filtro", # Conferencia
            command=lambda: self.clear_date_filter("conferencia"),
            fg_color="#777777",
            hover_color="#555555"
        )
        self.btn_clear_conf.pack(fill="x", padx=6, pady=(0, 10))
        
        # --- Header toggle CNPJ ---
        self.btn_toggle_cnpj = ctk.CTkButton(
            self.left_frame,
            text="▶ CNPJ (EH / MVA)",
            anchor="w",
            command=self.toggle_cnpj_filters,
            fg_color="#5ECC97",
            hover_color="#6DEDAF",
            corner_radius=6
        )
        self.btn_toggle_cnpj.pack(fill="x", padx=6, pady=(4, 2))

        # frame que contém os controles de CNPJ (checkboxes)
        self.cnpj_content_frame = ctk.CTkFrame(
            self.left_frame,
            fg_color="#2a2a2a",
            border_color="#F5F2F2",
            border_width=2,
            corner_radius=8
        )

        # vars e checkboxes (parent é o cnpj_content_frame)
        self.filter_vars = {"EH": tk.BooleanVar(value=True), "MVA": tk.BooleanVar(value=True)}
        cb_eh = ctk.CTkCheckBox(
            self.cnpj_content_frame,
            text="Horizonte",
            variable=self.filter_vars["EH"],
            command=self.refresh_table,
            text_color="white"
        )
        cb_mva = ctk.CTkCheckBox(
            self.cnpj_content_frame,
            text="MVA",
            variable=self.filter_vars["MVA"],
            command=self.refresh_table,
            text_color="white"
        )
        cb_eh.pack(anchor="w", padx=6, pady=2)
        cb_mva.pack(anchor="w", padx=6, pady=2)

        # --- Header toggle filtros avançados ---
        self.btn_toggle_adv = ctk.CTkButton(
            self.left_frame,
            text="▶ Filtros avançados",
            anchor="w",
            command=self.toggle_adv_filters,
            fg_color="#5ECC97",
            hover_color="#6DEDAF",
            corner_radius=6
        )
        self.btn_toggle_adv.pack(fill="x", padx=6, pady=(4, 2))

        # frame que contém os filtros avançados (fornecedor / conferente / status)
        self.adv_content_frame = ctk.CTkFrame(
            self.left_frame,
            fg_color="#2a2a2a",
            border_color="#F5F2F2",
            border_width=2,
            corner_radius=8
        )


        # Fornecedor
        make_label(self.adv_content_frame, "Fornecedor:").pack(anchor="w", padx=4, pady=(6, 0))
        self.filter_fornecedor_var = ctk.StringVar(value="Todas")
        self.filter_fornecedor_cb = ctk.CTkComboBox(
            self.adv_content_frame,
            values=["Todas"] + self._supplier_names(),
            variable=self.filter_fornecedor_var,
            state="readonly",
            justify="center"
        )
        self.filter_fornecedor_cb.pack(fill="x", padx=6, pady=4)

        # Conferente
        make_label(self.adv_content_frame, "Conferente:").pack(anchor="w", padx=4, pady=(4, 0))
        self.filter_conferente_var = ctk.StringVar(value="Todos")
        self.filter_conferente_cb = ctk.CTkComboBox(
            self.adv_content_frame,
            values=["Todos"] + self._conferente_names(),
            variable=self.filter_conferente_var,
            state="readonly",
            justify="center"
        )
        self.filter_conferente_cb.pack(fill="x", padx=6, pady=4)

        # Status conferência
        make_label(self.adv_content_frame, "Status conferência:").pack(anchor="w", padx=4, pady=(4, 0))
        self.filter_conferido_var = tk.StringVar(value="Todas")
        self.combo_filtro_conferido = ctk.CTkComboBox(
            self.adv_content_frame,
            values=["Todas", "Notas conferidas", "Notas não conferidas"],
            variable=self.filter_conferido_var,
            state="readonly",
            justify="center"
        )
        self.combo_filtro_conferido.pack(pady=4, padx=6, fill="x")

        # Frame dos botões Aplicar / Limpar
        self.frame_filters = ctk.CTkFrame(self.left_frame)
        self.btn_apply_filters = ctk.CTkButton(
            self.frame_filters,
            text="Aplicar filtros",
            command=self.refresh_table,
            hover_color="#2b81e2",
            fg_color="#4989d3"
        )
        self.btn_clear_filters = ctk.CTkButton(
            self.frame_filters,
            text="Limpar filtros",
            command=self._clear_filters,
            hover_color="#2b81e2",
            fg_color="#4989d3"
        )
        # não dar pack ainda; só quando o painel for expandido
        if self.btn_apply_filters:
            self.btn_apply_filters.pack(expand=True, fill="x", pady=4)
            self.btn_clear_filters.pack(expand=True, fill="x", pady=4)

        # --- quick actions (mantém a hierarquia / ordem original) ---
        ctk.CTkButton(self.left_frame, text="Adicionar Nota", command=self.show_add_form).pack(pady=(12, 6), padx=6, fill="x")
        ctk.CTkButton(self.left_frame, text="Gerenciar Fornecedores", command=self.show_manage_suppliers).pack(pady=6, padx=6, fill="x")
        ctk.CTkButton(self.left_frame, text="Gerenciar Conferentes", command=self.show_manage_conferentes).pack(pady=6, padx=6, fill="x")

    def _apply_filters(self, notes):
        """Aplica todos os filtros (CNPJ, datas, avançados)."""
        enabled_cnpjs = [k for k, v in self.filter_vars.items() if v.get()]
        filtro_fornecedor = self.filter_fornecedor_var.get()
        filtro_conferente = self.filter_conferente_var.get()
        filtro_conferido = self.filter_conferido_var.get()

        # Filtro de Data
        if self.data_expanded and hasattr(self, "data_filter_active"):
            try:
                if self.data_filter_active == "chegada":
                    date_from = self.date_from.get_date()
                    date_to = self.date_to.get_date()
                    notes = [
                        n for n in notes
                        if n.get("data_chegada")
                        and date_from <= datetime.strptime(n["data_chegada"], "%d-%m-%Y").date() <= date_to
                    ]
                elif self.data_filter_active == "conferencia":
                    date_from = self.date_conf_from.get_date()
                    date_to = self.date_conf_to.get_date()
                    notes = [
                        n for n in notes
                        if n.get("conferido_em")
                        and date_from <= datetime.strptime(n["conferido_em"], "%d-%m-%Y").date() <= date_to
                    ]
            except Exception as e:
                print("Erro ao filtrar por data:", e)

        # Filtro de CNPJs
        notes = [n for n in notes if n.get("cnpj") in enabled_cnpjs]

        # Filtro de fornecedor
        if filtro_fornecedor and filtro_fornecedor != "Todas":
            notes = [n for n in notes if n.get("fornecedor_name") == filtro_fornecedor]

        # Filtro de conferente
        if filtro_conferente and filtro_conferente != "Todos":
            notes = [n for n in notes if n.get("conferente_name") == filtro_conferente]

        # Filtro de conferência
        if filtro_conferido == "Notas conferidas":
            notes = [n for n in notes if n.get("conferido", False)]
        elif filtro_conferido == "Notas não conferidas":
            notes = [n for n in notes if not n.get("conferido", False)]

        return notes

    def toggle_cnpj_filters(self):
        """Mostra/oculta o painel de CNPJ (EH / MVA)."""
        if self.cnpj_expanded:
            self.cnpj_content_frame.pack_forget()
            self.btn_toggle_cnpj.configure(text="▶ CNPJ (EH / MVA)")
            self.cnpj_expanded = False
        else:
            self.cnpj_content_frame.pack(fill="x", padx=6, pady=(2, 4))
            self.btn_toggle_cnpj.configure(text="▼ CNPJ (EH / MVA)")
            self.cnpj_expanded = True

    def toggle_adv_filters(self):
        """Mostra/oculta o painel de filtros avançados e os botões Aplicar/Limpar."""
        if self.adv_expanded:
            self.adv_content_frame.pack_forget()
            self.btn_toggle_adv.configure(text="▶ Filtros avançados")
            self.adv_expanded = False
        else:
            self.adv_content_frame.pack(fill="x", padx=6, pady=(2, 4))
            self.btn_toggle_adv.configure(text="▼ Filtros avançados")
            self.adv_expanded = True
        self._update_filter_buttons()

    def toggle_data_filters(self):
        """Mostra/oculta o painel de Filtros de Datas."""
        if self.data_expanded:
            self.data_content_frame.pack_forget()
            self.btn_toggle_data.configure(text="▶ Filtros de Datas")
            self.data_expanded = False
        else:
            self.data_content_frame.pack(fill="x", padx=6, pady=(2, 4))
            self.btn_toggle_data.configure(text="▼ Filtros de Datas")
            self.data_expanded = True

    def _update_filter_buttons(self):
        """Controla quando mostrar os botões Aplicar/Limpar filtros."""
        if self.adv_expanded or self.data_expanded:
            self.frame_filters.pack(fill="x", padx=6, pady=(6, 4))
        else:
            self.frame_filters.pack_forget()


        if not hasattr(self, "suggestion_box"):
            return
        selection = self.suggestion_box.curselection()
        if selection:
            valor = self.suggestion_box.get(selection[0])
            self.search_entry.delete(0, "end")
            self.search_entry.insert(0, valor)
            self.suggestion_box.destroy()
            self._search_notes()

    def apply_date_filter(self, tipo):
        """Ativa um tipo de filtro de data e desativa o outro."""
        if tipo == "chegada":
            # aplica filtro de chegada
            self.data_filter_active = "chegada"
            self.btn_apply_conf.configure(state="disabled", text_color="red", fg_color="#555555")
            self.btn_clear_conf.configure(state="disabled", text_color="red", fg_color="#555555")
        else:
            # aplica filtro de conferência
            self.data_filter_active = "conferencia"
            self.btn_apply_chegada.configure(state="disabled", text_color="red", fg_color="#555555")
            self.btn_clear_chegada.configure(state="disabled", text_color="red", fg_color="#555555")

        self.refresh_table()

    def clear_date_filter(self, tipo):
        """Limpa o filtro de data ativo e reativa os botões do outro."""
        if hasattr(self, "data_filter_active") and self.data_filter_active == tipo:
            self.data_filter_active = None

        # reativa ambos
        self.btn_apply_chegada.configure(state="normal", text_color="white", fg_color="#4989d3")
        self.btn_clear_chegada.configure(state="normal", text_color="white", fg_color="#777777")
        self.btn_apply_conf.configure(state="normal", text_color="white", fg_color="#4989d3")
        self.btn_clear_conf.configure(state="normal", text_color="white", fg_color="#777777")

        self.refresh_table()

    def warning_month_filter(self):
        if not self.settings.get("visualizar_todos_meses", False):
            import locale, threading  
            locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")
            def show_warning():
                messagebox.showinfo(
                "Aviso",
                f"Dados filtrados do mês de {datetime.now().strftime('%B').capitalize()}/{datetime.now().year}.\n"
                "Para visualizar todos os meses, acesse as Configurações."
                )
            threading.Thread(target=show_warning).start()
        else:
            return
    
    def _clear_filters(self):
        self.filter_vars["EH"].set(True)
        self.filter_vars["MVA"].set(True)
        self.filter_fornecedor_var.set("Todas")
        self.filter_conferente_var.set("Todos")
        self.filter_conferido_var.set("Todas")
        self.refresh_table()
   