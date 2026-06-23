from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app import gamepad_control as gc
from app.config import Config


@pytest.fixture(autouse=True)
def reset_gamepad_singleton(monkeypatch):
    monkeypatch.setattr(gc, "_gamepad", None)
    monkeypatch.setattr(gc, "_gamepad_unavailable", False)


def test_get_gamepad_returns_none_when_vgamepad_unavailable(monkeypatch):
    def raise_error():
        raise RuntimeError("ViGEmBus not installed")
    monkeypatch.setattr(gc.vg, "VX360Gamepad", raise_error)

    assert gc._get_gamepad() is None
    assert gc._get_gamepad() is None  # second call doesn't re-raise


def test_get_gamepad_caches_instance_when_available(monkeypatch):
    fake_gamepad = MagicMock()
    constructor = MagicMock(return_value=fake_gamepad)
    monkeypatch.setattr(gc.vg, "VX360Gamepad", constructor)

    first = gc._get_gamepad()
    second = gc._get_gamepad()

    assert first is fake_gamepad
    assert second is fake_gamepad
    constructor.assert_called_once()


def test_send_gamepad_button_noops_when_gamepad_unavailable(monkeypatch):
    monkeypatch.setattr(gc, "_get_gamepad", lambda: None)

    gc.send_gamepad_button(1)  # must not raise


def test_send_gamepad_button_presses_and_releases_mapped_button(monkeypatch):
    fake_gamepad = MagicMock()
    monkeypatch.setattr(gc, "_get_gamepad", lambda: fake_gamepad)
    monkeypatch.setattr(gc.time, "sleep", lambda s: None)

    gc.send_gamepad_button(1)

    fake_gamepad.press_button.assert_called_once_with(button=gc.BUTTON_MAP[1])
    fake_gamepad.release_button.assert_called_once_with(button=gc.BUTTON_MAP[1])
    assert fake_gamepad.update.call_count == 2


def test_send_gamepad_button_unknown_number_noops(monkeypatch):
    fake_gamepad = MagicMock()
    monkeypatch.setattr(gc, "_get_gamepad", lambda: fake_gamepad)

    gc.send_gamepad_button(99)

    fake_gamepad.press_button.assert_not_called()


def test_button_control_dispatches_configured_gamepad_note(monkeypatch, tmp_path):
    config = Config(path=tmp_path / "config.json")
    config.buttons = {"60": {"type": "gamepad", "value": 3, "label": "Mute"}}
    sent = []
    monkeypatch.setattr(gc, "send_gamepad_button", lambda n: sent.append(n))

    controller = gc.Button_Control(config)
    controller.handle_midi(SimpleNamespace(type="note_on", note=60, velocity=127))

    assert sent == [3]


def test_button_control_ignores_unconfigured_note(monkeypatch, tmp_path):
    config = Config(path=tmp_path / "config.json")
    config.buttons = {}
    sent = []
    monkeypatch.setattr(gc, "send_gamepad_button", lambda n: sent.append(n))

    controller = gc.Button_Control(config)
    controller.handle_midi(SimpleNamespace(type="note_on", note=61, velocity=127))

    assert sent == []


def test_button_control_ignores_non_note_on(monkeypatch, tmp_path):
    config = Config(path=tmp_path / "config.json")
    config.buttons = {"60": {"type": "gamepad", "value": 3}}
    sent = []
    monkeypatch.setattr(gc, "send_gamepad_button", lambda n: sent.append(n))

    controller = gc.Button_Control(config)
    controller.handle_midi(SimpleNamespace(type="note_off", note=60, velocity=0))

    assert sent == []
