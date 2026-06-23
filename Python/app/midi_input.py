import mido


class MidiInput:
    """Non-crashing MIDI input. Returns None from read() if no port is connected."""

    def __init__(self):
        self.port = None
        self._try_connect()

    def _try_connect(self):
        """Attempt to open the first ESP32/MIDI port found. Silent if none."""
        try:
            ports = mido.get_input_names()
            print("MIDI ports found:", ports)
            for p in ports:
                if "ESP32" in p or "MIDI" in p:
                    self.port = mido.open_input(p)
                    print("Connected to:", p)
                    return
            print("No ESP32/MIDI port found - running without MIDI input.")
        except Exception as e:
            print(f"MIDI init error: {e}")

    def reconnect(self):
        """Try to reconnect - call this if the device is plugged in later."""
        if self.port is None:
            self._try_connect()

    def read(self):
        """Poll for a single MIDI message. Returns None if no port or no message."""
        if self.port is None:
            return None
        return self.port.poll()

    @property
    def connected(self):
        return self.port is not None
