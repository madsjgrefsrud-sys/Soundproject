// Macropad master test for ESP32-S3.
// Polls the C3 macropad over I2C and prints key press/release events.
// Open Serial Monitor at 115200 baud.
//
// Board:   ESP32S3 Dev Module
// SDA=GPIO8  SCL=GPIO9
// Run MacropadTest.ino on the C3 at the same time.

#include <Arduino.h>
#include <Wire.h>

const uint8_t I2C_SDA_PIN       = 8;
const uint8_t I2C_SCL_PIN       = 9;
const uint8_t MACROPAD_ADDR     = 0x42;
const uint8_t MACROPAD_NUM_KEYS = 20;

bool keyState[MACROPAD_NUM_KEYS] = {false};
bool macropadConnected           = false;

void setup() {
  Serial.begin(115200);
  delay(3000);
  Serial.println("=== Macropad master test (S3) ===");
  Serial.println("Polling C3 macropad at 0x42...");

  Wire.begin((int)I2C_SDA_PIN, (int)I2C_SCL_PIN);
  Wire.setClock(100000);
}

void loop() {
  uint8_t report[3] = {0, 0, 0};

  Wire.requestFrom(MACROPAD_ADDR, (uint8_t)3);

  if (Wire.available() < 3) {
    if (macropadConnected) {
      Serial.println("Macropad disconnected!");
      macropadConnected = false;
    }
    delay(500);
    return;
  }

  if (!macropadConnected) {
    Serial.println("Macropad connected.");
    macropadConnected = true;
  }

  for (uint8_t i = 0; i < 3; i++) {
    report[i] = Wire.read();
  }

  for (uint8_t id = 0; id < MACROPAD_NUM_KEYS; id++) {
    bool pressed = (report[id / 8] >> (id % 8)) & 0x01;
    if (pressed != keyState[id]) {
      keyState[id] = pressed;
      Serial.print(pressed ? "PRESS   " : "RELEASE ");
      Serial.print("KEY=D");
      Serial.println(id + 1);
    }
  }

  delay(10);
}
