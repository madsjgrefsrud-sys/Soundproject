from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QLinearGradient
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QSizePolicy

from . import theme


class ButtonWidget(QWidget):
    def __init__(self, index, note_key, config, on_edit):
        super().__init__()
        self.note_key = note_key
        self.config   = config
        self.on_edit  = on_edit
        self._active  = False
        self.setMinimumSize(100, 90)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(1)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.num_lbl = QLabel(str(index + 1))
        self.num_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.num_lbl)

        btn_data = config.buttons.get(note_key, {})
        self.name_lbl = QLabel(btn_data.get("label", "-")[:12] or "-")
        self.name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_lbl.setStyleSheet(f"color: {theme.TEXT}; font-size: 9px; font-weight: bold; background: transparent;")
        layout.addWidget(self.name_lbl)

        self.type_lbl = QLabel(self._type_text(btn_data))
        self.type_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.type_lbl.setStyleSheet(f"color: {theme.TEXT_DIM}; font-size: 8px; background: transparent;")
        layout.addWidget(self.type_lbl)

        self.val_lbl = QLabel(self._val_text(btn_data))
        self.val_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.val_lbl.setStyleSheet(f"color: {theme.TEXT_DIM}; font-size: 8px; background: transparent;")
        layout.addWidget(self.val_lbl)

        self._apply_number_style()

    def _type_text(self, btn_data):
        t = btn_data.get("type", "")
        return {"gamepad": "gamepad", "macro": "macro", "app_control": "app"}.get(t, t)

    def _val_text(self, btn_data):
        val = btn_data.get("value", "")
        return f"val: {val}" if val != "" else ""

    def _apply_number_style(self):
        color = theme.ACCENT if self._active else theme.TEXT_DIM
        self.num_lbl.setStyleSheet(f"color: {color}; font-size: 18px; font-weight: bold; background: transparent;")

    def refresh(self):
        btn_data = self.config.buttons.get(self.note_key, {})
        self.name_lbl.setText(btn_data.get("label", "-")[:12] or "-")
        self.type_lbl.setText(self._type_text(btn_data))
        self.val_lbl.setText(self._val_text(btn_data))

    def set_active(self, active):
        self._active = active
        self._apply_number_style()
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self._active:
            bg     = QColor(theme.ACCENT_BG)
            border = QColor(theme.ACCENT)
        else:
            bg     = QColor(theme.CARD)
            border = QColor(theme.BORDER)
        p.setBrush(QBrush(bg))
        p.setPen(QPen(border, 1))
        p.drawRoundedRect(1, 1, self.width() - 2, self.height() - 2, 8, 8)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.on_edit(self.note_key)


class _FaderTrack(QWidget):
    """Read-only visual fader fill, reflects a 0-127 MIDI CC value."""

    def __init__(self):
        super().__init__()
        self._value = 64
        self.setMinimumHeight(200)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def set_value(self, val):
        self._value = max(0, min(127, val))
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h  = self.width(), self.height()
        bar_w = 14
        x     = (w - bar_w) // 2

        p.setBrush(QBrush(QColor(theme.CARD)))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(x, 0, bar_w, h, 7, 7)

        fill_h = int((self._value / 127.0) * h)
        if fill_h > 0:
            grad = QLinearGradient(0, h, 0, h - fill_h)
            grad.setColorAt(0, QColor(theme.FADER_BOTTOM))
            grad.setColorAt(1, QColor(theme.FADER_TOP))
            p.setBrush(QBrush(grad))
            p.drawRoundedRect(x, h - fill_h, bar_w, fill_h, 7, 7)

        if fill_h > 4:
            p.setBrush(QBrush(QColor(theme.FADER_CAP)))
            p.setOpacity(0.95)
            p.drawRoundedRect(x, h - fill_h - 3, bar_w, 6, 3, 3)


class FaderWidget(QWidget):
    def __init__(self, cc_key, config, on_edit):
        super().__init__()
        self.cc_key  = cc_key
        self.config  = config
        self.on_edit = on_edit
        self.setFixedWidth(130)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 16, 12, 12)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        cc_lbl = QLabel(f"FADER  {self.cc_key}")
        cc_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cc_lbl.setStyleSheet(f"color: {theme.ACCENT}; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        layout.addWidget(cc_lbl)

        sl_data = self.config.sliders.get(self.cc_key, {"app": "?"})
        self.app_lbl = QLabel(sl_data.get("app", "?"))
        self.app_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.app_lbl.setStyleSheet(f"""
            color: {theme.TEXT}; font-size: 12px; font-weight: bold;
            background: {theme.CARD}; border: 1px solid {theme.BORDER};
            border-radius: 4px; padding: 3px 6px;
        """)
        self.app_lbl.setWordWrap(True)
        layout.addWidget(self.app_lbl)

        self.track = _FaderTrack()
        layout.addWidget(self.track, stretch=1)

        self.pct_lbl = QLabel("50%")
        self.pct_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pct_lbl.setStyleSheet(f"color: {theme.TEXT}; font-size: 16px; font-weight: bold;")
        layout.addWidget(self.pct_lbl)

        edit_btn = QPushButton("Edit")
        edit_btn.setFixedHeight(28)
        edit_btn.setStyleSheet("font-size: 11px;")
        edit_btn.clicked.connect(lambda: self.on_edit(self.cc_key))
        layout.addWidget(edit_btn)

    def set_value(self, val):
        self.track.set_value(val)
        self.pct_lbl.setText(f"{int(val / 127 * 100)}%")

    def refresh(self):
        sl_data = self.config.sliders.get(self.cc_key, {"app": "?"})
        self.app_lbl.setText(sl_data.get("app", "?"))

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QBrush(QColor(theme.PANEL)))
        p.setPen(QPen(QColor(theme.BORDER), 1))
        p.drawRoundedRect(0, 0, self.width() - 1, self.height() - 1, 8, 8)
