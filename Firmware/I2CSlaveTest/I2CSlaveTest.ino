// I2C slave test for ESP32-C3.
// Responds to master requests with 3 known bytes + a counter.
// Open Serial Monitor at 115200 baud.
//
// Board:   ESP32C3 Dev Module
// USB CDC on Boot: Enabled
// SDA=GPIO8  SCL=GPIO9  Address=0x42

#include <Arduino.h>
#include <Wire.h>

const uint8_t I2C_ADDR    = 0x42;
const uint8_t I2C_SDA_PIN = 8;
const uint8_t I2C_SCL_PIN = 9;

volatile uint8_t requestCount = 0;

void onRequest() {
  Wire.write(0xAA);
  Wire.write(0x55);
  Wire.write(requestCount);
  requestCount++;
}

void setup() {
  Serial.begin(115200);
  delay(3000);
  Serial.println("=== I2C slave test (C3) ===");
  Serial.println("Waiting for master requests...");

  Wire.begin((uint8_t)I2C_ADDR, I2C_SDA_PIN, I2C_SCL_PIN);
  Wire.onRequest(onRequest);

  Serial.println("Slave ready at 0x42.");
}

void loop() {
  static uint8_t lastCount = 0;
  uint8_t count = requestCount;
  if (count != lastCount) {
    Serial.print("Request #");
    Serial.print(count);
    Serial.print("  sent: 0xAA 0x55 0x");
    Serial.println(count - 1, HEX);
    lastCount = count;
  }
}
