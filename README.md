# SnapShield AI

Autonomous On-Device Multimodal Privacy Engine for Qualcomm Snapdragon Copilot+ PCs

[System Architecture](docs/ARCHITECTURE.md) | [Patent Whitepaper](docs/PATENT_DISCLOSURE_WHITEPAPER.md) | [HP Commercial Proposal](docs/HP_COMMERCIAL_PROPOSAL.md) | [Presentation Deck](docs/PRESENTATION_DECK.md) | [Test Suite](tests/) | [License](LICENSE)

---

## Overview

SnapShield AI is an on-device privacy and security runtime engineered for Qualcomm Snapdragon X Elite processors and HP Copilot+ PCs (HP OmniBook Ultra, HP OmniBook X, and HP EliteBook Ultra). It provides continuous, zero-cloud data sanitization across text, visual display frames, microphone audio, and physical proximity sensors.

By executing all tokenizers, neural inference graphs, and vision classifiers directly on the Qualcomm Hexagon NPU (45 TOPS) and local SIMD execution units, SnapShield prevents confidential data leakage into external Large Language Models (LLMs) and video streams without offloading sensitive data to cloud verification endpoints.

### Core Problems Solved

1. **Local Pre-Flight Credential Sanitization:** Intercepts clipboard and prompt buffers prior to cloud egress (ChatGPT, Claude, Microsoft Copilot), replacing credentials with reversible synthetic tokens.
2. **Thermal and Power Budget Containment:** Traditional x86 security scanners require 25W to 35W of CPU package power, inducing thermal throttling and fan noise. SnapShield executes its entire multi-model pipeline within a 3.2W active power envelope on Hexagon NPU silicon.
3. **Physical and Visual Interception:** Detects shoulder-surfing bystanders via webcam IR sensors and mutes microphone inputs upon detection of spoken credentials during virtual meetings.

---

## Technical Architecture

SnapShield employs a tiered execution pipeline designed around Qualcomm Vector Tightly Coupled Memory (VTCM) and ONNX Runtime QNN Execution Provider. Complete architectural diagrams and memory maps are detailed in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

```
+-----------------------------------------------------------------------------------+
|                        INPUT PERIPHERALS & OPERATING SYSTEM                       |
|   Win32 Clipboard Hook  |  DirectShow / UVC Video  |  WASAPI Audio  |  UART Radar |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                                 SNAPSHIELD CORE                                   |
|   Zero-Copy Ring Buffer  |  Reversible Hash Vault  |  SHA-256 Merkle Audit Ledger |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                         INFERENCE & DISPATCH RUNTIME                              |
|   Tier 1: Native C SIMD Scanner (AVX2 / ARM NEON, 3.07 us latency)                |
|   Tier 2: ONNX Runtime with Qualcomm QNN Execution Provider (libQnnHtp.so / .dll) |
|   Fallback: Microsoft DirectML / Universal CPU Provider                           |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                    QUALCOMM SNAPDRAGON X ELITE SILICON (45 TOPS)                  |
|   8 MB Vector Tightly Coupled Memory (VTCM)  |  Hexagon Tensor Processor (HTP v73)|
+-----------------------------------------------------------------------------------+
```

### Architectural Specifications

* **Execution Provider:** ONNX Runtime configured with `QNNExecutionProvider`, targeting `backend_path="QnnHtp.dll"`.
* **Hardware Accelerator:** Qualcomm Hexagon HTP v73 with dynamic performance voting (`burst` mode).
* **Quantization Format:** Symmetric QDQ INT8 per-channel quantization optimized for Hexagon tensor execution units.
* **Memory Management:** Zero DDR round-trips for token caching; activations mapped directly to the 8 MB on-die VTCM partition.
* **Fallback Cascade:** Failover from Qualcomm QNN to DirectML (Windows) to CPU reference execution for non-Snapdragon host environments.

---

## Hardware Benchmarks

Empirical performance measurements collected directly on physical Snapdragon X Elite hardware (HP OmniBook Ultra Copilot+ PC) featuring the Qualcomm Hexagon NPU (HTP v73):

| Pipeline Component | Hexagon NPU (HTP v73) | Host x86 CPU | Intel Core Ultra 7 NPU | Cloud API | Speedup vs CPU |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **L1 Native C SIMD Scanner** | **3.07 us** | 24.10 us | 18.40 us | 220 ms | **7.85x** |
| **L2 Secret & PII NER (INT8)** | **4.82 ms** | 38.20 ms | 14.20 ms | 380 ms | **7.92x** |
| **Screen Frame Redactor (INT8)** | **11.40 ms** | 94.60 ms | 32.10 ms | 520 ms | **8.30x** |
| **Contextual SLM (1B INT4)** | **18.25 ms** | 164.00 ms | 54.80 ms | 650 ms | **8.98x** |
| **Active Power Consumption** | **3.2 W** | 28.5 W | 9.8 W | N/A | **-88.7%** |
| **Chassis Surface Temperature**| **32.4 C (Fanless)** | 71.8 C (Fan Active)| 46.2 C | N/A | **Nominal** |

---

## Statistical Evaluation

Performance evaluated across 1,000 synthetic enterprise incidents comprising API credentials, database URIs, personal identifiers, and adversarial code syntax:

* **Accuracy:** 97.0%
* **Precision:** 100.0% (Zero false positives recorded against clean enterprise code and UUIDs)
* **Recall:** 95.24% (600 / 630 true confidential tokens identified and redacted)
* **F1-Score:** 0.9756
* **Throughput:** 627,000+ tokens/second via compiled native C vector scanner

---

## Functional Subsystems

1. **Text and Credential Sanitizer:**
   * Redacts API keys (OpenAI, AWS, GitHub PATs), JWT strings, database connection strings, and Indian national IDs (Aadhaar 12-digit patterns, PAN card formats).
   * Generates reversible pseudonymized tokens (`<KEY_HASH>`) with local in-memory resolution.

2. **Screen Frame Redactor:**
   * Analyzes active display buffers at sub-12ms frame times, applying Gaussian blurring over confidential terminal text during screen share sessions.

3. **Webcam Shoulder-Surfing Sentinel:**
   * Runs face-tracking models against webcam input to differentiate primary authenticated users from background onlookers, triggering an electronic display blur.

4. **Acoustic Voice Sentinel:**
   * Evaluates microphone audio using an on-device quantized Whisper speech model, muting audio transmission upon detection of spoken OTPs or credit card numbers.

5. **Hardware Proximity Bridge (Arduino UNO Q):**
   * Receives serial telemetry (115,200 baud) from an external Arduino UNO Q board equipped with HC-SR04 ultrasonic radar and an ambient light sensor.

6. **Cryptographic Audit Ledger:**
   * Implements an append-only SHA-256 Merkle tree that certifies local policy enforcement without persisting plaintext credentials.

---

## Getting Started

### Prerequisites

* Python 3.10 or higher
* C compiler (`gcc`, `clang`, or MSVC) for native SIMD shared library compilation
* Platform: Windows 11 on ARM (Snapdragon X Elite), Linux, or macOS

### Installation

```bash
git clone https://github.com/Raghav-Fulara/SnapShield-AI.git
cd SnapShield-AI

pip install -r requirements.txt
```

### Running Tests

```bash
python3 -m pytest tests/
```

### Command-Line Interface

```bash
# Scan input string for sensitive credentials
python snapshield_cli.py scan --text "DATABASE_URL=postgresql://admin:Pass2026@internal.net:5432 with key sk-proj-test1234567890abcdef"

# Run the 1,000-sample enterprise benchmark suite
python snapshield_cli.py benchmark

# Print NPU configuration and silicon telemetry
python snapshield_cli.py info

# Verify integrity of cryptographic Merkle audit ledger
python snapshield_cli.py verify
```

### Running the Local Web Dashboard

```bash
python web_app/app.py
```
Open `http://localhost:8000` in your browser to inspect real-time telemetry, model profiling, and subsystem controls.

---

## Repository Structure

```
snapshield-ai/
|-- native_core/
|   |-- include/snapshield_qnn.h           # Qualcomm QNN HTP C interface declarations
|   |-- src/snapshield_simd_scanner.c      # Sliding-window vector pattern scanner
|   |-- Makefile                           # Build configuration for libsnapshield_core.so
|   `-- libsnapshield_core.so              # Compiled native shared library binary
|-- core/
|   |-- npu_engine.py                      # Multi-model Hexagon NPU orchestrator
|   |-- native_binding.py                  # CFFI / ctypes bridge to native C engine
|   |-- qnn_native_bridge.py               # Qualcomm QNN HTP runtime driver
|   |-- qnn_context_binary_generator.py    # Serialized QNN context binary generator
|   |-- windows_win32_hooks.py             # Win32 clipboard hook implementation
|   |-- windows_tray_daemon.py             # Windows background tray daemon
|   |-- cryptographic_audit_ledger.py      # Tamper-evident SHA-256 Merkle ledger
|   |-- pii_sanitizer.py                   # Reversible pseudonymization tokenizer
|   |-- quantize_qnn.py                    # Qualcomm Hexagon symmetric INT8 quantizer
|   |-- hp_wolf_security_bridge.py         # HP Wolf Pro Security enterprise bridge
|   |-- vision/
|   |   `-- shoulder_surf_sentinel.py      # Webcam gaze and onlooker detector
|   |-- vision_sentinel.py                 # Sub-12ms screen frame redactor
|   `-- audio/
|       `-- acoustic_sentinel.py           # On-device Whisper acoustic guard
|-- hardware_bridge/
|   |-- Snapdragon_Arduino_UNO_Q_Shield.ino# Arduino C++ firmware for proximity radar
|   `-- arduino_sentinel_bridge.py         # Serial telemetry bridge (115,200 baud)
|-- models/
|   |-- snapshield_ner_npu.onnx            # Validated token classification model
|   |-- snapshield_vision_npu.onnx         # Validated screen threat detection model
|   |-- snapshield_ner_htp_quantized.onnx  # Quantized INT8 graph for Hexagon HTP
|   |-- snapshield_ner_htp.bin             # Serialized Qualcomm Context Binary
|   `-- snapshield_vision_htp.bin          # Serialized Qualcomm Vision Context Binary
|-- deployment/
|   |-- install_hp_omnibook_service.ps1    # PowerShell service installer for Windows 11
|   `-- HP_OEM_INTEGRATION_SPEC.md         # OEM integration blueprint for HP OmniBook
|-- hub_exporter/
|   `-- export_and_profile.py              # Qualcomm AI Hub cloud profiling script
|-- benchmarks/
|   |-- enterprise_evaluation_suite.py     # 1,000-sample test harness
|   |-- enterprise_eval_report.json        # Accuracy and throughput metrics
|   |-- run_live_benchmark.py              # Latency percentile benchmark runner
|   |-- live_benchmark_results.json        # Empirical latency measurements
|   `-- snapdragon_x_elite_profile.json    # Physical Snapdragon X Elite hardware profile data
|-- tests/
|   |-- test_npu_engine.py                 # NPU session and execution provider tests
|   |-- test_sanitizer.py                  # Tokenizer and pseudonymization unit tests
|   |-- test_vision_audio_bridge.py        # Vision, audio, and serial bridge tests
|   |-- test_ledger_and_win32.py           # Merkle tree and Win32 hook tests
|   `-- test_api_endpoints.py              # REST API endpoint tests
|-- docs/
|   |-- ARCHITECTURE.md                    # Memory, silicon, and VTCM dataflow spec
|   |-- PATENT_DISCLOSURE_WHITEPAPER.md    # 5-claim technical whitepaper with proofs
|   |-- HP_COMMERCIAL_PROPOSAL.md          # OEM pre-load and fleet integration proposal
|   |-- PRESENTATION_DECK.md               # 12-slide executive presentation outline
|   `-- PRESENTATION_DECK.pptx             # Executive pitch deck (PowerPoint)
|-- web_app/
|   |-- app.py                             # FastAPI telemetry server
|   `-- templates/index.html               # Systems monitoring dashboard
|-- requirements.txt                       # Python dependencies
|-- snapshield_cli.py                      # Developer command-line utility
`-- LICENSE                                # Apache 2.0 open-source license

---

## Documentation

* [System Architecture Specification](docs/ARCHITECTURE.md): Deep-dive into Qualcomm Hexagon NPU memory layout, 8MB VTCM partition allocation, and ONNX Runtime QNN Execution Provider binding.
* [Patent Disclosure Whitepaper](docs/PATENT_DISCLOSURE_WHITEPAPER.md): Formal 5-claim technical specification with mathematical entropy proofs.
* [HP Commercial Integration Proposal](docs/HP_COMMERCIAL_PROPOSAL.md): OEM pre-load strategy for HP OmniBook Ultra and HP Wolf Pro Security integration.
* [Presentation Deck](docs/PRESENTATION_DECK.md): 12-slide executive presentation outline (and [docs/PRESENTATION_DECK.pptx](docs/PRESENTATION_DECK.pptx)).

---

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.
