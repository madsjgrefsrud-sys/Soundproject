from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume

from .config import Config


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
                print(f"Bound s{cc} -> {app_name}")
            else:
                print(f"Not running: {app_name} ({app['exe']})")


class Control:
    def volum_control(self, cc_number, cc_value, inputs: Inputs):
        slider_name = f"s{cc_number}"
        if slider_name not in inputs.volumes:
            return
        vol_obj = inputs.volumes[slider_name]
        value   = cc_value / 127.0
        try:
            vol_obj.SetMasterVolume(value, None)
            print(f"{slider_name} -> {value:.2f}")
        except Exception as e:
            print(f"Volume error (session may have closed): {e}")
            # Remove stale reference so rebind picks it up next cycle
            del inputs.volumes[slider_name]
