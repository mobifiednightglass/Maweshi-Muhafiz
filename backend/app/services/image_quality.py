"""
ImageQualityService — Pre-assessment image quality validation.

Analyzes images for darkness and resolution issues before they're
accepted for health assessment. Uses OpenCV for fast local checks.

Blur detection is handled separately via Gemini (see vision_provider.check_blur).

Usage:
    service = ImageQualityService()
    result = service.check_quality(image_bytes)
    # result = {"is_acceptable": bool, "issues": [...]}
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
                "issues": list[str]
            }
        """
        issues: List[str] = []

        try:
            # Decode image from bytes
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                return {
                    "is_acceptable": False,
                    "issues": ["Image could not be processed"],
                }

            # Check resolution
            height, width = img.shape[:2]
            if width < MIN_RESOLUTION[0] or height < MIN_RESOLUTION[1]:
                issues.append("Image resolution is too low")

            # Convert to grayscale for darkness analysis
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Check darkness (mean brightness)
            mean_brightness = float(gray.mean())
            if mean_brightness < DARKNESS_THRESHOLD:
                issues.append("Image is too dark")

            return {
                "is_acceptable": len(issues) == 0,
                "issues": issues,
            }

        except Exception as e:
            logger.exception("Error processing image quality check: %s", e)
            return {
                "is_acceptable": False,
                "issues": ["Image could not be processed"],
            }
