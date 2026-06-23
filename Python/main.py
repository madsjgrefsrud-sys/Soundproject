import sys
import threading
import time

from PyQt6.QtWidgets import QApplication

from app.config import Config
from app.midi_input import MidiInput
from app.audio_control import Inputs, Control
from app.gamepad_control import Button_Control
from app.gui.main_window import MainWindow, apply_palette


def dispatch_midi_message(msg, inputs, control, buttons, bridge):
    """Route one MIDI message to the audio/gamepad backends and the GUI bridge."""
    if msg.type == "control_change":
        control.volum_control(msg.control, msg.value, inputs)
        bridge.emit_cc(msg.control, msg.value)
    elif msg.type == "note_on":
        buttons.handle_midi(msg)
        bridge.emit_note_on(msg.note, msg.velocity)
    elif msg.type == "note_off":
        bridge.emit_note_off(msg.note, msg.velocity)


def midi_loop(midi, inputs, control, buttons, bridge):
    last_bind = 0
    while True:
        try:
            if not midi.connected:
                midi.reconnect()
                if midi.connected:
                    inputs.bind_all_sliders()

            msg = midi.read()
            now = time.time()

            if now - last_bind > 5:
                inputs.bind_all_sliders()
                last_bind = now

            if msg is None:
                time.sleep(0.001)
                continue

            print(f"MIDI: {msg}")
            dispatch_midi_message(msg, inputs, control, buttons, bridge)
        except Exception as e:
            print(f"MIDI loop error: {e}")


def main():
    config  = Config()
    inputs  = Inputs(config)
    control = Control()
    buttons = Button_Control(config)
    midi    = MidiInput()

    inputs.bind_all_sliders()
    print("MIDI system active...")

    app = QApplication(sys.argv)
    apply_palette(app)
    win = MainWindow(config)
    win.show()

    threading.Thread(
        target=midi_loop,
        args=(midi, inputs, control, buttons, win.bridge),
        daemon=True,
    ).start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
