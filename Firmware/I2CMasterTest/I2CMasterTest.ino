// I2C master test for ESP32-S3.
// Polls slave at 0x42 every second and prints the 3 received bytes.
// Open Serial Monitor at 115200 baud.
//
// Board:   ESP32S3 Dev Module
// SDA=GPIO8  SCL=GPIO9

#include <Arduino.h>
#include <Wire.h>

const uint8_t I2C_SDA_PIN = 8;
const uint8_t I2C_SCL_PIN = 9;
const uint8_t SLAVE_ADDR  = 0x42;
const uint8_t READ_BYTES  = 3;

uint32_t successCount = 0;
uint32_t failCount    = 0;

void setup() {
  Serial.begin(115200);
  delay(3000);
  Serial.println("=== I2C master test (S3) ===");
  Serial.println("Polling slave 0x42 every second...");

  Wire.begin((int)I2C_SDA_PIN, (int)I2C_SCL_PIN);
  Wire.setClock(100000);
}

void loop() {
  Wire.requestFrom(SLAVE_ADDR, READ_BYTES);

  if (Wire.available() < READ_BYTES) {
    failCount++;
    Serial.print("FAIL  (no response)  total fails: ");
    Serial.println(failCount);
  } else {
    uint8_t b0 = Wire.read();
    uint8_t b1 = Wire.read();
    uint8_t b2 = Wire.read();
    successCount++;
    Serial.print("OK  0x");
    Serial.print(b0, HEX);
    Serial.print(" 0x");
    Serial.print(b1, HEX);
    Serial.print(" 0x");
    Serial.print(b2, HEX);
    Serial.print("  counter=");
    Serial.print(b2);
    Serial.print("  total ok: ");
    Serial.println(successCount);
  }

  delay(1000);
}
