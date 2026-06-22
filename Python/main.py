import sys
import threading
import time
from PyQt6.QtWidgets import QApplication
from gui import MainWindow
from config import Config
from Soundprojekt_pakke import Inputs, Control, Button_Control
from input import MidiInput

# Load JSON config
config = Config()

# Set up volume control and buttons
inputs  = Inputs(config)
control = Control()
buttons = Button_Control(config)

# Start MIDI reader (non-crashing if no device)
midi = MidiInput()

# Bind sliders to apps on startup
inputs.bind_all_sliders()

print("MIDI system active...")

# Start GUI
app = QApplication(sys.argv)
win = MainWindow()
win.show()


def midi_loop():
    last_bind = 0
    while True:
        # Try to reconnect if device was plugged in after startup
        if not midi.connected:
            midi.reconnect()
            if midi.connected:
                inputs.bind_all_sliders()

        msg = midi.read()
        now = time.time()

        # Rebind sliders every 5 seconds in case apps opened/closed
        if now - last_bind > 5:
            inputs.bind_all_sliders()
            last_bind = now

        if msg is None:
            time.sleep(0.001)  # Avoid busy-spinning when idle
            continue

        print(f"MIDI: {msg}")

        if msg.type == "control_change":
            control.volum_control(msg.control, msg.value, inputs)
            win.bridge.emit_cc(msg.control, msg.value)

        elif msg.type == "note_on":
            buttons.handle_midi(msg)
            win.bridge.emit_note_on(msg.note, msg.velocity)

        elif msg.type == "note_off":
            win.bridge.emit_note_off(msg.note, msg.velocity)


# Run MIDI loop in background
threading.Thread(target=midi_loop, daemon=True).start()

sys.exit(app.exec())
