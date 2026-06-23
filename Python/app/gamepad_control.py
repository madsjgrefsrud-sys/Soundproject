import time

import vgamepad as vg

from .config import Config

BUTTON_MAP = {
    1:  vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
    2:  vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
    3:  vg.XUSB_BUTTON.XUSB_GAMEPAD_X,
    4:  vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
    5:  vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER,
    6:  vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
    7:  vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
    8:  vg.XUSB_BUTTON.XUSB_GAMEPAD_START,
    9:  vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB,
    10: vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB,
    11: vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,
    12: vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
    13: vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT,
    14: vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT,
    15: vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER,
    16: vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
}

_gamepad = None
_gamepad_unavailable = False


def _get_gamepad():
    """Lazily create the virtual gamepad. Returns None (and warns once) if
    the ViGEmBus driver isn't installed, instead of crashing the app."""
    global _gamepad, _gamepad_unavailable
    if _gamepad is not None:
        return _gamepad
    if _gamepad_unavailable:
        return None
    try:
        _gamepad = vg.VX360Gamepad()
    except Exception as e:
        _gamepad_unavailable = True
        print(f"Gamepad unavailable (is ViGEmBus installed?): {e}")
        return None
    return _gamepad


def send_gamepad_button(button_number):
    """Press and release a virtual gamepad button."""
    gamepad = _get_gamepad()
    if gamepad is None:
        return
    btn = BUTTON_MAP.get(button_number)
    if btn is None:
        print(f"Unknown button number: {button_number}")
        return
    gamepad.press_button(button=btn)
    gamepad.update()
    time.sleep(0.05)
    gamepad.release_button(button=btn)
    gamepad.update()
    print(f"Gamepad button {button_number} -> {btn}")


class Button_Control:
    def __init__(self, config: Config):
        self.config = config

    def handle_midi(self, msg):
        if msg.type != "note_on":
            return

        note = str(msg.note)
        if note not in self.config.buttons:
            return

        action = self.config.buttons[note]
        if action["type"] == "gamepad":
            send_gamepad_button(action["value"])
