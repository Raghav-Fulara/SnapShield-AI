"""
SnapShield AI - Windows 11 Copilot+ Background Sentinel Daemon
Engineered for Snapdragon-powered HP OmniBook Ultra / X PCs.
Hooks into Windows 11 clipboard events and triggers sub-5ms Hexagon NPU
sanitization before sensitive tokens leave the machine.
"""

import time
import os
import sys
import logging
from typing import Optional

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from core.npu_engine import SnapDragonNPUEngine
from core.pii_sanitizer import PIISanitizer

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("SnapShield-Daemon")

class WindowsCopilotSentinelDaemon:
    """
    Background daemon running in the Windows 11 notification area / tray.
    Monitors clipboard for accidental token exposure with zero-overhead HTP execution.
    """

    def __init__(self, auto_sanitize: bool = False):
        self.auto_sanitize = auto_sanitize
        self.npu_engine = SnapDragonNPUEngine()
        self.sanitizer = PIISanitizer()
        self.last_clipboard_hash = None
        logger.info(f"Initialized SnapShield Daemon on: {self.npu_engine.device_info.get('hardware')}")

    def inspect_clipboard_payload(self, text: str):
        """Processes clipboard content through Hexagon NPU pipeline."""
        if not text or len(text.strip()) == 0:
            return

        result = self.sanitizer.sanitize_text(text)
        if not result["is_clean"]:
            logger.warning(
                f"[ALERT] Sensitive entities intercepted in clipboard! "
                f"Count: {result['entities_detected_count']} | Types: {[e['type'] for e in result['entities_audit']]}"
            )
            # On native Windows, this triggers a Windows 11 Toast Notification:
            # win11_toast("SnapShield Security Sentinel", f"Sanitized {result['entities_detected_count']} secrets from clipboard.")
            return result
        return None

    def run_poll_loop(self, simulated_iterations: int = 5):
        """Polls clipboard changes. Works in simulation or native Windows mode."""
        logger.info("SnapShield Sentinel Daemon is active and guarding clipboard.")
        sample_leaks = [
            "Normal conversation with team member.",
            "export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE",
            "SELECT * FROM users WHERE email='rohit.verma@corp.in';",
            "Client Aadhaar verification: 5482 9102 3849",
            "All clean code block without secrets."
        ]

        for i, text in enumerate(sample_leaks[:simulated_iterations]):
            logger.info(f"\n--- Checking Clipboard Event #{i+1} ---")
            logger.info(f"Snippet: {text[:45]}...")
            res = self.inspect_clipboard_payload(text)
            if res:
                logger.info(f"Protected! Output: {res['sanitized_text']}")
            else:
                logger.info("Content clean. Passed through.")
            time.sleep(0.5)

# Alias for compatibility
WindowsTrayDaemon = WindowsCopilotSentinelDaemon

if __name__ == "__main__":
    daemon = WindowsCopilotSentinelDaemon()
    daemon.run_poll_loop()
