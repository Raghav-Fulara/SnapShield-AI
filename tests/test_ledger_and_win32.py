"""Unit tests for Cryptographic Audit Ledger and Win32 Hooks."""

import pytest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from core.cryptographic_audit_ledger import CryptographicAuditLedger
from core.windows_win32_hooks import Win32ClipboardSentinel
from core.pii_sanitizer import PIISanitizer
from core.hp_wolf_security_bridge import HPWolfSecurityBridge

def test_ledger_genesis_and_append(tmp_path):
    ledger_path = os.path.join(tmp_path, "test_ledger.json")
    ledger = CryptographicAuditLedger(ledger_file=ledger_path)
    
    assert len(ledger.chain) == 1
    assert ledger.chain[0]["event_type"] == "GENESIS_INITIALIZATION"

    # Add block
    sample_entities = [{"type": "OPENAI_API_KEY", "preview": "sk-proj-test"}]
    block = ledger.record_interception_event("CLIPBOARD_INTERCEPT", sample_entities)
    assert block["block_index"] == 1
    assert len(ledger.chain) == 2

    # Verify integrity
    integrity = ledger.verify_ledger_integrity()
    assert integrity["valid"] is True
    assert integrity["integrity_status"] == "CRYPTO_VERIFIED_TAMPER_PROOF"

def test_win32_clipboard_emulation():
    sanitizer = PIISanitizer()
    sentinel = Win32ClipboardSentinel(sanitizer_instance=sanitizer)
    
    test_text = "Database URI: postgresql://admin:p@ss123@db.corp.net:5432/main"
    sentinel.write_clipboard_text(test_text)
    
    res = sentinel.intercept_and_sanitize_clipboard()
    assert res["status"] == "sanitized"
    assert res["modified"] is True
    assert "[REDACTED_DATABASE_CONNECTION_URI]" in sentinel.read_clipboard_text()

def test_hp_wolf_security_bridge():
    wolf = HPWolfSecurityBridge()
    assert wolf.sure_view_active is False
    
    # Trigger Sure View privacy veil
    evt = wolf.trigger_sure_view_privacy_screen("Lurker behind shoulder at 68cm", actor_distance_cm=68.5)
    assert wolf.sure_view_active is True
    assert evt["action"] == "HP_SURE_VIEW_HARDWARE_FILTER_ACTIVATED"
    assert evt["threat_proximity_cm"] == 68.5

    # Emit CEF SIEM telemetry
    cef = wolf.emit_cef_threat_telemetry("CREDENTIAL_LEAK", 7, {"summary": "API Key redacted"})
    assert "CEF:0|HP|WolfSecurity-SnapShield" in cef
    assert "SnapShield NPU Threat Intercept" in cef

    # Deactivate Sure View
    restore = wolf.deactivate_sure_view()
    assert wolf.sure_view_active is False
    assert restore["status"] == "NORMAL_VIEWING_RESTORED"
