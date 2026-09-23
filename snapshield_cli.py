#!/usr/bin/env python3
"""
SnapShield AI - Developer & Enterprise Command-Line Interface (CLI)
Target: Qualcomm Snapdragon X Elite (Hexagon NPU 45 TOPS) / HP OmniBook
Provides instant terminal scanning, cryptographic verification, and hardware profiling.
"""

import sys
import os
import time
import argparse
import json

sys.path.append(os.path.dirname(__file__))
from core.pii_sanitizer import PIISanitizer
from core.npu_engine import SnapDragonNPUEngine
from core.cryptographic_audit_ledger import CryptographicAuditLedger
from core.qnn_native_bridge import QnnNativeHarness

ASCII_BANNER = r"""
  ██████  ███    ██  █████  ██████  ███████ ██   ██ ██ ███████ ██      ██████  
 ██       ████   ██ ██   ██ ██   ██ ██      ██   ██ ██ ██      ██      ██   ██ 
 ███████  ██ ██  ██ ███████ ██████  ███████ ███████ ██ █████   ██      ██   ██ 
      ██  ██  ██ ██ ██   ██ ██           ██ ██   ██ ██ ██      ██      ██   ██ 
 ██████   ██   ████ ██   ██ ██      ███████ ██   ██ ██ ███████ ███████ ██████  
"""

def cmd_scan(args):
    print(ASCII_BANNER)
    print("=" * 75)
    print("   SnapShield AI - Native C SIMD & Hexagon NPU Scanner")
    print("=" * 75)

    sanitizer = PIISanitizer()
    text = args.text
    if not text and args.file:
        if os.path.exists(args.file):
            with open(args.file, "r") as f:
                text = f.read()
        else:
            print(f"[ERROR] File not found: {args.file}")
            return

    if not text:
        text = "DATABASE_URL=postgresql://admin:SecretPass2026@db.corp.net:5432/main with key sk-proj-1234567890abcdefghijklmnop and Aadhaar 5482 9102 3849."

    print(f"\n[INPUT TEXT ({len(text)} chars)]:\n{text[:120]}...\n")

    t0 = time.perf_counter()
    res = sanitizer.sanitize_text(text, mode=args.mode)
    elapsed_ms = (time.perf_counter() - t0) * 1000

    print("=" * 75)
    print(f"[SANITIZED RESULT] (Processed in {elapsed_ms:.2f} ms):")
    print("=" * 75)
    print(res["sanitized_text"])
    print("-" * 75)
    print(f"Entities Detected: {res['entities_detected_count']}")
    for e in res["entities_audit"]:
        print(f"  * {e['type']}: {e['preview']} -> {e['replacement']}")

    if res.get("native_acceleration"):
        print(f"\n[NATIVE SIMD ACCELERATION ACTIVE]: Latency: {res['native_acceleration']['latency_microseconds']} µs | Peak: 45 TOPS")

def cmd_verify(args):
    print("=" * 75)
    print("   SnapShield AI - Cryptographic Merkle-Tree Ledger Auditor")
    print("=" * 75)
    ledger = CryptographicAuditLedger()
    status = ledger.verify_ledger_integrity()
    print(f"Ledger File: {ledger.ledger_file}")
    print(f"Total Blocks: {status['total_blocks']}")
    print(f"Latest Block Hash: {status['latest_block_hash']}")
    print(f"Cryptographic Verification: {'[PASS] (Tamper-Proof)' if status['valid'] else '[FAIL] (Integrity Violation)'}")

def cmd_info(args):
    qnn = QnnNativeHarness()
    engine = SnapDragonNPUEngine()
    print("=" * 75)
    print("   SnapShield AI - Qualcomm Snapdragon & Hexagon HTP Hardware Specs")
    print("=" * 75)
    print(f"Target OEM:         {engine.SNAPDRAGON_X_ELITE_SPEC['device_target']}")
    print(f"Silicon Accelerator: {engine.SNAPDRAGON_X_ELITE_SPEC['npu_name']}")
    print(f"Peak Compute:       {engine.SNAPDRAGON_X_ELITE_SPEC['peak_tops']} TOPS")
    print(f"Typical Active TDP: {engine.SNAPDRAGON_X_ELITE_SPEC['typical_tdp_watts']} Watts")
    print(f"Host CPU TDP:       {engine.SNAPDRAGON_X_ELITE_SPEC['cpu_tdp_watts']} Watts")
    print(f"Energy Efficiency:  {engine.SNAPDRAGON_X_ELITE_SPEC['energy_efficiency_gain']}")
    print(f"VTCM Partitioning:  8.0 MB Vector Tightly Coupled Memory")
    print(f"Power Profile:      {qnn.configure_htp_power_profile('BURST')['voltage_corner']} (Burst Mode)")

def cmd_benchmark(args):
    from benchmarks.enterprise_evaluation_suite import evaluate_enterprise_accuracy
    evaluate_enterprise_accuracy()

def main():
    parser = argparse.ArgumentParser(description="SnapShield AI CLI")
    subparsers = parser.add_subparsers(dest="command")

    # scan
    p_scan = subparsers.add_parser("scan", help="Scan text or file for credentials")
    p_scan.add_argument("--text", "-t", type=str, help="Text to scan")
    p_scan.add_argument("--file", "-f", type=str, help="File to scan")
    p_scan.add_argument("--mode", "-m", choices=["mask", "pseudonymize"], default="mask")

    # verify
    subparsers.add_parser("verify", help="Verify Merkle audit ledger integrity")

    # info
    subparsers.add_parser("info", help="Display Qualcomm Hexagon hardware specifications")

    # benchmark
    subparsers.add_parser("benchmark", help="Run 1,000-incident enterprise benchmark evaluation")

    args = parser.parse_args()
    if args.command == "scan":
        cmd_scan(args)
    elif args.command == "verify":
        cmd_verify(args)
    elif args.command == "info":
        cmd_info(args)
    elif args.command == "benchmark":
        cmd_benchmark(args)
    else:
        cmd_scan(argparse.Namespace(text=None, file=None, mode="mask"))

if __name__ == "__main__":
    main()
