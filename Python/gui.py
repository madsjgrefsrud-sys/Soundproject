"""
Soundproject – GUI (PyQt6)
Run: python main.py
Requirements: pip install PyQt6 mido
"""

import sys
import threading

from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QColor, QFont, QPainter, QPen, QBrush, QPalette, QLinearGradient
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QComboBox, QLineEdit,
    QDialog, QDialogButtonBox, QFrame, QScrollArea, QSizePolicy,
    QStatusBar, QSlider, QSpinBox
)

from config import Config


# ─────────────────────────────────────────────────────────────
#  COLOR PALETTE
# ─────────────────────────────────────────────────────────────
BG       = "#0e0f14"
PANEL    = "#16181f"
CARD     = "#1c1f2b"
BORDER   = "#2a2d3a"
ACCENT   = "#4f8ef7"
ACCENT2  = "#7c5cbf"
ACTIVE   = "#3ddc84"
TEXT     = "#e8eaf0"
TEXT_DIM = "#6b6f85"
BTN_HOV  = "#252836"

STYLE_MAIN = f"""
QMainWindow, QWidget {{
    background-color: {BG};
    color: {TEXT};
    font-family: 'Consolas', 'Courier New', monospace;
}}
QLabel {{ color: {TEXT}; background: transparent; }}
QLineEdit, QSpinBox, QComboBox {{
    background-color: {CARD};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 4px 8px;
    font-family: 'Consolas', monospace;
}}
QComboBox::drop-down {{ border: none; }}
QComboBox QAbstractItemView {{
    background-color: {CARD};
    color: {TEXT};
    selection-background-color: {ACCENT};
}}
QPushButton {{
    background-color: {CARD};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 5px;
    padding: 5px 14px;
    font-family: 'Consolas', monospace;
}}
QPushButton:hover {{ background-color: {BTN_HOV}; border-color: {ACCENT}; }}
QPushButton#accent {{ background-color: {ACCENT}; color: {BG}; border: none; font-weight: bold; }}
QPushButton#accent:hover {{ background-color: #6aa3ff; }}
QPushButton#accent2 {{ background-color: {ACCENT2}; color: {TEXT}; border: none; font-weight: bold; }}
QScrollArea {{ border: none; background: transparent; }}
QStatusBar {{ background-color: {PANEL}; color: {TEXT_DIM}; font-size: 10px; }}
"""


# ─────────────────────────────────────────────────────────────
#  MIDI SIGNAL BRIDGE  (thread-safe → Qt)
# ─────────────────────────────────────────────────────────────
class MidiBridge(QObject):
    note_on  = pyqtSignal(int, int)
    note_off = pyqtSignal(int, int)
    cc       = pyqtSignal(int, int)

    def __init__(self):
        super().__init__()
        self._cc_ema = {}

    def emit_note_on(self, note, vel):  self.note_on.emit(note, vel)
    def emit_note_off(self, note, vel): self.note_off.emit(note, vel)

    def emit_cc(self, num, val):
        prev   = self._cc_ema.get(num, val)
        smooth = int(prev * 0.6 + val * 0.4)
        # Snap to endpoints so we always reach 0 and 127
        if val >= 124: smooth = 127
        if val <= 3:   smooth = 0
        self._cc_ema[num] = smooth
        self.cc.emit(num, smooth)


# ─────────────────────────────────────────────────────────────
#  BUTTON EDIT DIALOG
# ─────────────────────────────────────────────────────────────
class ButtonEditDialog(QDialog):
    def __init__(self, parent, note_key, config):
        super().__init__(parent)
        self.note_key = note_key
        self.config   = config
        self.setWindowTitle(f"Edit button – MIDI note {note_key}")
        self.setFixedSize(360, 280)
        self.setStyleSheet(STYLE_MAIN)

        btn_data = config.buttons.get(note_key, {"type": "gamepad", "value": 1, "label": ""})
        self._is_configured = note_key in config.buttons

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 16)

        title = QLabel(f"⚙  BUTTON  –  NOTE {note_key}")
        title.setStyleSheet(f"color: {ACCENT}; font-size: 13px; font-weight: bold;")
        layout.addWidget(title)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"color: {BORDER};")
        layout.addWidget(line)

        form = QGridLayout()
        form.setSpacing(10)

        form.addWidget(QLabel("Label:"), 0, 0)
        self.lbl_edit = QLineEdit(btn_data.get("label", ""))
        form.addWidget(self.lbl_edit, 0, 1)

        form.addWidget(QLabel("Gamepad button (1–16):"), 1, 0)
        self.val_spin = QSpinBox()
        self.val_spin.setRange(1, 16)
        self.val_spin.setValue(int(btn_data.get("value", 1)))
        form.addWidget(self.val_spin, 1, 1)

        layout.addLayout(form)
        layout.addStretch()

        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setStyleSheet(f"color: {BORDER};")
        layout.addWidget(line2)

        btn_row = QHBoxLayout()

        save_btn = QPushButton("  Save  ")
        save_btn.setObjectName("accent")
        save_btn.clicked.connect(self._save)
        btn_row.addWidget(save_btn)

        if self._is_configured:
            clear_btn = QPushButton("  🗑 Remove  ")
            clear_btn.setStyleSheet(
                "background-color: #3a1a1a; color: #ff6b6b; border: 1px solid #5a2a2a; "
                "border-radius: 5px; padding: 5px 14px;"
            )
            clear_btn.clicked.connect(self._clear)
            btn_row.addWidget(clear_btn)

        cancel_btn = QPushButton("  Cancel  ")
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


# ─────────────────────────────────────────────────────────────
#  SLIDER EDIT DIALOG
# ─────────────────────────────────────────────────────────────
class SliderEditDialog(QDialog):
    def __init__(self, parent, cc_key, config):
        super().__init__(parent)
        self.cc_key = cc_key
        self.config = config
        self.setWindowTitle(f"Edit Slider – CC {cc_key}")
        self.setFixedSize(320, 190)
        self.setStyleSheet(STYLE_MAIN)

        sl_data = config.sliders.get(cc_key, {"app": "Chrome"})
        layout  = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 16)

        title = QLabel(f"⚙  SLIDER  –  CC {cc_key}")
        title.setStyleSheet(f"color: {ACCENT2}; font-size: 13px; font-weight: bold;")
        layout.addWidget(title)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"color: {BORDER};")
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
        save_btn   = QPushButton("  Save  ")
        cancel_btn = QPushButton("  Cancel  ")
        save_btn.setObjectName("accent2")
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


# ─────────────────────────────────────────────────────────────
#  BUTTON WIDGET
# ─────────────────────────────────────────────────────────────
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
        self.num_lbl.setStyleSheet(f"color: {TEXT_DIM}; font-size: 16px; font-weight: bold; background: transparent;")
        layout.addWidget(self.num_lbl)

        btn_data = config.buttons.get(note_key, {})
        self.name_lbl = QLabel(btn_data.get("label", "–")[:12] or "–")
        self.name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_lbl.setStyleSheet(f"color: {TEXT}; font-size: 9px; font-weight: bold; background: transparent;")
        layout.addWidget(self.name_lbl)

        self.type_lbl = QLabel(self._type_text(btn_data))
        self.type_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.type_lbl.setStyleSheet(f"color: {ACCENT}; font-size: 8px; background: transparent;")
        layout.addWidget(self.type_lbl)

        self.val_lbl = QLabel(self._val_text(btn_data))
        self.val_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.val_lbl.setStyleSheet(f"color: {TEXT_DIM}; font-size: 8px; background: transparent;")
        layout.addWidget(self.val_lbl)

    def _type_text(self, btn_data):
        t = btn_data.get("type", "")
        return {"gamepad": "🎮 gamepad", "macro": "⚡ macro", "app_control": "🖥 app"}.get(t, t)

    def _val_text(self, btn_data):
        val = btn_data.get("value", "")
        return f"val: {val}" if val != "" else ""

    def refresh(self):
        btn_data = self.config.buttons.get(self.note_key, {})
        self.name_lbl.setText(btn_data.get("label", "–")[:12] or "–")
        self.type_lbl.setText(self._type_text(btn_data))
        self.val_lbl.setText(self._val_text(btn_data))

    def set_active(self, active):
        self._active = active
        col = ACTIVE if active else TEXT_DIM
        self.num_lbl.setStyleSheet(f"color: {col}; font-size: 18px; font-weight: bold; background: transparent;")
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self._active:
            bg = QColor(ACTIVE); bg.setAlpha(35)
            border = QColor(ACTIVE)
        else:
            bg     = QColor(CARD)
            border = QColor(BORDER)
        p.setBrush(QBrush(bg))
        p.setPen(QPen(border, 1))
        p.drawRoundedRect(1, 1, self.width()-2, self.height()-2, 8, 8)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.on_edit(self.note_key)


# ─────────────────────────────────────────────────────────────
#  VOLUME BAR WIDGET
# ─────────────────────────────────────────────────────────────
class VolumeBar(QWidget):
    """Visual volume indicator – read-only, reflects MIDI CC value."""
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

        w, h   = self.width(), self.height()
        bar_w  = 14
        x      = (w - bar_w) // 2

        p.setBrush(QBrush(QColor("#252836")))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(x, 0, bar_w, h, 7, 7)

        fill_h = int((self._value / 127.0) * h)
        if fill_h > 0:
            grad = QLinearGradient(0, h, 0, h - fill_h)
            grad.setColorAt(0, QColor(ACCENT))
            grad.setColorAt(1, QColor("#88c0ff"))
            p.setBrush(QBrush(grad))
            p.drawRoundedRect(x, h - fill_h, bar_w, fill_h, 7, 7)

        if fill_h > 4:
            p.setBrush(QBrush(QColor("white")))
            p.setOpacity(0.9)
            p.drawRoundedRect(x, h - fill_h - 3, bar_w, 6, 3, 3)


# ─────────────────────────────────────────────────────────────
#  SLIDER WIDGET
# ─────────────────────────────────────────────────────────────
class SliderWidget(QWidget):
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

        cc_lbl = QLabel(f"SLIDER  {self.cc_key}")
        cc_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cc_lbl.setStyleSheet(f"color: {ACCENT2}; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        layout.addWidget(cc_lbl)

        sl_data = self.config.sliders.get(self.cc_key, {"app": "?"})
        self.app_lbl = QLabel(sl_data.get("app", "?"))
        self.app_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.app_lbl.setStyleSheet(f"""
            color: {TEXT}; font-size: 12px; font-weight: bold;
            background: {CARD}; border: 1px solid {BORDER};
            border-radius: 4px; padding: 3px 6px;
        """)
        self.app_lbl.setWordWrap(True)
        layout.addWidget(self.app_lbl)

        self.vol_bar = VolumeBar()
        layout.addWidget(self.vol_bar, stretch=1)

        self.pct_lbl = QLabel("50%")
        self.pct_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pct_lbl.setStyleSheet(f"color: {TEXT}; font-size: 16px; font-weight: bold;")
        layout.addWidget(self.pct_lbl)

        edit_btn = QPushButton("✎ Edit")
        edit_btn.setFixedHeight(28)
        edit_btn.setStyleSheet("font-size: 11px;")
        edit_btn.clicked.connect(lambda: self.on_edit(self.cc_key))
        layout.addWidget(edit_btn)

    def set_value(self, val):
        self.vol_bar.set_value(val)
        self.pct_lbl.setText(f"{int(val / 127 * 100)}%")

    def refresh(self):
        sl_data = self.config.sliders.get(self.cc_key, {"app": "?"})
        self.app_lbl.setText(sl_data.get("app", "?"))

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QBrush(QColor(PANEL)))
        p.setPen(QPen(QColor(BORDER), 1))
        p.drawRoundedRect(0, 0, self.width()-1, self.height()-1, 8, 8)


# ─────────────────────────────────────────────────────────────
#  MAIN WINDOW
# ─────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config      = Config()
        self.btn_widgets = {}
        self.sl_widgets  = {}
        self.bridge      = MidiBridge()

        self.setWindowTitle("Soundproject – Control Panel")
        self.setMinimumSize(900, 620)
        self.setStyleSheet(STYLE_MAIN)

        self._build_ui()
        self._connect_signals()
        self._scan_midi_ports()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._make_header())

        body = QHBoxLayout()
        body.setContentsMargins(14, 12, 14, 12)
        body.setSpacing(12)
        body.addWidget(self._make_grid(), stretch=1)

        slider_panel = self._make_slider_panel()
        slider_panel.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        body.addWidget(slider_panel)
        root.addLayout(body)

    def _make_header(self):
        hdr = QWidget()
        hdr.setFixedHeight(62)
        hdr.setStyleSheet(f"background-color: {PANEL}; border-bottom: 1px solid {BORDER};")
        h = QHBoxLayout(hdr)
        h.setContentsMargins(18, 0, 18, 0)
        h.setSpacing(16)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet(f"color: {BORDER};")
        h.addWidget(sep)

        midi_lbl = QLabel("MIDI:")
        midi_lbl.setStyleSheet(f"color: {TEXT_DIM}; font-size: 10px; font-weight: bold;")
        h.addWidget(midi_lbl)

        self.midi_devices_layout = QHBoxLayout()
        self.midi_devices_layout.setSpacing(8)
        h.addLayout(self.midi_devices_layout)
        h.addStretch()

        return hdr

    def _scan_midi_ports(self):
        while self.midi_devices_layout.count():
            item = self.midi_devices_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        try:
            import mido
            ports = mido.get_input_names()
        except Exception:
            ports = []

        if not ports:
            lbl = QLabel("● No devices")
            lbl.setStyleSheet(
                f"color: {TEXT_DIM}; font-size: 10px; background: {CARD}; "
                f"border: 1px solid {BORDER}; border-radius: 4px; padding: 2px 8px;"
            )
            self.midi_devices_layout.addWidget(lbl)
            return

        for port_name in ports:
            is_esp = "ESP32" in port_name or "MIDI" in port_name
            color  = ACTIVE if is_esp else ACCENT2
            short  = port_name[:22] + "…" if len(port_name) > 22 else port_name
            lbl    = QLabel(f"●  {short}")
            lbl.setStyleSheet(
                f"color: {color}; font-size: 10px; background: {CARD}; "
                f"border: 1px solid {BORDER}; border-radius: 4px; padding: 2px 8px;"
            )
            lbl.setToolTip(port_name)
            self.midi_devices_layout.addWidget(lbl)

    def _make_grid(self):
        outer = QWidget()
        vbox  = QVBoxLayout(outer)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(8)

        lbl = QLabel("BUTTON MATRIX  4 × 5")
        lbl.setStyleSheet(f"color: {TEXT_DIM}; font-size: 9px; font-weight: bold;")
        vbox.addWidget(lbl)

        grid_w = QWidget()
        grid_w.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        grid   = QGridLayout(grid_w)
        grid.setSpacing(8)
        grid.setContentsMargins(0, 0, 0, 0)

        for i in range(4):
            grid.setColumnStretch(i, 1)
        for i in range(5):
            grid.setRowStretch(i, 1)

        notes = sorted(int(k) for k in self.config.buttons.keys())
        while len(notes) < 20:
            notes.append(60 + len(notes))

        for i, note in enumerate(notes[:20]):
            note_key = str(note)
            w = ButtonWidget(i, note_key, self.config, self._edit_button)
            self.btn_widgets[note_key] = w
            grid.addWidget(w, i // 4, i % 4)

        vbox.addWidget(grid_w, stretch=1)
        return outer

    def _make_slider_panel(self):
        outer = QWidget()
        h     = QHBoxLayout(outer)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(10)
        for cc_key in ["1", "2"]:
            w = SliderWidget(cc_key, self.config, self._edit_slider)
            self.sl_widgets[cc_key] = w
            h.addWidget(w)
        return outer

    def _connect_signals(self):
        self.bridge.note_on.connect(self._on_note_on)
        self.bridge.note_off.connect(self._on_note_off)
        self.bridge.cc.connect(self._on_cc)

    def _on_note_on(self, note, vel):
        note_key = str(note)
        if note_key in self.btn_widgets:
            self.btn_widgets[note_key].set_active(True)

    def _on_note_off(self, note, vel):
        note_key = str(note)
        if note_key in self.btn_widgets:
            self.btn_widgets[note_key].set_active(False)

    def _on_cc(self, num, val):
        cc_key = str(num)
        if cc_key in self.sl_widgets:
            self.sl_widgets[cc_key].set_value(val)

    def _edit_button(self, note_key):
        dlg = ButtonEditDialog(self, note_key, self.config)
        if dlg.exec():
            for w in self.btn_widgets.values():
                w.refresh()

    def _edit_slider(self, cc_key):
        dlg = SliderEditDialog(self, cc_key, self.config)
        if dlg.exec():
            for w in self.sl_widgets.values():
                w.refresh()


# ─────────────────────────────────────────────────────────────
#  STANDALONE ENTRY POINT (for testing GUI only, no MIDI)
# ─────────────────────────────────────────────────────────────
def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window,          QColor(BG))
    palette.setColor(QPalette.ColorRole.WindowText,      QColor(TEXT))
    palette.setColor(QPalette.ColorRole.Base,            QColor(CARD))
    palette.setColor(QPalette.ColorRole.AlternateBase,   QColor(PANEL))
    palette.setColor(QPalette.ColorRole.Text,            QColor(TEXT))
    palette.setColor(QPalette.ColorRole.Button,          QColor(CARD))
    palette.setColor(QPalette.ColorRole.ButtonText,      QColor(TEXT))
    palette.setColor(QPalette.ColorRole.Highlight,       QColor(ACCENT))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(BG))
    app.setPalette(palette)

    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
