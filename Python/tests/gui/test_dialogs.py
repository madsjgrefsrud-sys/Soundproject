from app.config import Config
from app.gui.dialogs import ButtonEditDialog, SliderEditDialog


def make_config(tmp_path):
    return Config(path=tmp_path / "config.json")


def test_button_edit_dialog_save_writes_label_and_value(qtbot, tmp_path):
    config = make_config(tmp_path)
    config.buttons = {}
    dlg = ButtonEditDialog(None, "60", config)
    qtbot.addWidget(dlg)

    dlg.lbl_edit.setText("Mute")
    dlg.val_spin.setValue(5)
    dlg._save()

    assert config.buttons["60"] == {"type": "gamepad", "value": 5, "label": "Mute"}


def test_button_edit_dialog_save_persists_to_disk(qtbot, tmp_path):
    config = make_config(tmp_path)
    dlg = ButtonEditDialog(None, "60", config)
    qtbot.addWidget(dlg)

    dlg.lbl_edit.setText("Mute")
    dlg._save()

    reloaded = Config(path=tmp_path / "config.json")
    assert reloaded.buttons["60"]["label"] == "Mute"


def test_button_edit_dialog_clear_removes_entry(qtbot, tmp_path):
    config = make_config(tmp_path)
    config.buttons["60"] = {"type": "gamepad", "value": 1, "label": "Mute"}
    dlg = ButtonEditDialog(None, "60", config)
    qtbot.addWidget(dlg)

    dlg._clear()

    assert "60" not in config.buttons


def test_slider_edit_dialog_save_writes_chosen_app(qtbot, tmp_path):
    config = make_config(tmp_path)
    dlg = SliderEditDialog(None, "1", config)
    qtbot.addWidget(dlg)

    dlg.app_combo.setCurrentText("Spotify")
    dlg._save()

    assert config.sliders["1"] == {"app": "Spotify"}
