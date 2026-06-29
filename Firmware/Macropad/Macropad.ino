// Soundproject - Macropad (I2C slave)
//
// 4x5 diode-protected button matrix (20 keys, D1-D20 on the schematic)
// Scans locally and reports key state to the main unit over I2C on request.
//
// Board:    ESP32C3 Dev Module (ESP32C3-SuperMini)
// Wiring (per schematic):
//   Y1=GPIO10  Y2=GPIO9  Y3=GPIO8  Y4=GPIO5   (INPUT_PULLUP)
//   X1=GPIO0   X2=GPIO1  X3=GPIO2  X4=GPIO3  X5=GPIO4   (driven, idle HIGH)
//   SDA=GPIO6  SCL=GPIO7
//
// Diodes point Y -> X (cathode toward the X row), so X must be the driven
// side (current needs to flow from the pulled-up Y line, through the
// switch and diode, into the driven-low X line) and Y must be sensed.
// If presses come out inverted or don't register, your diodes are
// oriented the other way - swap OUTPUT/INPUT_PULLUP between Y and X below
// rather than rewiring.

#include <Arduino.h>
#include <Wire.h>

const uint8_t I2C_ADDR = 0x42;
const uint8_t I2C_SDA_PIN = 6;
const uint8_t I2C_SCL_PIN = 7;

const uint8_t Y_PINS[] = {10, 9, 8, 5};         // Y1, Y2, Y3, Y4 - INPUT_PULLUP
const uint8_t X_PINS[] = {0, 1, 2, 3, 4};       // X1, X2, X3, X4, X5 - OUTPUT, idle HIGH
const uint8_t NUM_Y = sizeof(Y_PINS) / sizeof(Y_PINS[0]);
const uint8_t NUM_X = sizeof(X_PINS) / sizeof(X_PINS[0]);
const uint8_t NUM_KEYS = NUM_Y * NUM_X;          // 20
const uint16_t DEBOUNCE_MS = 20;

// Maps [y][x] -> key number matching the diode labels (D1-D20) on the schematic.
const uint8_t KEY_ID[NUM_Y][NUM_X] = {
  // X1   X2   X3   X4   X5
  {  17,   1,   2,   3,   4 },   // Y1
  {  18,   5,   6,   7,   8 },   // Y2
  {  19,   9,  10,  11,  12 },   // Y3
  {  20,  13,  14,  15,  16 },   // Y4
};

bool keyState[NUM_Y][NUM_X] = {{false}};
unsigned long lastChangeMs[NUM_Y][NUM_X] = {{0}};

// 3 bytes = 24 bits, one bit per key (bit (id-1) of byte (id-1)/8), bits 21-24 unused.
volatile uint8_t i2cReport[3] = {0, 0, 0};

void scanMatrix() {
  uint8_t report[3] = {0, 0, 0};

  for (uint8_t x = 0; x < NUM_X; x++) {
    digitalWrite(X_PINS[x], LOW);
    delayMicroseconds(30);  // let the pulled-up Y line settle through the diode

    for (uint8_t y = 0; y < NUM_Y; y++) {
      bool pressed = (digitalRead(Y_PINS[y]) == LOW);
      unsigned long now = millis();

      if (pressed != keyState[y][x] && (now - lastChangeMs[y][x]) >= DEBOUNCE_MS) {
        keyState[y][x] = pressed;
        lastChangeMs[y][x] = now;
      }
    }

    digitalWrite(X_PINS[x], HIGH);
  }

  for (uint8_t y = 0; y < NUM_Y; y++) {
    for (uint8_t x = 0; x < NUM_X; x++) {
      if (keyState[y][x]) {
        uint8_t id = KEY_ID[y][x] - 1;  // 0-19
        report[id / 8] |= (1 << (id % 8));
      }
    }
  }

  noInterrupts();
  i2cReport[0] = report[0];
  i2cReport[1] = report[1];
  i2cReport[2] = report[2];
  interrupts();
}

void onI2CRequest() {
  Wire.write((const uint8_t*)i2cReport, sizeof(i2cReport));
}

void setup() {
  for (uint8_t y = 0; y < NUM_Y; y++) {
    pinMode(Y_PINS[y], INPUT_PULLUP);
  }
  for (uint8_t x = 0; x < NUM_X; x++) {
    pinMode(X_PINS[x], OUTPUT);
    digitalWrite(X_PINS[x], HIGH);
  }

  Wire.begin((uint8_t)I2C_ADDR, I2C_SDA_PIN, I2C_SCL_PIN);
  Wire.onRequest(onI2CRequest);
}

void loop() {
  scanMatrix();
}
