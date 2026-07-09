// Macropad test - prints button coords to Serial and handles I2C requests.
// Open Serial Monitor at 115200 baud.

#include <Arduino.h>
#include <Wire.h>

const uint8_t I2C_ADDR    = 0x42;
const uint8_t I2C_SDA_PIN = 8;
const uint8_t I2C_SCL_PIN = 9;

const uint8_t Y_PINS[] = {21, 20, 10, 6};
const uint8_t X_PINS[] = {0, 1, 2, 3, 4};
const uint8_t NUM_Y = sizeof(Y_PINS) / sizeof(Y_PINS[0]);
const uint8_t NUM_X = sizeof(X_PINS) / sizeof(X_PINS[0]);

const uint8_t KEY_ID[NUM_Y][NUM_X] = {
  // X1   X2   X3   X4   X5
  {  17,   1,   2,   3,   4 },  // Y1
  {  18,   5,   6,   7,   8 },  // Y2
  {  19,   9,  10,  11,  12 },  // Y3
  {  20,  13,  14,  15,  16 },  // Y4
};

bool keyState[NUM_Y][NUM_X] = {{false}};
volatile uint8_t i2cReport[3] = {0, 0, 0};
volatile uint32_t i2cRequestCount = 0;

void onI2CRequest() {
  Wire.write((const uint8_t*)i2cReport, 3);
  i2cRequestCount++;
}

void setup() {
  Serial.begin(115200);
  delay(3000);
  Serial.println("=== Macropad test ===");
  Serial.println("Press buttons to see coordinates.");
  Serial.println();

  for (uint8_t y = 0; y < NUM_Y; y++) {
    pinMode(Y_PINS[y], INPUT_PULLUP);
  }
  for (uint8_t x = 0; x < NUM_X; x++) {
    pinMode(X_PINS[x], OUTPUT);
    digitalWrite(X_PINS[x], HIGH);
  }

  Wire.begin((uint8_t)I2C_ADDR, I2C_SDA_PIN, I2C_SCL_PIN);
  Wire.onRequest(onI2CRequest);

  Serial.println("I2C slave ready at address 0x42.");
}

void loop() {
  uint8_t report[3] = {0, 0, 0};

  for (uint8_t x = 0; x < NUM_X; x++) {
    digitalWrite(X_PINS[x], LOW);
    delayMicroseconds(30);

    for (uint8_t y = 0; y < NUM_Y; y++) {
      bool pressed = (digitalRead(Y_PINS[y]) == LOW);

      if (pressed != keyState[y][x]) {
        keyState[y][x] = pressed;
        Serial.print(pressed ? "PRESS   " : "RELEASE ");
        Serial.print("Y="); Serial.print(y + 1);
        Serial.print("  X="); Serial.print(x + 1);
        Serial.print("  KEY=D"); Serial.println(KEY_ID[y][x]);
      }

      if (keyState[y][x]) {
        uint8_t id = KEY_ID[y][x] - 1;
        report[id / 8] |= (1 << (id % 8));
      }
    }

    digitalWrite(X_PINS[x], HIGH);
  }

  noInterrupts();
  i2cReport[0] = report[0];
  i2cReport[1] = report[1];
  i2cReport[2] = report[2];
  interrupts();

  // Print I2C poll count every 2 seconds so you can confirm master is talking to us.
  static uint32_t lastPrint = 0;
  static uint32_t lastCount = 0;
  if (millis() - lastPrint >= 2000) {
    lastPrint = millis();
    uint32_t count = i2cRequestCount;
    if (count != lastCount) {
      Serial.print("I2C polls from master: ");
      Serial.println(count);
      lastCount = count;
    }
  }
}
