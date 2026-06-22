import json
import os
from pathlib import Path


def default_config_path() -> Path:
    base = os.environ.get("APPDATA") or str(Path.home())
    return Path(base) / "Soundproject" / "config.json"


def _default_data() -> dict:
    return {
        "buttons": {
            str(60 + i): {"type": "gamepad", "value": i + 1, "label": f"key{i+1}"}
            for i in range(20)
        },
        "sliders": {"1": {"app": "Chrome"}, "2": {"app": "Discord"}},
        "apps": {
            "Chrome":  {"exe": "chrome.exe"},
            "Discord": {"exe": "discord.exe"},
            "Spotify": {"exe": "Spotify.exe"},
            "System":  {"exe": ""}
        }
    }


class Config:
    """Single Config class used by all modules."""

    def __init__(self, path=None):
        self.path = Path(path) if path is not None else default_config_path()
        try:
            with open(self.path, "r") as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data = _default_data()

        self.buttons = self.data.setdefault("buttons", {})
        self.sliders = self.data.setdefault("sliders", {})
        self.apps    = self.data.setdefault("apps", {})

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w") as f:
            json.dump(self.data, f, indent=4)
