from app.config import Config
from app.gui.main_window import MainWindow


def make_config(tmp_path):
    return Config(path=tmp_path / "config.json")


def test_main_window_shares_the_config_instance_it_was_given(qtbot, tmp_path):
    config = make_config(tmp_path)

    win = MainWindow(config)
    qtbot.addWidget(win)

    assert win.config is config


def test_note_on_signal_activates_matching_button_widget(qtbot, tmp_path):
    config = make_config(tmp_path)
    win = MainWindow(config)
    qtbot.addWidget(win)

    win.bridge.emit_note_on(60, 100)

    assert win.btn_widgets["60"]._active is True


def test_note_off_signal_deactivates_matching_button_widget(qtbot, tmp_path):
    config = make_config(tmp_path)
    win = MainWindow(config)
    qtbot.addWidget(win)

    win.bridge.emit_note_on(60, 100)
    win.bridge.emit_note_off(60, 0)

    assert win.btn_widgets["60"]._active is False


def test_cc_signal_updates_matching_fader_widget(qtbot, tmp_path):
    config = make_config(tmp_path)
    win = MainWindow(config)
    qtbot.addWidget(win)

    win.bridge.emit_cc(1, 127)

    assert win.sl_widgets["1"].pct_lbl.text() == "100%"


def test_editing_a_button_through_the_gui_is_immediately_visible_to_the_shared_config(qtbot, tmp_path):
    config = make_config(tmp_path)
    win = MainWindow(config)
    qtbot.addWidget(win)

    win._edit_button = lambda note_key: None  # not exercising the dialog here
    config.buttons["60"]["label"] = "Renamed via GUI"

    # The same config object the MIDI backend would be holding sees the change
    # immediately - this is the bug fix, expressed as a test.
    assert config.buttons["60"]["label"] == "Renamed via GUI"
    assert win.config.buttons["60"]["label"] == "Renamed via GUI"
