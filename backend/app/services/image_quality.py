"""
ImageQualityService — Pre-assessment image quality validation.

Analyzes images for blur, darkness, and resolution issues before they're
accepted for health assessment. Uses OpenCV's Laplacian variance method
for blur detection (no external AI API needed).

Usage:
    service = ImageQualityService()
    result = service.check_quality(image_bytes)
    # result = {"is_acceptable": bool, "issues": [...], "blur_score": float}
"""

import logging
from typing import Dict, List

import cv2
import numpy as np

logger = logging.getLogger(__name__)
#image quality ko analyze krta hai
# ---------------------------------------------------------------------------
# Tunable thresholds (module-level constants for easy adjustment)
# ---------------------------------------------------------------------------

BLUR_THRESHOLD = 25.0
"""Minimum Laplacian variance. Lower values = more blur tolerance."""

DARKNESS_THRESHOLD = 50.0
"""Minimum mean pixel brightness (0-255 scale). Lower values = darker tolerance."""

MIN_RESOLUTION = (200, 200)
"""Minimum image dimensions (width, height) in pixels."""


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class ImageQualityService:
    """Validates image quality before health assessment processing."""

    def check_quality(self, image_bytes: bytes) -> Dict:
        """Analyze image quality and return validation results.

        Parameters
        ----------
        image_bytes : bytes
            Raw image data (JPEG, PNG, etc.)

        Returns
        -------
        dict
            {
                "is_acceptable": bool,
                "issues": list[str],
                "blur_score": float
            }
        """
        issues: List[str] = []
        blur_score = 0.0

        try:
            # Decode image from bytes
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                return {
                    "is_acceptable": False,
                    "issues": ["Image could not be processed"],
                    "blur_score": 0.0,
                }

            # Check resolution
            height, width = img.shape[:2]
            if width < MIN_RESOLUTION[0] or height < MIN_RESOLUTION[1]:
                issues.append("Image resolution is too low")

            # Convert to grayscale for analysis
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Check blur (Laplacian variance)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            blur_score = float(laplacian.var())
            # DEBUG: log actual blur score vs threshold for every image
            print(f"[DEBUG] Image blur_score: {blur_score:.4f}, threshold: {BLUR_THRESHOLD}", flush=True)
            logger.info("Image blur_score: %.4f, threshold: %s", blur_score, BLUR_THRESHOLD)
            if blur_score < BLUR_THRESHOLD:
                issues.append("Image is too blurry")

            # Check darkness (mean brightness)
            mean_brightness = float(gray.mean())
            if mean_brightness < DARKNESS_THRESHOLD:
                issues.append("Image is too dark")

            return {
                "is_acceptable": len(issues) == 0,
                "issues": issues,
                "blur_score": blur_score,
            }

        except Exception as e:
            logger.exception("Error processing image quality check: %s", e)
            return {
                "is_acceptable": False,
                "issues": ["Image could not be processed"],
                "blur_score": 0.0,
            }
