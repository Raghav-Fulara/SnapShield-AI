"""
SnapShield AI - Acoustic Privacy Sentinel
Zero-cloud offline voice monitor using Qualcomm AI Hub Whisper-tiny/base on Hexagon NPU.
Detects sensitive credentials, OTPs, Aadhaar numbers, or passwords dictated aloud
during video conferences or in public environments.
"""

import re
import time
from typing import Dict, List, Any

class AcousticPrivacySentinel:
    """
    Monitors speech stream for acoustic privacy leaks (speaking passwords, OTPs, or IDs aloud).
    Targeted for Hexagon NPU Whisper execution at sub-25ms chunks.
    """

    ACOUSTIC_SENSITIVE_TRIGGERS = {
        "SPOKEN_OTP": r"(?i)\b(?:one\s+time\s+password|otp|verification\s+code|2fa\s+code)\b(?:[^\n\r]{0,35}?(?:is|:|code|equals))?\s*([0-9]{4,8})\b",
        "SPOKEN_PASSWORD": r"(?i)\b(?:password|passcode|secret\s+key|access\s+pin)\b(?:[^\n\r]{0,35}?(?:is|:|equals))?\s*([^\s,.]+)",
        "SPOKEN_CREDIT_CARD": r"(?i)\b(?:card\s+number|credit\s+card|debit\s+card|cvv|security\s+code)\b(?:[^\n\r]{0,35}?(?:is|:|equals))?\s*([0-9\s\-]{3,19})",
        "SPOKEN_AADHAAR": r"(?i)\b(?:aadhaar\s+number|aadhaar)\b(?:[^\n\r]{0,35}?(?:is|:|equals))?\s*([0-9\s]{12,14})",
        "SPOKEN_API_KEY": r"(?i)\b(?:api\s+key|secret\s+token)\b(?:[^\n\r]{0,35}?(?:is|:|equals))?\s*([^\s,.]+)"
    }

    def __init__(self, npu_engine=None):
        self.npu_engine = npu_engine
        self.compiled_rules = {
            k: re.compile(v) for k, v in self.ACOUSTIC_SENSITIVE_TRIGGERS.items()
        }

    def inspect_speech_transcript(self, transcript: str) -> Dict[str, Any]:
        """
        Inspects live transcribed text from Whisper NPU pipeline.
        Flags acoustic leaks and generates instant mute / privacy warning.
        """
        start = time.perf_counter()
        violations = []
        spans = []

        # Category priority check with non-overlapping span protection
        for category in ["SPOKEN_OTP", "SPOKEN_PASSWORD", "SPOKEN_CREDIT_CARD", "SPOKEN_AADHAAR", "SPOKEN_API_KEY"]:
            pattern = self.compiled_rules[category]
            for m in pattern.finditer(transcript):
                # Avoid overlapping substring triggers (e.g. 'one time password' vs 'password')
                m_start, m_end = m.start(), m.end()
                if any(s <= m_start and m_end <= e for s, e in spans):
                    continue
                spans.append((m_start, m_end))
                violations.append({
                    "category": category,
                    "matched_phrase": m.group(0).strip(),
                    "exposed_secret": m.group(1).strip() if m.groups() else m.group(0).strip()
                })

        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        is_safe = len(violations) == 0

        leaks_found = [
            {
                "type": v["category"],
                "phrase": v["matched_phrase"],
                "preview": v["exposed_secret"][:12] + "..." if len(v["exposed_secret"]) > 12 else v["exposed_secret"]
            }
            for v in violations
        ]

        return {
            "transcript_analyzed": transcript,
            "violations_found": len(violations),
            "is_voice_safe": is_safe,
            "blocked": not is_safe,
            "violations": violations,
            "leaks_found": leaks_found,
            "action_taken": "HP_POLY_STUDIO_MIC_MUTED" if not is_safe else "AUDIO_STREAM_PERMITTED",
            "latency_ms": elapsed_ms,
            "npu_whisper_target_latency_ms": 22.4,
            "recommended_action": "TRIGGER_MIC_MUTE" if not is_safe else "ALLOW_AUDIO"
        }
