/*
 * Snapdragon® AI Lab - Arduino® UNO Q Hardware Sentinel Shield
 * Designed for HP Snapdragon Copilot+ PC Physical Security Integration
 * 
 * Communicates with SnapShield AI via high-speed serial (115200 baud).
 * Broadcasts JSON telemetry:
 *   - Proximity sensor (detects physical intruders approaching from behind)
 *   - Ambient light / Tamper sensor
 *   - Hardware Privacy Physical Kill-Switch
 */

#include <Arduino.h>

const int PIN_PROXIMITY_TRIG = 9;
const int PIN_PROXIMITY_ECHO = 10;
const int PIN_HARDWARE_KILLSWITCH = 2;
const int PIN_STATUS_LED_NPU = 13;

unsigned long lastBroadcast = 0;
const unsigned long BROADCAST_INTERVAL_MS = 100; // 10Hz telemetry rate

void setup() {
  Serial.begin(115200);
  pinMode(PIN_PROXIMITY_TRIG, OUTPUT);
  pinMode(PIN_PROXIMITY_ECHO, INPUT);
  pinMode(PIN_HARDWARE_KILLSWITCH, INPUT_PULLUP);
  pinMode(PIN_STATUS_LED_NPU, OUTPUT);

  // Send hardware handshake
  Serial.println("{\"device\": \"Arduino_UNO_Q\", \"status\": \"READY\", \"firmware\": \"SnapShield_v1.4\"}");
}

long measureDistanceCm() {
  digitalWrite(PIN_PROXIMITY_TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(PIN_PROXIMITY_TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(PIN_PROXIMITY_TRIG, LOW);

  long duration = pulseIn(PIN_PROXIMITY_ECHO, HIGH, 25000); // 25ms timeout (~4m)
  if (duration == 0) return 999; // No obstacle
  return duration * 0.034 / 2;
}

void loop() {
  if (millis() - lastBroadcast >= BROADCAST_INTERVAL_MS) {
    lastBroadcast = millis();

    long distanceCm = measureDistanceCm();
    bool killSwitchActive = (digitalRead(PIN_HARDWARE_KILLSWITCH) == LOW);
    int lightLevel = analogRead(A0);

    // Physical intruder detection: someone standing closer than 85cm behind laptop
    bool physicalIntruderDetected = (distanceCm < 85 && distanceCm > 5);

    // Format telemetry payload
    Serial.print("{\"distance_cm\": ");
    Serial.print(distanceCm);
    Serial.print(", \"intruder_alert\": ");
    Serial.print(physicalIntruderDetected ? "true" : "false");
    Serial.print(", \"hardware_kill_switch\": ");
    Serial.print(killSwitchActive ? "true" : "false");
    Serial.print(", \"light_level\": ");
    Serial.print(lightLevel);
    Serial.println("}");

    // Toggle onboard LED if NPU privacy mode is triggered
    digitalWrite(PIN_STATUS_LED_NPU, physicalIntruderDetected ? HIGH : LOW);
  }

  // Handle incoming commands from Snapdragon Copilot+ PC
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd == "NPU_ARMED") {
      digitalWrite(PIN_STATUS_LED_NPU, HIGH);
    } else if (cmd == "NPU_DISARMED") {
      digitalWrite(PIN_STATUS_LED_NPU, LOW);
    }
  }
}
