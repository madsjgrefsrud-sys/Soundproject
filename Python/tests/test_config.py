import json

from app.config import Config, default_config_path


def test_default_path_uses_appdata(monkeypatch, tmp_path):
    monkeypatch.setenv("APPDATA", str(tmp_path))
    assert default_config_path() == tmp_path / "Soundproject" / "config.json"


def test_creates_default_data_when_file_missing(tmp_path):
    cfg = Config(path=tmp_path / "nofile.json")
    assert len(cfg.buttons) == 20
    assert set(cfg.buttons.keys()) == {str(60 + i) for i in range(20)}
    assert cfg.sliders == {"1": {"app": "Chrome"}, "2": {"app": "Discord"}}
    assert "Chrome" in cfg.apps


def test_save_creates_parent_directory_and_persists(tmp_path):
    path = tmp_path / "nested" / "dir" / "config.json"
    cfg = Config(path=path)
    cfg.buttons["60"]["label"] = "Mute"
    cfg.save()

    assert path.exists()
    with open(path) as f:
        data = json.load(f)
    assert data["buttons"]["60"]["label"] == "Mute"


def test_loads_existing_file_verbatim(tmp_path):
    path = tmp_path / "config.json"
    custom = {"buttons": {"61": {"type": "gamepad", "value": 2, "label": "X"}},
              "sliders": {"1": {"app": "Spotify"}}, "apps": {}}
    with open(path, "w") as f:
        json.dump(custom, f)

    cfg = Config(path=path)
    assert cfg.buttons == {"61": {"type": "gamepad", "value": 2, "label": "X"}}
    assert cfg.sliders == {"1": {"app": "Spotify"}}
