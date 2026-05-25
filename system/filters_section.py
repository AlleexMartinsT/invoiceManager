from datetime import datetime

from PySide6 import QtCore, QtGui, QtWidgets

from system.ui_components import (
    ClickableDateEdit,
    Toast,
    make_badge,
    make_label,
    make_panel,
    style_button,
    style_combo_field,
    style_date_field,
    style_text_field,
)
from utils_estoque import load_notes


class FiltersMixin:
    def _set_filter_toggle_state(self, button, expanded, label):
        button.setText(label)
        button.setArrowType(QtCore.Qt.DownArrow if expanded else QtCore.Qt.RightArrow)

    def _make_filter_section_label(self, parent, text):
        label = make_label(parent, text, font=("Segoe UI", 11, "bold"), anchor="center")
        label.setProperty("filterSectionLabel", True)
        label.style().unpolish(label)
        label.style().polish(label)
        return label

    def _make_filter_field_label(self, parent, text):
        label = make_label(parent, text, muted=True, anchor="center")
        label.setProperty("filterFieldLabel", True)
        label.setFixedWidth(42)
        label.style().unpolish(label)
        label.style().polish(label)
        return label

    def _make_filter_combo_label(self, parent, text):
        label = make_label(parent, text, muted=True)
        label.setProperty("filterComboLabel", True)
        label.style().unpolish(label)
        label.style().polish(label)
        return label

    def _style_filter_toggle(self, button):
        button.setProperty("filterToggleButton", True)
        font = button.font()
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        font.setBold(True)
        button.setFont(font)
        style_button(button, nav=True)

    def _make_filter_toggle_button(self, parent, label):
        button = QtWidgets.QToolButton(parent)
        button.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        button.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self._set_filter_toggle_state(button, False, label)
        self._style_filter_toggle(button)
        return button

    def _build_filters(self):
        hero_shell = QtWidgets.QHBoxLayout()
        hero_shell.setContentsMargins(0, 0, 0, 0)
        hero_shell.setSpacing(18)
        self.hero_layout.addLayout(hero_shell)

        left_block = QtWidgets.QVBoxLayout()
        left_block.setContentsMargins(0, 0, 0, 0)
        left_block.setSpacing(0)
        hero_shell.addLayout(left_block, 1)

        title = make_label(self.hero_frame, "Dashboard do Estoque", anchor="w")
        title.setProperty("appTitle", True)
        title.style().unpolish(title)
        title.style().polish(title)
        left_block.addWidget(title)
        left_block.addStretch(1)

        right_panel = make_panel(self.hero_frame, "surface")
        right_layout = QtWidgets.QVBoxLayout(right_panel)
        right_layout.setContentsMargins(16, 14, 16, 14)
        right_layout.setSpacing(10)
        hero_shell.addWidget(right_panel, 0, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        self.scope_action_row = QtWidgets.QHBoxLayout()
        self.scope_action_row.setContentsMargins(0, 0, 0, 0)
        self.scope_action_row.setSpacing(10)
        self.scope_badge = make_panel(right_panel, "scopeHighlight")
        self.scope_badge.setProperty("kind", "scopeHighlight")
        scope_layout = QtWidgets.QVBoxLayout(self.scope_badge)
        scope_layout.setContentsMargins(18, 12, 18, 12)
        scope_layout.setSpacing(0)
        self.scope_badge_label = make_label(self.scope_badge, "Mes atual", anchor="center")
        self.scope_badge_label.setProperty("scopeHeadline", True)
        self.scope_badge_label.style().unpolish(self.scope_badge_label)
        self.scope_badge_label.style().polish(self.scope_badge_label)
        scope_layout.addWidget(self.scope_badge_label, 0, QtCore.Qt.AlignCenter)
        self.scope_action_row.addWidget(self.scope_badge, 0, QtCore.Qt.AlignCenter)
        right_layout.addLayout(self.scope_action_row)

        self._build_search_menu()

        self.search_frame.setVisible(False)

        filter_header = make_label(self.left_frame, "Filtrar por:", anchor="center")
        filter_header.setProperty("filterHeader", True)
        filter_header.style().unpolish(filter_header)
        filter_header.style().polish(filter_header)
        self.left_layout.addWidget(filter_header, 0, QtCore.Qt.AlignCenter)

        self.cnpj_expanded = False
        self.adv_expanded = False
        self.data_expanded = False
        self.data_filter_active = None

        self.data_panel = make_panel(self.left_frame, "surface")
        data_panel_layout = QtWidgets.QVBoxLayout(self.data_panel)
        data_panel_layout.setContentsMargins(10, 10, 10, 10)
        data_panel_layout.setSpacing(8)
        self.btn_toggle_data = self._make_filter_toggle_button(self.data_panel, "Datas")
        self.btn_toggle_data.clicked.connect(self.toggle_data_filters)
        data_panel_layout.addWidget(self.btn_toggle_data)

        self.data_content_frame = QtWidgets.QFrame(self.data_panel)
        self.data_content_frame.setVisible(False)
        data_layout = QtWidgets.QVBoxLayout(self.data_content_frame)
        data_layout.setContentsMargins(4, 0, 4, 4)
        data_layout.setSpacing(7)

        data_layout.addWidget(self._make_filter_section_label(self.data_content_frame, "Data de chegada"))
        chegada_from_row = QtWidgets.QHBoxLayout()
        chegada_from_row.setContentsMargins(0, 0, 0, 0)
        chegada_from_row.setSpacing(8)
        chegada_from_row.addWidget(self._make_filter_field_label(self.data_content_frame, "De"))
        self.date_from = ClickableDateEdit(self.data_content_frame)
        self.date_from.setProperty("filterDateField", True)
        style_date_field(self.date_from, width=160, display_format="dd/MM/yyyy")
        self.date_from.setDate(QtCore.QDate.currentDate())
        chegada_from_row.addWidget(self.date_from)
        data_layout.addLayout(chegada_from_row)

        chegada_to_row = QtWidgets.QHBoxLayout()
        chegada_to_row.setContentsMargins(0, 0, 0, 0)
        chegada_to_row.setSpacing(8)
        chegada_to_row.addWidget(self._make_filter_field_label(self.data_content_frame, "Até"))
        self.date_to = ClickableDateEdit(self.data_content_frame)
        self.date_to.setProperty("filterDateField", True)
        style_date_field(self.date_to, width=160, display_format="dd/MM/yyyy")
        self.date_to.setDate(QtCore.QDate.currentDate())
        chegada_to_row.addWidget(self.date_to)
        data_layout.addLayout(chegada_to_row)

        chegada_actions = QtWidgets.QHBoxLayout()
        chegada_actions.setContentsMargins(0, 0, 0, 0)
        chegada_actions.setSpacing(6)
        self.btn_apply_chegada = QtWidgets.QPushButton("Aplicar", self.data_content_frame)
        self.btn_apply_chegada.setFixedWidth(96)
        style_button(self.btn_apply_chegada, accent=True)
        self.btn_apply_chegada.clicked.connect(lambda: self.apply_date_filter("chegada"))
        chegada_actions.addWidget(self.btn_apply_chegada)
        self.btn_clear_chegada = QtWidgets.QPushButton("Limpar", self.data_content_frame)
        self.btn_clear_chegada.setFixedWidth(96)
        style_button(self.btn_clear_chegada, quiet=True)
        self.btn_clear_chegada.clicked.connect(lambda: self.clear_date_filter("chegada"))
        chegada_actions.addWidget(self.btn_clear_chegada)
        data_layout.addLayout(chegada_actions)

        data_layout.addSpacing(6)
        data_layout.addWidget(self._make_filter_section_label(self.data_content_frame, "Conferência"))
        conf_from_row = QtWidgets.QHBoxLayout()
        conf_from_row.setContentsMargins(0, 0, 0, 0)
        conf_from_row.setSpacing(8)
        conf_from_row.addWidget(self._make_filter_field_label(self.data_content_frame, "De"))
        self.date_conf_from = ClickableDateEdit(self.data_content_frame)
        self.date_conf_from.setProperty("filterDateField", True)
        style_date_field(self.date_conf_from, width=160, display_format="dd/MM/yyyy")
        self.date_conf_from.setDate(QtCore.QDate.currentDate())
        conf_from_row.addWidget(self.date_conf_from)
        data_layout.addLayout(conf_from_row)

        conf_to_row = QtWidgets.QHBoxLayout()
        conf_to_row.setContentsMargins(0, 0, 0, 0)
        conf_to_row.setSpacing(8)
        conf_to_row.addWidget(self._make_filter_field_label(self.data_content_frame, "Até"))
        self.date_conf_to = ClickableDateEdit(self.data_content_frame)
        self.date_conf_to.setProperty("filterDateField", True)
        style_date_field(self.date_conf_to, width=160, display_format="dd/MM/yyyy")
        self.date_conf_to.setDate(QtCore.QDate.currentDate())
        conf_to_row.addWidget(self.date_conf_to)
        data_layout.addLayout(conf_to_row)

        conf_actions = QtWidgets.QHBoxLayout()
        conf_actions.setContentsMargins(0, 0, 0, 0)
        conf_actions.setSpacing(6)
        self.btn_apply_conf = QtWidgets.QPushButton("Aplicar", self.data_content_frame)
        self.btn_apply_conf.setFixedWidth(96)
        style_button(self.btn_apply_conf, accent=True)
        self.btn_apply_conf.clicked.connect(lambda: self.apply_date_filter("conferencia"))
        conf_actions.addWidget(self.btn_apply_conf)
        self.btn_clear_conf = QtWidgets.QPushButton("Limpar", self.data_content_frame)
        self.btn_clear_conf.setFixedWidth(96)
        style_button(self.btn_clear_conf, quiet=True)
        self.btn_clear_conf.clicked.connect(lambda: self.clear_date_filter("conferencia"))
        conf_actions.addWidget(self.btn_clear_conf)
        data_layout.addLayout(conf_actions)

        data_panel_layout.addWidget(self.data_content_frame)
        self.left_layout.addWidget(self.data_panel)

        self.cnpj_panel = make_panel(self.left_frame, "surface")
        cnpj_panel_layout = QtWidgets.QVBoxLayout(self.cnpj_panel)
        cnpj_panel_layout.setContentsMargins(10, 10, 10, 10)
        cnpj_panel_layout.setSpacing(8)
        self.btn_toggle_cnpj = self._make_filter_toggle_button(self.cnpj_panel, "CNPJ")
        self.btn_toggle_cnpj.clicked.connect(self.toggle_cnpj_filters)
        cnpj_panel_layout.addWidget(self.btn_toggle_cnpj)

        self.cnpj_content_frame = QtWidgets.QFrame(self.cnpj_panel)
        self.cnpj_content_frame.setVisible(False)
        cnpj_layout = QtWidgets.QVBoxLayout(self.cnpj_content_frame)
        cnpj_layout.setContentsMargins(4, 0, 4, 4)
        cnpj_layout.setSpacing(8)

        self.filter_vars = {
            "EH": QtWidgets.QCheckBox("Horizonte", self.cnpj_content_frame),
            "MVA": QtWidgets.QCheckBox("MVA", self.cnpj_content_frame),
        }
        self.filter_vars["EH"].setChecked(True)
        self.filter_vars["MVA"].setChecked(True)
        self.filter_vars["EH"].stateChanged.connect(lambda *_: self.refresh_table())
        self.filter_vars["MVA"].stateChanged.connect(lambda *_: self.refresh_table())
        cnpj_row = QtWidgets.QHBoxLayout()
        cnpj_row.setContentsMargins(0, 0, 0, 0)
        cnpj_row.setSpacing(10)
        cnpj_row.addWidget(self.filter_vars["EH"])
        cnpj_row.addWidget(self.filter_vars["MVA"])
        cnpj_layout.addLayout(cnpj_row)
        cnpj_panel_layout.addWidget(self.cnpj_content_frame)
        self.left_layout.addWidget(self.cnpj_panel)

        self.adv_panel = make_panel(self.left_frame, "surface")
        adv_panel_layout = QtWidgets.QVBoxLayout(self.adv_panel)
        adv_panel_layout.setContentsMargins(10, 10, 10, 10)
        adv_panel_layout.setSpacing(8)
        self.btn_toggle_adv = self._make_filter_toggle_button(self.adv_panel, "Detalhes")
        self.btn_toggle_adv.clicked.connect(self.toggle_adv_filters)
        adv_panel_layout.addWidget(self.btn_toggle_adv)

        self.adv_content_frame = QtWidgets.QFrame(self.adv_panel)
        self.adv_content_frame.setVisible(False)
        adv_layout = QtWidgets.QVBoxLayout(self.adv_content_frame)
        adv_layout.setContentsMargins(4, 0, 4, 4)
        adv_layout.setSpacing(8)

        adv_layout.addWidget(self._make_filter_combo_label(self.adv_content_frame, "Fornecedor"))
        self.filter_fornecedor_cb = QtWidgets.QComboBox(self.adv_content_frame)
        self.filter_fornecedor_cb.addItems(["Todas"] + self._supplier_names())
        style_combo_field(self.filter_fornecedor_cb, center=True)
        self.filter_fornecedor_cb.currentTextChanged.connect(lambda *_: self.refresh_table())
        adv_layout.addWidget(self.filter_fornecedor_cb)

        adv_layout.addWidget(self._make_filter_combo_label(self.adv_content_frame, "Recebido por"))
        self.filter_recebido_cb = QtWidgets.QComboBox(self.adv_content_frame)
        self.filter_recebido_cb.addItems(["Todos"] + self._conferente_names())
        style_combo_field(self.filter_recebido_cb, center=True)
        self.filter_recebido_cb.currentTextChanged.connect(lambda *_: self.refresh_table())
        adv_layout.addWidget(self.filter_recebido_cb)

        adv_layout.addWidget(self._make_filter_combo_label(self.adv_content_frame, "Conferido por"))
        self.filter_conferido_por_cb = QtWidgets.QComboBox(self.adv_content_frame)
        self.filter_conferido_por_cb.addItems(["Todos"] + self._conferente_names())
        style_combo_field(self.filter_conferido_por_cb, center=True)
        self.filter_conferido_por_cb.currentTextChanged.connect(lambda *_: self.refresh_table())
        adv_layout.addWidget(self.filter_conferido_por_cb)

        adv_layout.addWidget(self._make_filter_combo_label(self.adv_content_frame, "Status da conferência"))
        self.combo_filtro_conferido = QtWidgets.QComboBox(self.adv_content_frame)
        self.combo_filtro_conferido.addItems(["Todas", "Notas conferidas", "Notas nao conferidas"])
        style_combo_field(self.combo_filtro_conferido, center=True)
        self.combo_filtro_conferido.currentTextChanged.connect(lambda *_: self.refresh_table())
        adv_layout.addWidget(self.combo_filtro_conferido)

        adv_panel_layout.addWidget(self.adv_content_frame)
        self.left_layout.addWidget(self.adv_panel)

        self.frame_filters = make_panel(self.left_frame, "surface")
        frame_filters_layout = QtWidgets.QVBoxLayout(self.frame_filters)
        frame_filters_layout.setContentsMargins(10, 10, 10, 10)
        frame_filters_layout.setSpacing(8)

        self.btn_apply_filters = QtWidgets.QPushButton("Aplicar filtros", self.frame_filters)
        style_button(self.btn_apply_filters, accent=True)
        self.btn_apply_filters.clicked.connect(self.refresh_table)
        frame_filters_layout.addWidget(self.btn_apply_filters)
        self.btn_apply_filters.setVisible(False)

        self.btn_clear_filters = QtWidgets.QPushButton("Limpar filtros", self.frame_filters)
        style_button(self.btn_clear_filters, quiet=True)
        self.btn_clear_filters.clicked.connect(self._clear_filters)
        frame_filters_layout.addWidget(self.btn_clear_filters)

        self.frame_filters.setVisible(True)
        self.left_layout.addWidget(self.frame_filters)

        self.left_layout.addStretch(1)
        self._refresh_scope_badge()

    def _build_search_menu(self):
        self.search_popup = QtWidgets.QFrame(self, QtCore.Qt.Popup | QtCore.Qt.FramelessWindowHint)
        self.search_popup.setObjectName("searchPopup")
        self.search_popup.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        popup_layout = QtWidgets.QVBoxLayout(self.search_popup)
        popup_layout.setContentsMargins(0, 0, 0, 0)
        popup_layout.setSpacing(0)

        search_cluster = make_panel(self.search_popup, "surface")
        search_cluster.setMinimumWidth(318)
        search_cluster.setMaximumWidth(318)
        search_cluster_layout = QtWidgets.QVBoxLayout(search_cluster)
        search_cluster_layout.setContentsMargins(16, 16, 16, 16)
        search_cluster_layout.setSpacing(8)

        menu_title = make_label(search_cluster, "Busca", font=("Segoe UI", 13, "bold"), anchor="center")
        search_cluster_layout.addWidget(menu_title, 0, QtCore.Qt.AlignCenter)

        menu_hint = make_label(
            search_cluster,
            "Escolha o tipo de busca e digite o valor para filtrar rapidamente.",
            muted=True,
            anchor="center",
        )
        menu_hint.setWordWrap(True)
        search_cluster_layout.addWidget(menu_hint)

        mode_row = QtWidgets.QHBoxLayout()
        mode_row.setContentsMargins(0, 0, 0, 0)
        mode_row.setSpacing(8)

        self.search_mode_nf = QtWidgets.QPushButton("NF", search_cluster)
        self.search_mode_nf.setObjectName("searchModeButton")
        self.search_mode_nf.setCheckable(True)
        self.search_mode_nf.setChecked(True)
        self.search_mode_nf.setFixedWidth(88)
        style_button(self.search_mode_nf)
        self.search_mode_nf.clicked.connect(lambda: self._set_search_mode("NF"))
        mode_row.addWidget(self.search_mode_nf)

        self.search_mode_supplier = QtWidgets.QPushButton("Fornecedor", search_cluster)
        self.search_mode_supplier.setObjectName("searchModeButton")
        self.search_mode_supplier.setCheckable(True)
        self.search_mode_supplier.setFixedWidth(118)
        style_button(self.search_mode_supplier)
        self.search_mode_supplier.clicked.connect(lambda: self._set_search_mode("Fornecedor"))
        mode_row.addWidget(self.search_mode_supplier)

        search_cluster_layout.addLayout(mode_row)

        self.search_entry = QtWidgets.QLineEdit(search_cluster)
        self.search_entry.setPlaceholderText("Procure NF...")
        self.search_entry.setMaxLength(20)
        style_text_field(self.search_entry, center=True, width=220)
        self.search_entry.textChanged.connect(self._sanitize_search_text)
        self.search_entry.returnPressed.connect(self._search_notes_and_close)
        search_cluster_layout.addWidget(self.search_entry, 0, QtCore.Qt.AlignCenter)

        button_row = QtWidgets.QHBoxLayout()
        button_row.setContentsMargins(0, 0, 0, 0)
        button_row.setSpacing(8)
        self.btn_search = QtWidgets.QPushButton("Buscar", search_cluster)
        style_button(self.btn_search, accent=True)
        self.btn_search.setFixedWidth(84)
        self.btn_search.clicked.connect(self._search_notes_and_close)
        button_row.addWidget(self.btn_search)

        self.btn_clear_search = QtWidgets.QPushButton("Limpar", search_cluster)
        style_button(self.btn_clear_search, quiet=True)
        self.btn_clear_search.setFixedWidth(76)
        self.btn_clear_search.clicked.connect(self._clear_search_and_close)
        button_row.addWidget(self.btn_clear_search)
        search_cluster_layout.addLayout(button_row)

        self._set_search_mode("NF")

        popup_layout.addWidget(search_cluster)
        self.search_menu = self.search_popup

    def _show_search_menu(self):
        if not hasattr(self, "search_popup") or not hasattr(self, "btn_toggle_search"):
            return

        if self.search_popup.isVisible():
            self.search_popup.close()
            return

        self.search_popup.ensurePolished()
        self.search_popup.adjustSize()
        popup_size = self.search_popup.sizeHint()
        anchor = self.btn_toggle_search
        anchor_bottom_right = anchor.mapToGlobal(QtCore.QPoint(anchor.width(), anchor.height()))
        x = anchor_bottom_right.x() - popup_size.width()
        y = anchor_bottom_right.y() + 10

        screen = QtGui.QGuiApplication.screenAt(anchor_bottom_right)
        if screen:
            available = screen.availableGeometry()
            x = max(available.left() + 8, min(x, available.right() - popup_size.width() - 8))
            y = max(available.top() + 8, min(y, available.bottom() - popup_size.height() - 8))

        self.search_popup.move(QtCore.QPoint(x, y))
        self.search_popup.show()
        self.search_popup.raise_()
        QtCore.QTimer.singleShot(0, self.search_entry.setFocus)

    def _set_search_mode(self, mode):
        nf_mode = mode == "NF"
        self.search_mode_nf.setChecked(nf_mode)
        self.search_mode_supplier.setChecked(not nf_mode)
        self.search_entry.clear()
        self.search_entry.setPlaceholderText("Procure NF..." if nf_mode else "Procure fornecedor...")
        self.search_entry.setMaxLength(20)
        if nf_mode:
            self.search_entry.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(r"\d*"), self.search_entry))
        else:
            self.search_entry.setValidator(None)
        if hasattr(self, "search_model"):
            self.search_model.setStringList([])
        self.update_entry_width()

    def _sanitize_search_text(self, text):
        if not hasattr(self, "search_entry"):
            return

        if self._current_search_mode() == "NF":
            sanitized = "".join(ch for ch in text if ch.isdigit())[:20]
        else:
            sanitized = text[:20]

        if sanitized != text:
            cursor_pos = min(len(sanitized), self.search_entry.cursorPosition())
            self.search_entry.blockSignals(True)
            self.search_entry.setText(sanitized)
            self.search_entry.setCursorPosition(cursor_pos)
            self.search_entry.blockSignals(False)

    def _search_notes_and_close(self):
        self._search_notes()
        if hasattr(self, "search_popup"):
            self.search_popup.close()

    def _clear_search_and_close(self):
        self.search_entry.clear()
        self.refresh_table()
        if hasattr(self, "search_popup"):
            self.search_popup.close()

    def _apply_filters(self, notes):
        enabled_cnpjs = [k for k, v in self.filter_vars.items() if v.isChecked()]
        filtro_fornecedor = self.filter_fornecedor_cb.currentText()
        filtro_conferido = self.combo_filtro_conferido.currentText()

        if self.data_expanded and self.data_filter_active:
            try:
                if self.data_filter_active == "chegada":
                    date_from = self._qdate_to_date(self.date_from.date())
                    date_to = self._qdate_to_date(self.date_to.date())
                    notes = [
                        n
                        for n in notes
                        if n.get("data_chegada")
                        and date_from <= datetime.strptime(n["data_chegada"], "%d-%m-%Y").date() <= date_to
                    ]
                elif self.data_filter_active == "conferencia":
                    date_from = self._qdate_to_date(self.date_conf_from.date())
                    date_to = self._qdate_to_date(self.date_conf_to.date())
                    notes = [
                        n
                        for n in notes
                        if n.get("conferido_em")
                        and date_from <= datetime.strptime(n["conferido_em"], "%d-%m-%Y").date() <= date_to
                    ]
            except Exception as e:
                print("Erro ao filtrar por data:", e)

        notes = [n for n in notes if n.get("cnpj") in enabled_cnpjs]

        if filtro_fornecedor and filtro_fornecedor != "Todas":
            notes = [n for n in notes if n.get("fornecedor_name") == filtro_fornecedor]

        filtro_recebido = self.filter_recebido_cb.currentText()
        if filtro_recebido and filtro_recebido != "Todos":
            notes = [
                n
                for n in notes
                if (n.get("recebido_por") or n.get("conferente_name")) == filtro_recebido
            ]

        filtro_conferido_por = self.filter_conferido_por_cb.currentText()
        if filtro_conferido_por and filtro_conferido_por != "Todos":
            notes = [n for n in notes if n.get("conferido_por") == filtro_conferido_por]

        if filtro_conferido == "Notas conferidas":
            notes = [n for n in notes if n.get("conferido", False)]
        elif filtro_conferido == "Notas nao conferidas":
            notes = [n for n in notes if not n.get("conferido", False)]

        return notes

    def toggle_cnpj_filters(self):
        self.cnpj_expanded = not self.cnpj_expanded
        self.cnpj_content_frame.setVisible(self.cnpj_expanded)
        self._set_filter_toggle_state(self.btn_toggle_cnpj, self.cnpj_expanded, "CNPJ")
        self._update_filter_buttons()

    def toggle_adv_filters(self):
        self.adv_expanded = not self.adv_expanded
        self.adv_content_frame.setVisible(self.adv_expanded)
        self._set_filter_toggle_state(self.btn_toggle_adv, self.adv_expanded, "Detalhes")
        self._update_filter_buttons()

    def toggle_data_filters(self):
        self.data_expanded = not self.data_expanded
        self.data_content_frame.setVisible(self.data_expanded)
        self._set_filter_toggle_state(self.btn_toggle_data, self.data_expanded, "Datas")
        self._update_filter_buttons()

    def _update_filter_buttons(self):
        self.frame_filters.setVisible(True)

    def apply_date_filter(self, tipo):
        if tipo == "chegada":
            self.data_filter_active = "chegada"
            self.btn_apply_conf.setEnabled(False)
            self.btn_clear_conf.setEnabled(False)
        else:
            self.data_filter_active = "conferencia"
            self.btn_apply_chegada.setEnabled(False)
            self.btn_clear_chegada.setEnabled(False)

        self.refresh_table()

    def clear_date_filter(self, tipo):
        if self.data_filter_active == tipo:
            self.data_filter_active = None

        self.btn_apply_chegada.setEnabled(True)
        self.btn_clear_chegada.setEnabled(True)
        self.btn_apply_conf.setEnabled(True)
        self.btn_clear_conf.setEnabled(True)
        self.refresh_table()

    def _refresh_scope_badge(self):
        if not hasattr(self, "scope_badge_label"):
            return

        if self.settings.get("visualizar_todos_meses", False):
            self.scope_badge_label.setText("Historico anual")
        else:
            self.scope_badge_label.setText("Mes atual")

    def _update_toolbar_summary(self, total, conferidas):
        self._refresh_scope_badge()
        escopo = "Hist\u00f3rico anual" if self.settings.get("visualizar_todos_meses", False) else datetime.now().strftime("%m/%Y")
        if hasattr(self, "operational_visible_value"):
            self.operational_visible_value.setText(str(total))
        if hasattr(self, "operational_done_value"):
            self.operational_done_value.setText(str(conferidas))
        if hasattr(self, "operational_scope_value"):
            self.operational_scope_value.setText(escopo)

    def warning_month_filter(self):
        if not self.settings.get("visualizar_todos_meses", False):
            Toast(
                self,
                f"Exibindo apenas o M\u00eas Atual ({datetime.now().strftime('%m/%Y')}). Ajuste isso em Preferencias.",
                timeout_ms=5600,
            )

    def _handle_autocomplete(self):
        termo = self.search_entry.text().strip().lower()
        if not termo:
            return

        filtro_tipo = self._current_search_mode()
        notes = load_notes()
        notes = self._apply_filters(notes)

        if filtro_tipo in ("NF", "Nota Fiscal"):
            valores = [str(n.get("nf_number", "")) for n in notes]
        elif filtro_tipo == "Fornecedor":
            valores = [str(n.get("fornecedor_name", "")) for n in notes]
        else:
            valores = []

        sugestao = next((v for v in valores if v.lower().startswith(termo)), None)
        if sugestao:
            self.search_entry.setText(sugestao)

    def _clear_filters(self):
        self.filter_vars["EH"].setChecked(True)
        self.filter_vars["MVA"].setChecked(True)
        self.filter_fornecedor_cb.setCurrentText("Todas")
        self.filter_recebido_cb.setCurrentText("Todos")
        self.filter_conferido_por_cb.setCurrentText("Todos")
        self.combo_filtro_conferido.setCurrentText("Todas")
        self.data_filter_active = None
        self.date_from.setDate(QtCore.QDate.currentDate())
        self.date_to.setDate(QtCore.QDate.currentDate())
        self.date_conf_from.setDate(QtCore.QDate.currentDate())
        self.date_conf_to.setDate(QtCore.QDate.currentDate())
        self.btn_apply_chegada.setEnabled(True)
        self.btn_clear_chegada.setEnabled(True)
        self.btn_apply_conf.setEnabled(True)
        self.btn_clear_conf.setEnabled(True)
        self.refresh_table()

    @staticmethod
    def _qdate_to_date(qdate):
        return datetime(qdate.year(), qdate.month(), qdate.day()).date()
