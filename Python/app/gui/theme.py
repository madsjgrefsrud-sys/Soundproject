BG           = "#0a0a0b"
PANEL        = "#111113"
CARD         = "#171718"
BORDER       = "#2a2a2c"
TEXT         = "#e8e8ea"
TEXT_DIM     = "#76767a"
ACCENT       = "#e0303f"
ACCENT_BG    = "#2a1012"
ACCENT_GLOW  = "rgba(224,48,63,0.55)"
FADER_TOP    = "#ff5a64"
FADER_BOTTOM = "#c81e2e"
FADER_CAP    = "#f2f2f3"

FONT_FAMILY = "'Segoe UI', system-ui, sans-serif"
MONO_FAMILY = "'Consolas', 'Courier New', monospace"

STYLE_MAIN = f"""
QMainWindow, QWidget {{
    background-color: {BG};
    color: {TEXT};
    font-family: {FONT_FAMILY};
}}
QLabel {{ color: {TEXT}; background: transparent; }}
QLineEdit, QSpinBox, QComboBox {{
    background-color: {CARD};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 4px 8px;
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
}}
QPushButton:hover {{ background-color: #1f1f22; border-color: {ACCENT}; }}
QPushButton#accent {{ background-color: {ACCENT}; color: {TEXT}; border: none; font-weight: bold; }}
QPushButton#accent:hover {{ background-color: #ff4a58; }}
QScrollArea {{ border: none; background: transparent; }}
QStatusBar {{ background-color: {PANEL}; color: {TEXT_DIM}; font-size: 10px; }}
"""
