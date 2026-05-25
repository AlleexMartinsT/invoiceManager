from PySide6 import QtCore, QtWidgets

import utils_estoque as utils
from system.ui_components import make_label, make_panel


class SettingsMixin:
    ALL_MONTHS_TEXT = "Visualizar todos os meses do ano"

    def _make_all_months_control(self, parent):
        wrapper = QtWidgets.QWidget(parent)
        row = QtWidgets.QHBoxLayout(wrapper)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)

        checkbox = QtWidgets.QCheckBox("", wrapper)
        checkbox.setFixedWidth(24)
        checkbox.setChecked(self.settings.get("visualizar_todos_meses", False))
        checkbox.stateChanged.connect(self._toggle_all_months)

        label = make_label(wrapper, self.ALL_MONTHS_TEXT, muted=True)
        label.setWordWrap(False)
        label.setMinimumWidth(label.sizeHint().width() + 8)
        label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        label.setCursor(QtCore.Qt.PointingHandCursor)
        label.mousePressEvent = lambda event: checkbox.toggle()

        row.addStretch(1)
        row.addWidget(checkbox, 0, QtCore.Qt.AlignVCenter)
        row.addWidget(label, 1)
        row.addStretch(1)
        return wrapper, checkbox

    def _build_settings_page(self, parent):
        layout = QtWidgets.QVBoxLayout(parent)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        card = make_panel(parent, "surface")
        card_layout = QtWidgets.QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(10)
        card_layout.addWidget(make_label(card, "Configurações", hero=True, anchor="center"))

        checkbox_control, self.var_all_months = self._make_all_months_control(card)
        card_layout.addWidget(checkbox_control)

        layout.addWidget(card)
        layout.addStretch(1)

    def _set_all_months_enabled(self, enabled):
        enabled = bool(enabled)
        current = bool(self.settings.get("visualizar_todos_meses", False))
        if current == enabled:
            return

        self.settings["visualizar_todos_meses"] = enabled
        utils.save_settings(self.settings)

        if hasattr(self, "var_all_months") and self.var_all_months.isChecked() != enabled:
            self.var_all_months.blockSignals(True)
            self.var_all_months.setChecked(enabled)
            self.var_all_months.blockSignals(False)

        if hasattr(self, "_settings_dialog_checkbox") and self._settings_dialog_checkbox.isChecked() != enabled:
            self._settings_dialog_checkbox.blockSignals(True)
            self._settings_dialog_checkbox.setChecked(enabled)
            self._settings_dialog_checkbox.blockSignals(False)

        if hasattr(self, "_refresh_scope_badge"):
            self._refresh_scope_badge()

        cached_notes = list(getattr(self, "_all_notes_cache", [])) if hasattr(self, "_all_notes_cache") else None
        if cached_notes is not None:
            QtCore.QTimer.singleShot(0, lambda notes=cached_notes: self.refresh_table(notes=notes))
        else:
            QtCore.QTimer.singleShot(0, self.refresh_table)

    def _toggle_all_months(self, state=None):
        if state is None:
            enabled = self.var_all_months.isChecked()
        else:
            enabled = bool(state)
        self._set_all_months_enabled(enabled)

    def show_settings_page(self):
        win = QtWidgets.QDialog(self)
        win.setWindowTitle("Configurações")
        win.setModal(True)
        win.setFixedSize(420, 160)
        layout = QtWidgets.QVBoxLayout(win)

        card = make_panel(win, "surface")
        card_layout = QtWidgets.QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(10)
        card_layout.addWidget(make_label(card, "Configurações", hero=True, anchor="center"))

        checkbox_control, cb = self._make_all_months_control(card)
        self._settings_dialog_checkbox = cb
        card_layout.addWidget(checkbox_control)

        layout.addWidget(card)
        self._exec_modal_dialog(win)
