import json


class Config:
    """Single Config class used by all modules."""

    def __init__(self, path="config.json"):
        self.path = path
        try:
            with open(path, "r") as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data = {
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

        self.buttons = self.data.setdefault("buttons", {})
        self.sliders = self.data.setdefault("sliders", {})
        self.apps    = self.data.setdefault("apps", {})

    def save(self):
        with open(self.path, "w") as f:
            json.dump(self.data, f, indent=4)
