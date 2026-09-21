"""Unit tests for SnapShield PII and Secret Sanitization Engine."""

import pytest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from core.pii_sanitizer import PIISanitizer

@pytest.fixture
def sanitizer():
    return PIISanitizer()

def test_openai_key_redaction(sanitizer):
    raw = "My test key is sk-proj-1234567890abcdefghijklmnopqrstuvwxyz and more."
    res = sanitizer.sanitize_text(raw)
    assert "[REDACTED_OPENAI_KEY]" in res["sanitized_text"]
    assert res["entities_detected_count"] >= 1
    assert not res["is_clean"]

def test_aws_key_redaction(sanitizer):
    raw = "export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE"
    res = sanitizer.sanitize_text(raw)
    assert "[REDACTED_AWS_KEY]" in res["sanitized_text"]
    assert res["entities_detected_count"] == 1

def test_indian_aadhaar_redaction(sanitizer):
    raw = "Client identification: 5482 9102 3849 for KYC processing."
    res = sanitizer.sanitize_text(raw)
    assert "[REDACTED_AADHAAR_ID]" in res["sanitized_text"]
    assert "5482" not in res["sanitized_text"]

def test_indian_pan_redaction(sanitizer):
    raw = "Tax ID PAN number: ABCDE1234F recorded."
    res = sanitizer.sanitize_text(raw)
    assert "[REDACTED_PAN_CARD]" in res["sanitized_text"]
    assert "ABCDE1234F" not in res["sanitized_text"]

def test_database_url_redaction(sanitizer):
    raw = "DATABASE_URL=postgresql://admin:super_secret_password_2026@db.corp.internal:5432/main"
    res = sanitizer.sanitize_text(raw)
    assert "[REDACTED_DATABASE_CONNECTION_URI]" in res["sanitized_text"]
    assert "super_secret_password_2026" not in res["sanitized_text"]

def test_reversible_pseudonymization(sanitizer):
    raw = "Call API using key sk-proj-abcdefghijklmnopqrstuv1234567890 please."
    res = sanitizer.sanitize_text(raw, mode="pseudonymize")
    assert "<OPENAI_API_KEY_" in res["sanitized_text"]
    
    # Restore
    restored = sanitizer.restore_text(res["sanitized_text"])
    assert "sk-proj-abcdefghijklmnopqrstuv1234567890" in restored
