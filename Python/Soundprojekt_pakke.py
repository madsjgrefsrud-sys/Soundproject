import time
import vgamepad as vg
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
from config import Config


# ---------------------------------------------------------
# GAMEPAD SENDER
# Registers a virtual Xbox 360 controller on Windows.
# Games see this as a real gamepad and let you bind
# buttons in their settings.
# ---------------------------------------------------------

_gamepad = vg.VX360Gamepad()

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


def send_gamepad_button(button_number):
    """Press and release a virtual gamepad button."""
    btn = BUTTON_MAP.get(button_number)
    if btn is None:
        print(f"Unknown button number: {button_number}")
        return
    _gamepad.press_button(button=btn)
    _gamepad.update()
    time.sleep(0.05)
    _gamepad.release_button(button=btn)
    _gamepad.update()
    print(f"Gamepad button {button_number} → {btn}")


# ---------------------------------------------------------
# INPUTS (APP VOLUME)
# ---------------------------------------------------------

class Inputs:
    def __init__(self, config: Config):
        self.config  = config
        self.volumes = {}

    def get_app_volume(self, process_name):
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            if session.Process and session.Process.name().lower() == process_name.lower():
                return session._ctl.QueryInterface(ISimpleAudioVolume)
        return None

    def bind_all_sliders(self):
        # Debug: list all running audio sessions
        sessions = AudioUtilities.GetAllSessions()
        for s in sessions:
            if s.Process:
                print(f"  Running: {s.Process.name()}")

        for cc, app_info in self.config.sliders.items():
            app_name = app_info["app"]
            app      = self.config.apps.get(app_name)
            if app is None:
                print(f"App '{app_name}' not found in config")
                continue
            vol = self.get_app_volume(app["exe"])
            if vol:
                self.volumes[f"s{cc}"] = vol
                print(f"Bound s{cc} → {app_name}")
            else:
                print(f"Not running: {app_name} ({app['exe']})")


# ---------------------------------------------------------
# CONTROL (SLIDER → VOLUME)
# ---------------------------------------------------------

class Control:
    def volum_control(self, cc_number, cc_value, inputs: Inputs):
        slider_name = f"s{cc_number}"
        if slider_name not in inputs.volumes:
            return
        vol_obj = inputs.volumes[slider_name]
        value   = cc_value / 127.0
        try:
            vol_obj.SetMasterVolume(value, None)
            print(f"{slider_name} → {value:.2f}")
        except Exception as e:
            print(f"Volume error (session may have closed): {e}")
            # Remove stale reference so rebind picks it up next cycle
            del inputs.volumes[slider_name]


# ---------------------------------------------------------
# BUTTON CONTROL (NOTE → GAMEPAD)
# ---------------------------------------------------------

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
