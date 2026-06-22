# Soundproject Redesign — Design

Date: 2026-06-22
Status: Approved by user, pending spec review

## 1. Summary

Soundproject is an ESP32-S3 MIDI controller (20-button matrix keyboard + 2 potentiometers) paired with a Windows Python app that maps MIDI input to per-app volume control (pycaw) and virtual gamepad button presses (vgamepad), with a PyQt6 control-panel GUI.

This round of work:
- Writes the firmware from scratch (it doesn't currently exist in this project — only editor config files are present in `Firmware/`).
- Restructures the Python backend into a small package, fixing a couple of robustness bugs found while reading the code.
- Redesigns the GUI with a new visual theme ("Carbon Red") on the existing, already-working layout.
- Packages the app as a standalone Windows `.exe` via PyInstaller.

## 2. Architecture (unchanged shape)

```
[ ESP32-S3 firmware ]
   5x4 button matrix (diode-protected, 20 keys) -> MIDI note_on/note_off (notes 60-79)
   2 potentiometers                              -> MIDI control_change (CC 1, CC 2)
   I2C bus initialized, extension hook present, not yet implemented
         |  USB MIDI (native USBMIDI device class)
         v
[ Python app - app/ package ]
   midi_input.py     -> polls MIDI via mido, non-crashing if no device
   audio_control.py  -> CC values set per-app Windows volume via pycaw
   gamepad_control.py -> note_on triggers a virtual Xbox 360 button via vgamepad
   bridge.py         -> thread-safe Qt signals from the MIDI thread to the GUI
         |
         v
[ GUI - app/gui/ package, PyQt6, "Carbon Red" theme ]
   Status header (MIDI device chips)
   Button grid (lights up red on note_on)
   2 faders (animate red on CC change)
   Click-to-edit dialogs for remapping buttons/sliders
```

This is one cohesive product (firmware and app only talk to each other via plain MIDI messages, an already-stable contract), so it gets one spec and one implementation plan rather than being split up.

## 3. Firmware

New file: `Firmware/ESP32_Soundproject.ino`. No source currently exists for this board — it's a fresh implementation against the spec below, since there's no real hardware available to me to test against. Pin assignments must be verified by the user against the actual wiring before flashing.

### 3.1 Button matrix

- It's a genuine **matrix-keyboard layout**: one diode per switch (anti-ghosting), so multiple simultaneous key presses are safe to scan normally — no extra ghost-masking logic needed.
- 5 rows x 4 columns = 20 keys, scanned with rows as outputs (idle HIGH, driven LOW one at a time) and columns as inputs (`INPUT_PULLUP`), 20 ms debounce per key.
- Key index = `row * 4 + col` (0-19) -> **MIDI note = 60 + index** (60-79), matching the Python app's existing default config (which already assumes 20 buttons numbered 60-79).
- note_on sent on press, note_off on release.
- If presses come out inverted or don't register, the most likely cause is the diodes being oriented the other way round — fixed by swapping which pin set is `OUTPUT` vs `INPUT_PULLUP` in the code, not a wiring change.

### 3.2 Potentiometers

- 2 pots on native ADC1 pins -> CC1 and CC2, matching the existing `config.json` default (`sliders: {"1": ..., "2": ...}`).
- 12-bit ADC (0-4095) oversampled (average of 8 reads) to cut down ESP32 ADC jitter, then scaled to 7-bit (0-127) by right-shifting 5 bits.
- A CC message is only sent when the value changes by >= 2 from the last sent value, and snapped to the exact 0/127 endpoints, so slow sweeps don't spam the bus but full-range sweeps still reliably hit both ends.

### 3.3 I2C — extension point only

- `Wire.begin(SDA, SCL)` is called at startup and a `readI2CInputs()` function is wired into `loop()`, but left as an empty stub with a `// TODO` comment.
- Actual protocol/device handling is deferred until the hardware/peripheral is finalized — out of scope for this round.

### 3.4 USB MIDI transport

- Uses the native `USB.h` / `USBMIDI.h` classes already included in the installed ESP32 Arduino board package (3.3.8) — `USBMIDI MIDI; MIDI.begin(); MIDI.noteOn(...); MIDI.controlChange(...);`. No extra libraries to install.
- The vendored `libraries/MIDI` (FortySevenEffects) checkout goes unused by this approach; left in place untouched.
- Requires Arduino IDE **Tools -> USB Mode -> "USB-OTG (TinyUSB)"** (already noted in the existing docs) — this is a per-board IDE setting, not something this file controls.
- `Firmware/.clangd` currently defines `ARDUINO_USB_MODE=1`, which corresponds to the *other* USB mode (Hardware CDC/JTAG) and would make clangd think the MIDI code is inside a disabled `#if` branch. Fixing this define to `0` so editor IntelliSense matches the real build.

### 3.5 Pin map (verify against actual wiring before flashing)

| Function | Pins | Notes |
|---|---|---|
| Matrix rows (OUTPUT, idle HIGH) | GPIO4, 5, 6, 7, 10 | 5 rows |
| Matrix columns (INPUT_PULLUP) | GPIO11, 12, 13, 14 | 4 columns |
| Potentiometer 1 -> CC1 | GPIO1 (ADC1_CH0) | |
| Potentiometer 2 -> CC2 | GPIO2 (ADC1_CH1) | |
| I2C SDA / SCL | GPIO8 / GPIO9 | bus initialized, unused for now |

Avoided: GPIO0/3/45/46 (strapping pins), GPIO19/20 (native USB D-/D+), GPIO35-37 (often wired to octal PSRAM on WROOM modules).

## 4. Python backend restructure

Flat scripts (`gui.py`, `config.py`, `input.py`, `Soundprojekt_pakke.py`, `main.py`) become a small package:

```
Python/
  app/
    config.py            Config class; default path moves to %AppData%\Soundproject\config.json
    midi_input.py         MidiInput (moved from input.py, behavior unchanged)
    audio_control.py      Inputs, Control (from Soundprojekt_pakke.py)
    gamepad_control.py    Button_Control + gamepad sending (from Soundprojekt_pakke.py)
    bridge.py             MidiBridge (moved out of gui.py)
    gui/
      theme.py             Carbon Red palette + QSS
      widgets.py           ButtonWidget, FaderWidget
      dialogs.py           ButtonEditDialog, SliderEditDialog
      main_window.py       MainWindow
  main.py                 thin entry point
  requirements.txt
  packaging/
    soundproject.spec      PyInstaller spec
    icon.ico
```

Behavior is preserved as-is except for two concrete fixes found while reading the code:
- **vgamepad/ViGEmBus crash on launch:** `Soundprojekt_pakke.py` currently constructs `vg.VX360Gamepad()` at import time, unguarded — if the ViGEmBus driver isn't installed, the entire app fails to start before the GUI ever appears. `gamepad_control.py` will lazily create the gamepad on first use, inside a try/except, and no-op with a one-time logged warning if it's unavailable, instead of crashing.
- **Config path:** moves from a relative `config.json` (depends on the working directory the process happened to start in) to `%AppData%\Soundproject\config.json`, so the packaged `.exe` behaves the same regardless of how it's launched.

Everything else that already works (MIDI reconnect logic, CC smoothing/snapping, stale-volume-reference cleanup) is left alone.

## 5. GUI redesign — "Carbon Red"

Same structure as today (status header with MIDI device chips, button grid, fader panel, click-to-edit dialogs) — re-themed, not re-architected:

| Token | Value | Used for |
|---|---|---|
| Background | `#0a0a0b` | window background |
| Panel | `#111113` | header bar |
| Card (idle) | `#171718` / border `#2a2a2c` | button cells, fader track |
| Text dim (idle) | `#76767a` | inactive labels/numbers |
| Text | `#e8e8ea` | primary text |
| Accent (live) | `#e0303f` + glow `rgba(224,48,63,.55)` | pressed button, active fader fill, connected MIDI device |
| Fader fill | gradient `#ff5a64` -> `#c81e2e` | fader level |
| Fader cap | `#f2f2f3` | fader handle |

One consistent red accent for everything "live" (buttons and faders share it — that was the point of this direction vs. the more multicolor options). Font switches from the current monospace "Consolas" to system sans-serif (Segoe UI) for general text; monospace is kept only for the MIDI device-name chips, which are genuinely technical/log-like. A small app icon (red mark on black) is added for the window and the packaged `.exe`.

No functional changes to the edit dialogs (still: label + gamepad button number for buttons; app dropdown for sliders).

## 6. Packaging

- PyInstaller, `--onedir` (not `--onefile` — easier to debug native-extension issues from pycaw/comtypes, vgamepad, python-rtmidi).
- `Python/packaging/soundproject.spec` builds `dist/Soundproject/Soundproject.exe` with the new icon.
- One-time external dependency, documented in the README, not bundleable: the ViGEmBus driver (kernel driver vgamepad needs).
- `requirements.txt` added: PyQt6, mido, python-rtmidi, pycaw, pywin32, vgamepad.
- A short `README.md` at the project root covers setup/build/run — the existing `Docs/Soundproject_Documentation.docx` is left untouched.

## 7. Verification plan

- **Python/GUI:** run the app locally with no hardware attached (it already supports a standalone no-MIDI mode), confirm it launches without errors, visually confirm the Carbon Red theme, exercise the button/slider edit dialogs, confirm config persists to the new `%AppData%` path. Screenshot before calling it done.
- **Packaged exe:** build via the PyInstaller spec and launch the resulting `.exe` once to confirm it starts standalone.
- **Firmware:** cannot be flashed/tested on real hardware in this environment. Verified for correct use of the native `USBMIDI` API (checked against the actual ESP32 Arduino core source) and internally consistent pin usage; the user must verify the pin map against their physical wiring before flashing.

## 8. Explicitly out of scope for this round

- Updating `Docs/Soundproject_Documentation.docx` (it's already stale on button count; left alone per user request — documentation comes later).
- Implementing the actual I2C peripheral protocol (hook only, per user request — hardware not finalized yet).
- Any change to MIDI smoothing/reconnect logic that already works.
- Any change to what the edit dialogs configure (only their visual style changes).
