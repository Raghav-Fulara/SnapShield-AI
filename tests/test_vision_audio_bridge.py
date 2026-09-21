"""Unit tests for Vision Sentinel, Acoustic Sentinel, and Arduino Bridge."""

import pytest
import sys
import os
import cv2
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from core.vision_sentinel import VisionSentinel
from core.audio.acoustic_sentinel import AcousticPrivacySentinel
from hardware_bridge.arduino_sentinel_bridge import ArduinoHardwareBridge

def test_screen_frame_redaction():
    sentinel = VisionSentinel()
    # Create test image
    img = np.ones((200, 400, 3), dtype=np.uint8) * 100
    _, buf = cv2.imencode('.jpg', img)
    
    result = sentinel.redact_image_buffer(buf.tobytes())
    assert result["image_width"] == 400
    assert result["image_height"] == 200
    assert result["detected_regions_count"] >= 1
    assert "data:image/jpeg;base64," in result["sanitized_image_base64"]

def test_acoustic_privacy_detection():
    sentinel = AcousticPrivacySentinel()
    speech = "Hello team, my verification code is 829104 and login password is SummerSecret2026."
    res = sentinel.inspect_speech_transcript(speech)
    assert not res["is_voice_safe"]
    assert res["violations_found"] == 2
    assert res["recommended_action"] == "TRIGGER_MIC_MUTE"

def test_arduino_hardware_bridge():
    bridge = ArduinoHardwareBridge()
    status = bridge.get_status()
    assert "Arduino" in status["device"]
    assert "distance_cm" in status
    assert status["connected"] is True
