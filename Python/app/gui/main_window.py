from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QFrame, QSizePolicy
)

from . import theme
from .widgets import ButtonWidget, FaderWidget
from .dialogs import ButtonEditDialog, SliderEditDialog
from ..bridge import MidiBridge


class MainWindow(QMainWindow):
    def __init__(self, config):
        super().__init__()
        self.config      = config
        self.btn_widgets = {}
        self.sl_widgets  = {}
        self.bridge      = MidiBridge()

        self.setWindowTitle("Soundproject - Control Panel")
        self.setMinimumSize(900, 620)
        self.setStyleSheet(theme.STYLE_MAIN)

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

        fader_panel = self._make_fader_panel()
        fader_panel.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        body.addWidget(fader_panel)
        root.addLayout(body)

    def _make_header(self):
        hdr = QWidget()
        hdr.setFixedHeight(62)
        hdr.setStyleSheet(f"background-color: {theme.PANEL}; border-bottom: 1px solid {theme.BORDER};")
        h = QHBoxLayout(hdr)
        h.setContentsMargins(18, 0, 18, 0)
        h.setSpacing(16)

        title_lbl = QLabel("SOUNDPROJECT")
        title_lbl.setStyleSheet(f"color: {theme.TEXT}; font-size: 13px; font-weight: bold; letter-spacing: 2px;")
        h.addWidget(title_lbl)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet(f"color: {theme.BORDER};")
        h.addWidget(sep)

        midi_lbl = QLabel("MIDI:")
        midi_lbl.setStyleSheet(f"color: {theme.TEXT_DIM}; font-size: 10px; font-weight: bold;")
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
            lbl = QLabel("No devices")
            lbl.setStyleSheet(
                f"color: {theme.TEXT_DIM}; font-size: 10px; font-family: {theme.MONO_FAMILY}; "
                f"background: {theme.CARD}; border: 1px solid {theme.BORDER}; "
                f"border-radius: 4px; padding: 2px 8px;"
            )
            self.midi_devices_layout.addWidget(lbl)
            return

        for port_name in ports:
            is_esp = "ESP32" in port_name or "MIDI" in port_name
            color  = theme.ACCENT if is_esp else theme.TEXT_DIM
            short  = port_name[:22] + "..." if len(port_name) > 22 else port_name
            lbl    = QLabel(short)
            # Device names stay monospace - the one place this app keeps the
            # old "terminal" font, since it's genuinely technical/log-like content.
            lbl.setStyleSheet(
                f"color: {color}; font-size: 10px; font-family: {theme.MONO_FAMILY}; "
                f"background: {theme.CARD}; border: 1px solid {theme.BORDER}; "
                f"border-radius: 4px; padding: 2px 8px;"
            )
            lbl.setToolTip(port_name)
            self.midi_devices_layout.addWidget(lbl)

    def _make_grid(self):
        outer = QWidget()
        vbox  = QVBoxLayout(outer)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(8)

        lbl = QLabel("BUTTON MATRIX  4 x 5")
        lbl.setStyleSheet(f"color: {theme.TEXT_DIM}; font-size: 9px; font-weight: bold;")
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

    def _make_fader_panel(self):
        outer = QWidget()
        h     = QHBoxLayout(outer)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(10)
        for cc_key in ["1", "2"]:
            w = FaderWidget(cc_key, self.config, self._edit_slider)
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


def apply_palette(app: QApplication):
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window,          QColor(theme.BG))
    palette.setColor(QPalette.ColorRole.WindowText,      QColor(theme.TEXT))
    palette.setColor(QPalette.ColorRole.Base,            QColor(theme.CARD))
    palette.setColor(QPalette.ColorRole.AlternateBase,   QColor(theme.PANEL))
    palette.setColor(QPalette.ColorRole.Text,            QColor(theme.TEXT))
    palette.setColor(QPalette.ColorRole.Button,          QColor(theme.CARD))
    palette.setColor(QPalette.ColorRole.ButtonText,      QColor(theme.TEXT))
    palette.setColor(QPalette.ColorRole.Highlight,       QColor(theme.ACCENT))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(theme.TEXT))
    app.setPalette(palette)
