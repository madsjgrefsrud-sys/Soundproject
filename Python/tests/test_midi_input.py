from unittest.mock import MagicMock

from app import midi_input as midi_input_module
from app.midi_input import MidiInput


def test_connects_to_first_matching_port(monkeypatch):
    fake_port = MagicMock()
    monkeypatch.setattr(midi_input_module.mido, "get_input_names",
                         lambda: ["Microsoft GS Wavetable Synth", "ESP32 MIDI 1"])
    monkeypatch.setattr(midi_input_module.mido, "open_input", lambda name: fake_port)

    m = MidiInput()

    assert m.connected is True
    assert m.port is fake_port


def test_stays_disconnected_when_no_matching_port(monkeypatch):
    monkeypatch.setattr(midi_input_module.mido, "get_input_names",
                         lambda: ["Microsoft GS Wavetable Synth"])

    m = MidiInput()

    assert m.connected is False
    assert m.read() is None


def test_reconnect_only_retries_when_disconnected(monkeypatch):
    calls = {"count": 0}

    def fake_get_input_names():
        calls["count"] += 1
        return []

    monkeypatch.setattr(midi_input_module.mido, "get_input_names", fake_get_input_names)

    m = MidiInput()
    assert calls["count"] == 1

    m.reconnect()
    assert calls["count"] == 2  # still disconnected, so it retries

    m.port = MagicMock()
    m.reconnect()
    assert calls["count"] == 2  # already connected, no retry


def test_read_delegates_to_port_poll(monkeypatch):
    fake_port = MagicMock()
    fake_port.poll.return_value = "a-message"
    monkeypatch.setattr(midi_input_module.mido, "get_input_names", lambda: ["ESP32 MIDI 1"])
    monkeypatch.setattr(midi_input_module.mido, "open_input", lambda name: fake_port)

    m = MidiInput()

    assert m.read() == "a-message"
