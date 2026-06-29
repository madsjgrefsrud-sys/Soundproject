// Soundproject - ESP32-S3 MIDI controller firmware
//
// 5x4 diode-protected button matrix (20 keys) -> MIDI notes 60-79
// 2 potentiometers                            -> MIDI CC 1, CC 2
// I2C macropad (20 keys, slave @ I2C_MACROPAD_ADDR) -> MIDI notes 80-99
//
// Board:    ESP32S3 Dev Module
// Required: Tools > USB Mode > "USB-OTG (TinyUSB)"
//
// Verify every pin below against your actual wiring before flashing.

#include <Arduino.h>
#include <Wire.h>

#if ARDUINO_USB_MODE
#warning "This sketch requires Tools > USB Mode > USB-OTG (TinyUSB)"
void setup() {}
void loop() {}
#else

SET_USB_MIDI_DEVICE_NAME("Soundproject MIDI")

#include "USB.h"
#include "USBMIDI.h"

USBMIDI MIDI;

// ---- Button matrix (diode-protected: safe to read multiple keys at once) --
const uint8_t ROW_PINS[] = {4, 5, 6, 7, 10};   // OUTPUT, idle HIGH
const uint8_t COL_PINS[] = {11, 12, 13, 14};   // INPUT_PULLUP
const uint8_t NUM_ROWS = sizeof(ROW_PINS) / sizeof(ROW_PINS[0]);
const uint8_t NUM_COLS = sizeof(COL_PINS) / sizeof(COL_PINS[0]);
const uint8_t FIRST_NOTE = 60;
const uint16_t DEBOUNCE_MS = 20;

bool keyState[NUM_ROWS][NUM_COLS] = {{false}};
unsigned long lastChangeMs[NUM_ROWS][NUM_COLS] = {{0}};

// If presses come out inverted or don't register at all, your diodes are
// likely oriented the other way - swap OUTPUT/INPUT_PULLUP between
// ROW_PINS and COL_PINS above rather than rewiring.

// ---- Potentiometers ----------------------------------------------------
const uint8_t POT_PINS[]   = {1, 2};   // ADC1 -> CC1, CC2
const uint8_t CC_NUMBERS[] = {1, 2};
const uint8_t NUM_POTS = sizeof(POT_PINS) / sizeof(POT_PINS[0]);
const uint8_t CC_THRESHOLD = 2;
const uint8_t ADC_SAMPLES = 8;
uint8_t lastCCValue[NUM_POTS] = {0, 0};

// ---- I2C macropad (slave board, 20 keys) -------------------------------
const uint8_t I2C_SDA_PIN = 8;
const uint8_t I2C_SCL_PIN = 9;
const uint8_t I2C_MACROPAD_ADDR = 0x42;
const uint8_t MACROPAD_FIRST_NOTE = 80;
const uint8_t MACROPAD_NUM_KEYS = 20;

bool macropadKeyState[MACROPAD_NUM_KEYS] = {false};
bool macropadConnected = false;

void scanMatrix() {
  for (uint8_t r = 0; r < NUM_ROWS; r++) {
    digitalWrite(ROW_PINS[r], LOW);
    delayMicroseconds(30);  // let the pulled-up column settle through the diode

    for (uint8_t c = 0; c < NUM_COLS; c++) {
      bool pressed = (digitalRead(COL_PINS[c]) == LOW);
      unsigned long now = millis();

      if (pressed != keyState[r][c] && (now - lastChangeMs[r][c]) >= DEBOUNCE_MS) {
        keyState[r][c] = pressed;
        lastChangeMs[r][c] = now;

        uint8_t note = FIRST_NOTE + (r * NUM_COLS + c);
        if (pressed) {
          MIDI.noteOn(note, 127);
        } else {
          MIDI.noteOff(note, 0);
        }
      }
    }

    digitalWrite(ROW_PINS[r], HIGH);
  }
}

void readPots() {
  for (uint8_t i = 0; i < NUM_POTS; i++) {
    uint32_t sum = 0;
    for (uint8_t s = 0; s < ADC_SAMPLES; s++) {
      sum += analogRead(POT_PINS[i]);
    }
    uint16_t raw   = sum / ADC_SAMPLES;  // 0-4095
    uint8_t  value = raw >> 5;           // -> 0-127

    if (raw >= 4080) value = 127;        // snap to exact endpoints
    if (raw <= 15)   value = 0;

    if (abs((int)value - (int)lastCCValue[i]) >= CC_THRESHOLD) {
      MIDI.controlChange(CC_NUMBERS[i], value);
      lastCCValue[i] = value;
    }
  }
}

void readI2CInputs() {
  uint8_t report[3];
  Wire.requestFrom(I2C_MACROPAD_ADDR, sizeof(report));

  if (Wire.available() < (int)sizeof(report)) {
    macropadConnected = false;
    Wire.flush();
    return;
  }
  macropadConnected = true;

  for (uint8_t i = 0; i < sizeof(report); i++) {
    report[i] = Wire.read();
  }

  for (uint8_t id = 0; id < MACROPAD_NUM_KEYS; id++) {
    bool pressed = (report[id / 8] >> (id % 8)) & 0x01;
    if (pressed != macropadKeyState[id]) {
      macropadKeyState[id] = pressed;
      uint8_t note = MACROPAD_FIRST_NOTE + id;
      if (pressed) {
        MIDI.noteOn(note, 127);
      } else {
        MIDI.noteOff(note, 0);
      }
    }
  }
}

void setup() {
  for (uint8_t r = 0; r < NUM_ROWS; r++) {
    pinMode(ROW_PINS[r], OUTPUT);
    digitalWrite(ROW_PINS[r], HIGH);
  }
  for (uint8_t c = 0; c < NUM_COLS; c++) {
    pinMode(COL_PINS[c], INPUT_PULLUP);
  }

  analogReadResolution(12);
  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);

  MIDI.begin();
  USB.begin();
}

void loop() {
  scanMatrix();
  readPots();
  readI2CInputs();
}

#endif
