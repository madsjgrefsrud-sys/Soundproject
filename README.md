# Soundproject

ESP32-S3 MIDI controller + Windows control panel: MIDI buttons trigger virtual
gamepad presses, MIDI faders control per-app Windows volume.

## Download

**[Download the latest installer](https://github.com/madsjgrefsrud-sys/Soundproject/releases/latest)** —
run `Soundproject-Setup-*.exe`, click through it, plug in the hardware. ViGEmBus
(needed for the gamepad buttons) installs automatically in the same step — nothing
else to install.

Unsigned installer: Windows SmartScreen will likely warn on first run ("Windows
protected your PC"). Click **More info → Run anyway** — expected for a free hobby
project without a paid code-signing certificate, not a sign anything's wrong.

## What's in this repo

- [`Python/`](Python/) — the control panel app (PyQt6). See
  [Python/README.md](Python/README.md) for running from source, tests, and
  building the installer yourself.
- [`Firmware/`](Firmware/) — ESP32-S3 firmware (Arduino). Flash
  [`Firmware/ESP32_Soundproject.ino`](Firmware/ESP32_Soundproject.ino) onto an
  "ESP32S3 Dev Module" board with **Tools → USB Mode → "USB-OTG (TinyUSB)"** set —
  verify the pin map at the top of the file against your actual wiring first.
- [`Docs/`](Docs/) — project documentation.

## License

GPLv3 — see [LICENSE](LICENSE).
