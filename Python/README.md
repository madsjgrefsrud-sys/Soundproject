# Soundproject

ESP32-S3 MIDI controller + Windows control panel: MIDI buttons trigger virtual
gamepad presses, MIDI faders control per-app Windows volume.

## Run from source

```
pip install -r requirements.txt
python main.py
```

## Run the tests

```
pip install -r requirements-dev.txt
python -m pytest -v
```

## Build the standalone .exe

```
pip install -r requirements-dev.txt
python packaging/make_icon.py
pyinstaller packaging/soundproject.spec
```

The build lands in `dist/Soundproject/Soundproject.exe`.

## One-time external dependency

Gamepad button presses require the [ViGEmBus driver](https://github.com/nefarius/ViGEmBus)
to be installed once on the machine. It can't be bundled into the .exe (it's
a Windows kernel driver). If it's missing, the app still runs and the GUI
still works — gamepad button presses just silently do nothing until it's
installed.

## Config

Settings (button/fader mappings) live in `%AppData%\Soundproject\config.json`,
created automatically on first run.
