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

## Build the installer

Requires the free [Inno Setup](https://jrsoftware.org/isinfo.php) compiler (one-time
dev-machine install: `winget install --id JRSoftware.InnoSetup`). Run after the steps
above, from `Python/`:

```
"%LocalAppData%\Programs\Inno Setup 6\ISCC.exe" packaging\installer.iss
```

Produces `dist\Soundproject-Setup-<version>.exe` (version comes from `MyAppVersion` in
`installer.iss`) — a single file that installs the app, shortcuts, and the ViGEmBus
driver in one click. This is what to hand to anyone who isn't building from source.

## One-time external dependency

If you used `Soundproject-Setup-*.exe`, this is already handled — skip this section.

Gamepad button presses require the [ViGEmBus driver](https://github.com/nefarius/ViGEmBus)
to be installed once on the machine. It can't be bundled into the .exe (it's
a Windows kernel driver). If it's missing, the app still runs and the GUI
still works — gamepad button presses just silently do nothing until it's
installed.

## Config

Settings (button/fader mappings) live in `%AppData%\Soundproject\config.json`,
created automatically on first run.

## License

GPLv3 — see [LICENSE](../LICENSE).
