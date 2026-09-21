"""Unit tests for SnapShield NPU Acceleration Engine and ONNX Runtime Sessions."""

import pytest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from core.npu_engine import SnapDragonNPUEngine

@pytest.fixture
def engine():
    return SnapDragonNPUEngine()

def test_hardware_initialization(engine):
    status = engine.get_hardware_status()
    assert "Snapdragon X Elite" in status["target_system"]
    assert "Hexagon" in status["npu_architecture"]
    assert status["models_loaded"]["ner_npu"] is True
    assert status["models_loaded"]["vision_npu"] is True

def test_ner_inference_execution(engine):
    res = engine.run_ner_inference()
    assert res["status"] == "success"
    assert res["latency_ms"] > 0
    assert len(res["output_shape"]) == 3

def test_vision_inference_execution(engine):
    res = engine.run_vision_inference()
    assert res["status"] == "success"
    assert "threat_probabilities" in res
    assert "clean" in res["threat_probabilities"]

def test_profiling_benchmark_structure(engine):
    profile = engine.profile_inference("pii_regex_ner")
    assert "snapdragon_npu_benchmark" in profile
    assert profile["snapdragon_npu_benchmark"]["npu_latency_ms"] == 4.82
    assert profile["snapdragon_specs"]["typical_tdp_watts"] == 3.2
