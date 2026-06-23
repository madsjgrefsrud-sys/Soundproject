from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPushButton

from app.config import Config
from app.gui.widgets import ButtonWidget, FaderWidget


def make_config(tmp_path):
    return Config(path=tmp_path / "config.json")


def test_button_widget_shows_configured_label(qtbot, tmp_path):
    config = make_config(tmp_path)
    config.buttons["60"] = {"type": "gamepad", "value": 1, "label": "Mute"}

    widget = ButtonWidget(0, "60", config, on_edit=lambda key: None)
    qtbot.addWidget(widget)

    assert widget.name_lbl.text() == "Mute"
    assert widget.type_lbl.text() == "gamepad"


def test_button_widget_click_calls_on_edit_with_note_key(qtbot, tmp_path):
    config = make_config(tmp_path)
    edited = []

    widget = ButtonWidget(0, "60", config, on_edit=lambda key: edited.append(key))
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget, Qt.MouseButton.LeftButton)

    assert edited == ["60"]


def test_button_widget_refresh_picks_up_config_changes(qtbot, tmp_path):
    config = make_config(tmp_path)
    config.buttons["60"] = {"type": "gamepad", "value": 1, "label": "Old"}
    widget = ButtonWidget(0, "60", config, on_edit=lambda key: None)
    qtbot.addWidget(widget)

    config.buttons["60"]["label"] = "New"
    widget.refresh()

    assert widget.name_lbl.text() == "New"


def test_button_widget_set_active_toggles_state(qtbot, tmp_path):
    config = make_config(tmp_path)
    widget = ButtonWidget(0, "60", config, on_edit=lambda key: None)
    qtbot.addWidget(widget)

    widget.set_active(True)
    assert widget._active is True

    widget.set_active(False)
    assert widget._active is False


def test_fader_widget_set_value_updates_percentage_label(qtbot, tmp_path):
    config = make_config(tmp_path)
    widget = FaderWidget("1", config, on_edit=lambda key: None)
    qtbot.addWidget(widget)

    widget.set_value(127)

    assert widget.pct_lbl.text() == "100%"


def test_fader_widget_edit_button_calls_on_edit_with_cc_key(qtbot, tmp_path):
    config = make_config(tmp_path)
    edited = []
    widget = FaderWidget("1", config, on_edit=lambda key: edited.append(key))
    qtbot.addWidget(widget)

    edit_btn = widget.findChild(QPushButton)
    qtbot.mouseClick(edit_btn, Qt.MouseButton.LeftButton)

    assert edited == ["1"]
