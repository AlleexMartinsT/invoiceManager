import os

from PySide6 import QtCore, QtGui, QtWidgets

import utils_estoque as utils
from system.ui_components import apply_shadow, make_badge, make_label, make_panel, style_button


class ActionsMixin:
    def _make_rail_card(self, height=None):
        card = make_panel(self.actions_body, "surface")
        card.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        if height:
            card.setFixedHeight(height)
        return card

    def _build_actions_stack(self):
        self.pages = {"home": self.actions_body}
        self.page_container = None
        self.actions_layout.setAlignment(QtCore.Qt.AlignTop)

        brand_card = QtWidgets.QFrame(self.actions_body)
        brand_card.setObjectName("brandLogoOnly")
        brand_card.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        brand_card.setFixedHeight(116)
        brand_layout = QtWidgets.QVBoxLayout(brand_card)
        brand_layout.setContentsMargins(0, 8, 0, 8)
        brand_layout.setSpacing(0)

        img_path = os.path.join("data", "logo.png")
        if os.path.exists(img_path):
            pix = QtGui.QPixmap(utils.resource_path(img_path))
            if not pix.isNull():
                lbl_img = QtWidgets.QLabel(brand_card)
                lbl_img.setFixedSize(96, 96)
                lbl_img.setPixmap(pix.scaled(96, 96, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
                lbl_img.setAlignment(QtCore.Qt.AlignCenter)
                brand_layout.addWidget(lbl_img, 0, QtCore.Qt.AlignCenter)

        title = make_label(brand_card, "Painel de Ações", font=("Segoe UI", 18, "bold"), anchor="center")
        brand_layout.addWidget(title, 0, QtCore.Qt.AlignCenter)
        self.home_badge = make_badge(brand_card, "Ativo", "blue")
        self.home_badge_label = self.home_badge.findChild(QtWidgets.QLabel)
        brand_layout.addWidget(self.home_badge, 0, QtCore.Qt.AlignCenter)
        title.setVisible(False)
        self.home_badge.setVisible(False)
        self.actions_layout.addWidget(brand_card)

        self._build_home(self.actions_body)

        cfg_icon_path = os.path.join("data", "config.png")
        if os.path.exists(cfg_icon_path):
            pix = QtGui.QPixmap(utils.resource_path(cfg_icon_path))
            if not pix.isNull():
                btn_cfg = QtWidgets.QToolButton(self.hero_frame)
                btn_cfg.setIcon(QtGui.QIcon(pix))
                btn_cfg.setIconSize(QtCore.QSize(22, 22))
                btn_cfg.clicked.connect(self.show_settings_page)
                if hasattr(self, "scope_action_row"):
                    self.scope_action_row.addWidget(btn_cfg, 0, QtCore.Qt.AlignCenter)

    def _build_home(self, _parent):
        quick_card = self._make_rail_card(210)
        quick_layout = QtWidgets.QVBoxLayout(quick_card)
        quick_layout.setContentsMargins(16, 14, 16, 14)
        quick_layout.setSpacing(8)

        self.btn_create_note = QtWidgets.QPushButton("Criar nota", quick_card)
        self.btn_create_note.setFixedSize(232, 40)
        self.btn_create_note.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        style_button(self.btn_create_note, accent=True)
        self.btn_create_note.clicked.connect(self.show_add_form)
        quick_layout.addWidget(self.btn_create_note, 0, QtCore.Qt.AlignCenter)

        self.btn_manage_suppliers = QtWidgets.QPushButton("Gerenciar fornecedores", quick_card)
        self.btn_manage_suppliers.setFixedSize(232, 40)
        self.btn_manage_suppliers.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        style_button(self.btn_manage_suppliers)
        self.btn_manage_suppliers.clicked.connect(self.show_manage_suppliers)
        quick_layout.addWidget(self.btn_manage_suppliers, 0, QtCore.Qt.AlignCenter)

        self.btn_manage_conferentes = QtWidgets.QPushButton("Gerenciar conferentes", quick_card)
        self.btn_manage_conferentes.setFixedSize(232, 40)
        self.btn_manage_conferentes.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        style_button(self.btn_manage_conferentes)
        self.btn_manage_conferentes.clicked.connect(self.show_manage_conferentes)
        quick_layout.addWidget(self.btn_manage_conferentes, 0, QtCore.Qt.AlignCenter)

        self.btn_quick_settings = QtWidgets.QPushButton("Preferencias", quick_card)
        self.btn_quick_settings.setFixedSize(232, 40)
        self.btn_quick_settings.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        style_button(self.btn_quick_settings, quiet=True)
        self.btn_quick_settings.clicked.connect(self.show_settings_page)
        quick_layout.addWidget(self.btn_quick_settings, 0, QtCore.Qt.AlignCenter)
        self.btn_quick_settings.setVisible(False)

        auto_hint = make_label(
            quick_card,
            "Atualização automática ativa. A tabela e este painel se atualizam quando houver mudanças.",
            muted=True,
            anchor="center",
        )
        auto_hint.setWordWrap(True)
        auto_hint.setFixedHeight(38)
        quick_layout.addWidget(auto_hint)
        self.actions_layout.addWidget(quick_card)

        recent_card = self._make_rail_card(286)
        recent_layout = QtWidgets.QVBoxLayout(recent_card)
        recent_layout.setContentsMargins(14, 10, 14, 10)
        recent_layout.setSpacing(5)
        recent_title = make_label(
            recent_card,
            "Últimas movimentações",
            font=("Segoe UI", 11, "bold"),
            anchor="center",
        )
        recent_layout.addWidget(recent_title, 0, QtCore.Qt.AlignCenter)

        self.recent_table = QtWidgets.QTableWidget(0, 3, recent_card)
        self.recent_table.setFixedHeight(160)
        self.recent_table.setHorizontalHeaderLabels(["NF", "Fornecedor", "CNPJ"])
        self.recent_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.recent_table.verticalHeader().setVisible(False)
        self.recent_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.recent_table.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.recent_table.setFocusPolicy(QtCore.Qt.NoFocus)
        self.recent_table.setShowGrid(False)
        self.recent_table.setAlternatingRowColors(True)
        recent_layout.addWidget(self.recent_table)

        self.recent_event_label = make_label(recent_card, "Nenhuma movimentação recente.", muted=True, anchor="center")
        self.recent_event_label.setWordWrap(True)
        self.recent_event_label.setFixedHeight(24)
        recent_layout.addWidget(self.recent_event_label)
        self.actions_layout.addWidget(recent_card)

        activity_card = self._make_rail_card(190)
        activity_layout = QtWidgets.QVBoxLayout(activity_card)
        activity_layout.setContentsMargins(16, 14, 16, 14)
        activity_layout.setSpacing(8)

        activity_header = QtWidgets.QGridLayout()
        activity_header.setContentsMargins(0, 0, 0, 0)
        activity_header.setSpacing(0)
        activity_title = make_label(
            activity_card,
            "Conferência",
            font=("Segoe UI", 11, "bold"),
            anchor="center",
        )
        activity_header.addWidget(activity_title, 0, 0, QtCore.Qt.AlignCenter)

        self.btn_conference_filter = QtWidgets.QToolButton(activity_card)
        self.btn_conference_filter.setText("")
        self.btn_conference_filter.setIcon(self._make_filter_icon())
        self.btn_conference_filter.setIconSize(QtCore.QSize(16, 16))
        self.btn_conference_filter.setToolTip("Filtrar conferências")
        self.btn_conference_filter.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.btn_conference_filter.setToolTip("Filtrar confer\u00eancias")
        self.conference_filter_menu = QtWidgets.QMenu(self.btn_conference_filter)
        self.conference_period_actions = {}
        for key, label in (
            ("day", "Dia"),
            ("week", "Semana"),
            ("month", "Mês"),
            ("total", "Total"),
        ):
            action = self.conference_filter_menu.addAction(label)
            action.setCheckable(True)
            action.triggered.connect(lambda checked=False, period=key: self._set_conference_period(period))
            self.conference_period_actions[key] = action
        self.conference_period = "month"
        self.conference_period_actions[self.conference_period].setChecked(True)
        self.conference_period_actions["month"].setText("M\u00eas")
        self.btn_conference_filter.setMenu(self.conference_filter_menu)
        activity_header.addWidget(self.btn_conference_filter, 0, 0, QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)
        activity_layout.addLayout(activity_header)

        self.conference_table = QtWidgets.QTableWidget(0, 2, activity_card)
        self.conference_table.setFixedHeight(116)
        self.conference_table.setHorizontalHeaderLabels(["Conferente", "Notas"])
        self.conference_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.conference_table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.conference_table.verticalHeader().setVisible(False)
        self.conference_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.conference_table.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.conference_table.setFocusPolicy(QtCore.Qt.NoFocus)
        self.conference_table.setShowGrid(False)
        self.conference_table.setAlternatingRowColors(True)
        self.conference_table.setWordWrap(False)
        activity_layout.addWidget(self.conference_table)
        self.actions_layout.addWidget(activity_card)

        self.actions_layout.addStretch(1)

    def update_recent_list(self):
        if not hasattr(self, "recent_table"):
            return

        self.recent_table.setRowCount(0)
        notes = utils.load_notes()
        recent_notes = list(reversed(notes[-5:]))
        for n in recent_notes:
            row = self.recent_table.rowCount()
            self.recent_table.insertRow(row)
            vals = [
                str(n.get("nf_number") or ""),
                str(n.get("fornecedor_name") or ""),
                str(n.get("cnpj") or ""),
            ]
            for col, val in enumerate(vals):
                item = QtWidgets.QTableWidgetItem(val)
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                self.recent_table.setItem(row, col, item)

        self.recent_table.resizeRowsToContents()

        if hasattr(self, "recent_event_label"):
            if recent_notes:
                latest = recent_notes[0]
                status = "conferida" if latest.get("conferido") else "recebida"
                self.recent_event_label.setText(
                    f"Última nota: NF {latest.get('nf_number')} foi {status}."
                )
            else:
                self.recent_event_label.setText("Nenhuma movimentação recente.")

    def show_page(self, _page_key, animated=True):
        return

    def _make_filter_icon(self):
        pixmap = QtGui.QPixmap(18, 18)
        pixmap.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QColor("#F8FAFC"))
        funnel = QtGui.QPolygon(
            [
                QtCore.QPoint(3, 4),
                QtCore.QPoint(15, 4),
                QtCore.QPoint(10, 10),
                QtCore.QPoint(10, 15),
                QtCore.QPoint(8, 15),
                QtCore.QPoint(8, 10),
            ]
        )
        painter.drawPolygon(funnel)
        painter.end()
        return QtGui.QIcon(pixmap)

    def _set_conference_period(self, period):
        self.conference_period = period
        for key, action in getattr(self, "conference_period_actions", {}).items():
            action.setChecked(key == period)
        if hasattr(self, "_update_conferente_counter"):
            self._update_conferente_counter(getattr(self, "last_visible_notes", None))
