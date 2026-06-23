from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from main import dispatch_midi_message, midi_loop


class _StopLoop(BaseException):
    """Escapes `except Exception` so tests can break an intentional `while True`."""


def test_dispatch_control_change_sets_volume_and_emits_cc():
    inputs, control, buttons, bridge = MagicMock(), MagicMock(), MagicMock(), MagicMock()
    msg = SimpleNamespace(type="control_change", control=1, value=64)

    dispatch_midi_message(msg, inputs, control, buttons, bridge)

    control.volum_control.assert_called_once_with(1, 64, inputs)
    bridge.emit_cc.assert_called_once_with(1, 64)
    buttons.handle_midi.assert_not_called()


def test_dispatch_note_on_triggers_buttons_and_emits_note_on():
    inputs, control, buttons, bridge = MagicMock(), MagicMock(), MagicMock(), MagicMock()
    msg = SimpleNamespace(type="note_on", note=60, velocity=100)

    dispatch_midi_message(msg, inputs, control, buttons, bridge)

    buttons.handle_midi.assert_called_once_with(msg)
    bridge.emit_note_on.assert_called_once_with(60, 100)
    control.volum_control.assert_not_called()


def test_dispatch_note_off_only_emits_note_off():
    inputs, control, buttons, bridge = MagicMock(), MagicMock(), MagicMock(), MagicMock()
    msg = SimpleNamespace(type="note_off", note=60, velocity=0)

    dispatch_midi_message(msg, inputs, control, buttons, bridge)

    bridge.emit_note_off.assert_called_once_with(60, 0)
    buttons.handle_midi.assert_not_called()
    control.volum_control.assert_not_called()


def test_dispatch_unknown_type_does_nothing():
    inputs, control, buttons, bridge = MagicMock(), MagicMock(), MagicMock(), MagicMock()
    msg = SimpleNamespace(type="sysex", data=())

    dispatch_midi_message(msg, inputs, control, buttons, bridge)

    control.volum_control.assert_not_called()
    buttons.handle_midi.assert_not_called()
    bridge.emit_note_on.assert_not_called()
    bridge.emit_note_off.assert_not_called()
    bridge.emit_cc.assert_not_called()


def test_midi_loop_survives_exception_and_continues(capsys):
    midi = MagicMock()
    midi.connected = True
    midi.read.side_effect = [RuntimeError("boom"), _StopLoop()]
    inputs, control, buttons, bridge = MagicMock(), MagicMock(), MagicMock(), MagicMock()

    with pytest.raises(_StopLoop):
        midi_loop(midi, inputs, control, buttons, bridge)

    assert midi.read.call_count == 2
    assert "boom" in capsys.readouterr().out
