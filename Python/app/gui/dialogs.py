from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QLineEdit, QSpinBox, QComboBox, QPushButton, QFrame, QDialogButtonBox
)

from . import theme


class ButtonEditDialog(QDialog):
    def __init__(self, parent, note_key, config):
        super().__init__(parent)
        self.note_key = note_key
        self.config   = config
        self.setWindowTitle(f"Edit button - MIDI note {note_key}")
        self.setFixedSize(360, 280)
        self.setStyleSheet(theme.STYLE_MAIN)

        btn_data = config.buttons.get(note_key, {"type": "gamepad", "value": 1, "label": ""})
        self._is_configured = note_key in config.buttons

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 16)

        title = QLabel(f"BUTTON - NOTE {note_key}")
        title.setStyleSheet(f"color: {theme.ACCENT}; font-size: 13px; font-weight: bold;")
        layout.addWidget(title)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"color: {theme.BORDER};")
        layout.addWidget(line)

        form = QGridLayout()
        form.setSpacing(10)

        form.addWidget(QLabel("Label:"), 0, 0)
        self.lbl_edit = QLineEdit(btn_data.get("label", ""))
        form.addWidget(self.lbl_edit, 0, 1)

        form.addWidget(QLabel("Gamepad button (1-16):"), 1, 0)
        self.val_spin = QSpinBox()
        self.val_spin.setRange(1, 16)
        self.val_spin.setValue(int(btn_data.get("value", 1)))
        form.addWidget(self.val_spin, 1, 1)

        layout.addLayout(form)
        layout.addStretch()

        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setStyleSheet(f"color: {theme.BORDER};")
        layout.addWidget(line2)

        btn_row = QHBoxLayout()

        save_btn = QPushButton("Save")
        save_btn.setObjectName("accent")
        save_btn.clicked.connect(self._save)
        btn_row.addWidget(save_btn)

        if self._is_configured:
            clear_btn = QPushButton("Remove")
            clear_btn.setStyleSheet(
                "background-color: #2a1012; color: #ff6b74; border: 1px solid #4a1a20; "
                "border-radius: 5px; padding: 5px 14px;"
            )
            clear_btn.clicked.connect(self._clear)
            btn_row.addWidget(clear_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        layout.addLayout(btn_row)

    def _save(self):
        self.config.buttons[self.note_key] = {
            "type":  "gamepad",
            "value": self.val_spin.value(),
            "label": self.lbl_edit.text()
        }
        self.config.data["buttons"] = self.config.buttons
        self.config.save()
        self.accept()

    def _clear(self):
        if self.note_key in self.config.buttons:
            del self.config.buttons[self.note_key]
        self.config.data["buttons"] = self.config.buttons
        self.config.save()
        self.accept()


class SliderEditDialog(QDialog):
    def __init__(self, parent, cc_key, config):
        super().__init__(parent)
        self.cc_key = cc_key
        self.config = config
        self.setWindowTitle(f"Edit Fader - CC {cc_key}")
        self.setFixedSize(320, 190)
        self.setStyleSheet(theme.STYLE_MAIN)

        sl_data = config.sliders.get(cc_key, {"app": "Chrome"})
        layout  = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 16)

        title = QLabel(f"FADER - CC {cc_key}")
        title.setStyleSheet(f"color: {theme.ACCENT}; font-size: 13px; font-weight: bold;")
        layout.addWidget(title)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"color: {theme.BORDER};")
        layout.addWidget(line)

        form = QGridLayout()
        form.addWidget(QLabel("Link to app:"), 0, 0)
        self.app_combo = QComboBox()
        self.app_combo.addItems(list(config.apps.keys()))
        self.app_combo.setCurrentText(sl_data.get("app", "Chrome"))
        form.addWidget(self.app_combo, 0, 1)
        layout.addLayout(form)
        layout.addStretch()

        btns       = QDialogButtonBox()
        save_btn   = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        save_btn.setObjectName("accent")
        save_btn.clicked.connect(self._save)
        cancel_btn.clicked.connect(self.reject)
        btns.addButton(save_btn,   QDialogButtonBox.ButtonRole.AcceptRole)
        btns.addButton(cancel_btn, QDialogButtonBox.ButtonRole.RejectRole)
        layout.addWidget(btns)

    def _save(self):
        self.config.sliders[self.cc_key] = {"app": self.app_combo.currentText()}
        self.config.data["sliders"] = self.config.sliders
        self.config.save()
        self.accept()
