"""Integration tests for SnapShield FastAPI REST endpoints."""

import pytest
import sys
import os
from fastapi.testclient import TestClient

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from web_app.app import app

@pytest.fixture
def client():
    return TestClient(app)

def test_get_hardware_status(client):
    res = client.get("/api/hardware-status")
    assert res.status_code == 200
    data = res.json()
    assert "Snapdragon X Elite" in data["target_system"]
    assert "arduino_bridge" in data

def test_get_model_zoo(client):
    res = client.get("/api/model-zoo")
    assert res.status_code == 200
    data = res.json()
    assert data["qualcomm_ai_hub_verified"] is True
    assert len(data["models"]) == 4

def test_compliance_report(client):
    res = client.get("/api/compliance-report")
    assert res.status_code == 200
    data = res.json()
    assert "DPDPA 2023" in data["compliance_standards"][0]["standard"]
    assert data["compliance_standards"][0]["status"] == "COMPLIANT"

def test_npu_stress_test(client):
    res = client.post("/api/stress-test", json={"iterations": 15})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "STRESS_TEST_PASSED"
    assert len(data["time_series"]) == 15
    assert data["mean_latency_ms"] > 0

def test_hp_wolf_status_endpoint(client):
    res = client.get("/api/hp-wolf-status")
    assert res.status_code == 200
    data = res.json()
    assert data["hp_wolf_security_integrated"] is True
    assert "HP OmniBook" in data["target_device"]

def test_enterprise_evaluation_endpoint(client):
    res = client.get("/api/enterprise-evaluation")
    assert res.status_code == 200
    data = res.json()
    assert "confusion_matrix" in data
    assert data["statistical_metrics"]["precision_pct"] == 100.0
