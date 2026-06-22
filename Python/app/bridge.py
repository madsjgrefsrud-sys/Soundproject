from PyQt6.QtCore import QObject, pyqtSignal


def smooth_cc(prev: int, val: int) -> int:
    """Exponential moving average with snap-to-endpoints, so slow CC sweeps
    don't jitter but full-range sweeps still reliably hit 0 and 127."""
    smoothed = int(prev * 0.6 + val * 0.4)
    if val >= 124:
        smoothed = 127
    if val <= 3:
        smoothed = 0
    return smoothed


class MidiBridge(QObject):
    """Thread-safe bridge from the MIDI-polling thread into Qt signals."""

    note_on  = pyqtSignal(int, int)
    note_off = pyqtSignal(int, int)
    cc       = pyqtSignal(int, int)

    def __init__(self):
        super().__init__()
        self._cc_last = {}

    def emit_note_on(self, note, vel):
        self.note_on.emit(note, vel)

    def emit_note_off(self, note, vel):
        self.note_off.emit(note, vel)

    def emit_cc(self, num, val):
        prev = self._cc_last.get(num, val)
        smoothed = smooth_cc(prev, val)
        self._cc_last[num] = smoothed
        self.cc.emit(num, smoothed)
