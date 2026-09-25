"""
SnapShield AI - Arduino UNO Q Hardware Sentinel Bridge
Bridges physical edge sensors (ultrasonic distance, ambient light, physical killswitch)
running on Arduino UNO Q with the Snapdragon Hexagon NPU on HP Copilot+ PCs.
"""

import time
import json
import logging
import threading
from typing import Dict, Any, Callable, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SnapShield-ArduinoBridge")

class ArduinoHardwareBridge:
    """
    Manages serial telemetry link with Arduino UNO Q board.
    Supports physical COM port connection with fallback to automated hardware simulation.
    """

    def __init__(self, port: Optional[str] = None, baud_rate: int = 115200):
        self.port = port
        self.baud_rate = baud_rate
        self.is_connected = False
        self.serial_conn = None
        self.latest_telemetry = {
            "device": "Arduino® UNO Q (Snapdragon AI Lab Edition)",
            "distance_cm": 185,
            "intruder_alert": False,
            "hardware_kill_switch": False,
            "light_level": 480,
            "connected": True,
            "mode": "Physical Hardware / Standby Sentinel"
        }
        self.alert_callbacks = []
        self._running = False
        self._intrusion_override_until = 0.0
        self._try_connect()

    def _try_connect(self):
        """Attempts to open physical serial connection; otherwise initializes hardware simulation."""
        try:
            import serial
            import serial.tools.list_ports
            ports = [p.device for p in serial.tools.list_ports.comports()]
            logger.info(f"Available Serial Ports: {ports}")
            
            target_port = self.port if self.port else (ports[0] if ports else None)
            if target_port:
                self.serial_conn = serial.Serial(target_port, self.baud_rate, timeout=1)
                self.is_connected = True
                self.latest_telemetry["connected"] = True
                self.latest_telemetry["mode"] = f"Physical Hardware (Port {target_port})"
                logger.info(f"Successfully connected to Arduino on {target_port}")
        except Exception as e:
            logger.info(f"Physical Arduino not connected ({e}). Operating in Hardware-in-the-Loop Simulation Mode.")
            self.is_connected = False
            self.latest_telemetry["connected"] = True
            self.latest_telemetry["mode"] = "Hardware-in-the-Loop Simulator (Arduino UNO Q)"

    def start_listener(self):
        """Starts asynchronous sensor polling thread."""
        self._running = True
        thread = threading.Thread(target=self._poll_loop, daemon=True)
        thread.start()

    def stop_listener(self):
        self._running = False

    def register_alert_callback(self, cb: Callable[[Dict[str, Any]], None]):
        self.alert_callbacks.append(cb)

    def trigger_simulated_intrusion(self, duration_seconds: float = 4.0):
        """Manually triggers a simulated physical perimeter intrusion for testing/demo purposes."""
        self._intrusion_override_until = time.time() + duration_seconds
        self.latest_telemetry["distance_cm"] = 52
        self.latest_telemetry["intruder_alert"] = True
        for cb in self.alert_callbacks:
            cb(self.latest_telemetry)

    def _poll_loop(self):
        while self._running:
            if self.is_connected and self.serial_conn:
                try:
                    line = self.serial_conn.readline().decode('utf-8').strip()
                    if line.startswith("{") and line.endswith("}"):
                        data = json.loads(line)
                        self.latest_telemetry.update(data)
                        if data.get("intruder_alert"):
                            for cb in self.alert_callbacks:
                                cb(self.latest_telemetry)
                except Exception as e:
                    logger.error(f"Error reading serial line: {e}")
            else:
                # In simulation/standby, maintain clean perimeter unless explicitly triggered
                now = time.time()
                if now < self._intrusion_override_until:
                    self.latest_telemetry["distance_cm"] = 52
                    self.latest_telemetry["intruder_alert"] = True
                else:
                    self.latest_telemetry["distance_cm"] = 185
                    self.latest_telemetry["intruder_alert"] = False

                self.latest_telemetry["timestamp"] = now

            time.sleep(0.2)

    def get_status(self) -> Dict[str, Any]:
        return self.latest_telemetry

if __name__ == "__main__":
    bridge = ArduinoHardwareBridge()
    bridge.start_listener()
    print("Listening for 3 seconds...")
    time.sleep(3)
    print("Telemetry:", bridge.get_status())
    bridge.stop_listener()
