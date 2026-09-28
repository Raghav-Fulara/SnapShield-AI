"""
SnapShield AI - Vision Screen Sentinel
Optimized for real-time screen frame redaction on Snapdragon Copilot+ HP PCs.
Detects sensitive credentials/PII regions and renders real-time blur/mask overlays.
"""

import cv2
import numpy as np
import base64
import time
from typing import Dict, List, Tuple, Any

class VisionSentinel:
    """
    On-device computer vision engine for detecting and blurring
    confidential screen coordinates with sub-15ms NPU target latency.
    """

    def __init__(self, npu_engine=None):
        self.npu_engine = npu_engine

    def redact_image_buffer(self, image_bytes: bytes, sensitivity: str = "high") -> Dict[str, Any]:
        """
        Takes raw image bytes (PNG/JPEG), simulates on-device NPU OCR/bounding box detection,
        and paints redaction boxes over sensitive regions.
        """
        start_time = time.perf_counter()
        
        # Decode image from buffer
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Invalid image buffer provided.")

        h, w, _ = img.shape
        redacted_img = img.copy()

        # Simulate intelligent NPU OCR bounding-box detection
        # Generates realistic bounding boxes for sensitive screen elements (tokens, passwords, keys)
        detected_boxes = []

        # Example candidate sensitive zones for demo:
        # Detect bright text lines or sample candidate areas
        sample_boxes = [
            {"label": "SECRET_KEY", "box": (int(w * 0.15), int(h * 0.28), int(w * 0.45), int(h * 0.08))},
            {"label": "PASS_CREDENTIAL", "box": (int(w * 0.15), int(h * 0.42), int(w * 0.35), int(h * 0.08))},
            {"label": "PAN_ID", "box": (int(w * 0.55), int(h * 0.65), int(w * 0.30), int(h * 0.08))}
        ]

        for item in sample_boxes:
            bx, by, bw, bh = item["box"]
            # Ensure within bounds
            bx = max(0, min(bx, w - 10))
            by = max(0, min(by, h - 10))
            bw = min(bw, w - bx)
            bh = min(bh, h - by)

            if bw > 5 and bh > 5:
                # Apply heavy Gaussian blur or black privacy rectangle
                roi = redacted_img[by:by+bh, bx:bx+bw]
                blurred_roi = cv2.GaussianBlur(roi, (51, 51), 30)
                redacted_img[by:by+bh, bx:bx+bw] = blurred_roi

                # Overlay discreet privacy border and watermark badge
                cv2.rectangle(redacted_img, (bx, by), (bx + bw, by + bh), (0, 0, 255), 2)
                cv2.putText(
                    redacted_img,
                    f"[SNAPSHIELD PROTECTED: {item['label']}]",
                    (bx + 4, max(15, by - 6)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.45,
                    (0, 0, 255),
                    1,
                    cv2.LINE_AA
                )
                detected_boxes.append({
                    "label": item["label"],
                    "coordinates": {"x": bx, "y": by, "width": bw, "height": bh}
                })

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # Encode back to JPEG base64
        _, buffer = cv2.imencode('.jpg', redacted_img, [cv2.IMWRITE_JPEG_QUALITY, 85])
        encoded_image = base64.b64encode(buffer).decode('utf-8')

        return {
            "image_width": w,
            "image_height": h,
            "detected_regions_count": len(detected_boxes),
            "detected_boxes": detected_boxes,
            "latency_ms": elapsed_ms,
            "npu_target_latency_ms": 11.4,
            "sanitized_image_base64": f"data:image/jpeg;base64,{encoded_image}"
        }
