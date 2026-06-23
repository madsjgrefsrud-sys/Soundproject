import logging
from unittest.mock import MagicMock

from app import audio_control as audio_control_module
from app.audio_control import Inputs, Control
from app.config import Config


def make_session(process_name):
    session = MagicMock()
    session.Process.name.return_value = process_name
    return session


def test_get_app_volume_matches_case_insensitively(monkeypatch, tmp_path):
    session = make_session("Chrome.exe")
    sentinel_vol = MagicMock()
    session._ctl.QueryInterface.return_value = sentinel_vol
    monkeypatch.setattr(audio_control_module.AudioUtilities, "GetAllSessions",
                         lambda: [session])

    inputs = Inputs(Config(path=tmp_path / "config.json"))

    assert inputs.get_app_volume("chrome.exe") is sentinel_vol


def test_get_app_volume_returns_none_when_not_running(monkeypatch, tmp_path):
    monkeypatch.setattr(audio_control_module.AudioUtilities, "GetAllSessions", lambda: [])

    inputs = Inputs(Config(path=tmp_path / "config.json"))

    assert inputs.get_app_volume("chrome.exe") is None


def test_bind_all_sliders_binds_running_apps(monkeypatch, tmp_path):
    monkeypatch.setattr(audio_control_module.AudioUtilities, "GetAllSessions", lambda: [])

    config = Config(path=tmp_path / "config.json")
    config.sliders = {"1": {"app": "Chrome"}}
    config.apps = {"Chrome": {"exe": "chrome.exe"}}
    inputs = Inputs(config)

    sentinel_vol = MagicMock()
    monkeypatch.setattr(inputs, "get_app_volume", lambda exe: sentinel_vol)

    inputs.bind_all_sliders()

    assert inputs.volumes["s1"] is sentinel_vol


def test_bind_all_sliders_skips_unknown_app(monkeypatch, tmp_path):
    monkeypatch.setattr(audio_control_module.AudioUtilities, "GetAllSessions", lambda: [])

    config = Config(path=tmp_path / "config.json")
    config.sliders = {"1": {"app": "Nonexistent"}}
    config.apps = {}
    inputs = Inputs(config)

    inputs.bind_all_sliders()

    assert inputs.volumes == {}


def test_volum_control_sets_master_volume(tmp_path):
    config = Config(path=tmp_path / "config.json")
    inputs = Inputs(config)
    vol_obj = MagicMock()
    inputs.volumes["s1"] = vol_obj

    Control().volum_control(cc_number="1", cc_value=127, inputs=inputs)

    vol_obj.SetMasterVolume.assert_called_once_with(1.0, None)


def test_volum_control_noops_when_slider_not_bound(tmp_path):
    config = Config(path=tmp_path / "config.json")
    inputs = Inputs(config)

    Control().volum_control(cc_number="1", cc_value=64, inputs=inputs)  # no exception


def test_volum_control_drops_stale_reference_on_exception(tmp_path):
    config = Config(path=tmp_path / "config.json")
    inputs = Inputs(config)
    vol_obj = MagicMock()
    vol_obj.SetMasterVolume.side_effect = Exception("session closed")
    inputs.volumes["s1"] = vol_obj

    Control().volum_control(cc_number="1", cc_value=64, inputs=inputs)

    assert "s1" not in inputs.volumes


def test_bind_all_sliders_does_not_print_anything(monkeypatch, tmp_path, capsys):
    session = make_session("Chrome.exe")
    monkeypatch.setattr(audio_control_module.AudioUtilities, "GetAllSessions", lambda: [session])

    config = Config(path=tmp_path / "config.json")
    config.sliders = {
        "1": {"app": "Chrome"},
        "2": {"app": "Discord"},
        "3": {"app": "Nonexistent"},
    }
    config.apps = {
        "Chrome":  {"exe": "chrome.exe"},
        "Discord": {"exe": "discord.exe"},
    }
    inputs = Inputs(config)

    inputs.bind_all_sliders()

    assert capsys.readouterr().out == ""


def test_bind_all_sliders_logs_session_and_binding_details_at_debug_level(monkeypatch, tmp_path, caplog):
    session = make_session("Chrome.exe")
    monkeypatch.setattr(audio_control_module.AudioUtilities, "GetAllSessions", lambda: [session])

    config = Config(path=tmp_path / "config.json")
    config.sliders = {
        "1": {"app": "Chrome"},
        "2": {"app": "Discord"},
        "3": {"app": "Nonexistent"},
    }
    config.apps = {
        "Chrome":  {"exe": "chrome.exe"},
        "Discord": {"exe": "discord.exe"},
    }
    inputs = Inputs(config)

    with caplog.at_level(logging.DEBUG, logger="app.audio_control"):
        inputs.bind_all_sliders()

    assert "Chrome.exe" in caplog.text
    assert "Bound s1" in caplog.text
    assert "Not running: Discord" in caplog.text
    assert "Nonexistent" in caplog.text
