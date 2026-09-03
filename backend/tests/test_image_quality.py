"""
Regression tests for ImageQualityService.

Validates that darkness and resolution gates correctly reject unacceptable
images. Blur detection is now merged into the main Gemini assessment call
(image_too_blurry field) and is not covered here.
"""

import cv2
import numpy as np
import pytest

from app.services.image_quality import (
    DARKNESS_THRESHOLD,
    ImageQualityService,
    MIN_RESOLUTION,
)


@pytest.fixture
def service():
    return ImageQualityService()


# ---------------------------------------------------------------------------
# Helpers — generate synthetic test images as JPEG bytes
# ---------------------------------------------------------------------------

def _encode_jpeg(img: np.ndarray, quality: int = 95) -> bytes:
    """Encode a BGR numpy array to JPEG bytes."""
    _, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, quality])
    return buf.tobytes()


def _sharp_image(width=400, height=400) -> bytes:
    """Create a well-lit, correctly-sized image (passes all remaining checks)."""
    img = np.full((height, width, 3), 180, dtype=np.uint8)
    for x in range(0, width, 20):
        cv2.line(img, (x, 0), (x, height), (0, 0, 0), 2)
    for y in range(0, height, 20):
        cv2.line(img, (0, y), (width, y), (0, 0, 0), 2)
    return _encode_jpeg(img)


def _dark_image(width=400, height=400) -> bytes:
    """Create a near-black image (fails darkness check)."""
    img = np.full((height, width, 3), 5, dtype=np.uint8)
    noise = np.random.randint(0, 8, img.shape, dtype=np.uint8)
    img = cv2.add(img, noise)
    return _encode_jpeg(img)


def _small_image() -> bytes:
    """Create a correctly-lit but too-small image (fails resolution check)."""
    img = np.full((50, 50, 3), 180, dtype=np.uint8)
    for x in range(0, 50, 5):
        cv2.line(img, (x, 0), (x, 50), (0, 0, 0), 1)
    for y in range(0, 50, 5):
        cv2.line(img, (0, y), (50, y), (0, 0, 0), 1)
    return _encode_jpeg(img)


# ---------------------------------------------------------------------------
# Tests — Acceptable image
# ---------------------------------------------------------------------------

class TestAcceptableImage:
    def test_valid_image_passes(self, service):
        result = service.check_quality(_sharp_image())
        assert result["is_acceptable"] is True
        assert result["issues"] == []

    def test_return_shape(self, service):
        result = service.check_quality(_sharp_image())
        assert "is_acceptable" in result
        assert "issues" in result
        assert "blur_score" not in result


# ---------------------------------------------------------------------------
# Tests — Dark image rejected
# ---------------------------------------------------------------------------

class TestDarknessDetection:
    def test_dark_image_rejected(self, service):
        result = service.check_quality(_dark_image())
        assert result["is_acceptable"] is False
        assert any("dark" in issue.lower() for issue in result["issues"])

    def test_dark_image_issue_message(self, service):
        result = service.check_quality(_dark_image())
        assert "Image is too dark" in result["issues"]


# ---------------------------------------------------------------------------
# Tests — Low-resolution image rejected
# ---------------------------------------------------------------------------

class TestResolutionDetection:
    def test_small_image_rejected(self, service):
        result = service.check_quality(_small_image())
        assert result["is_acceptable"] is False
        assert "Image resolution is too low" in result["issues"]


# ---------------------------------------------------------------------------
# Tests — Corrupt / unprocessable data
# ---------------------------------------------------------------------------

class TestCorruptData:
    def test_corrupt_bytes_rejected(self, service):
        result = service.check_quality(b"\x00\x01\x02not_an_image")
        assert result["is_acceptable"] is False
        assert "Image could not be processed" in result["issues"]

    def test_empty_bytes_rejected(self, service):
        result = service.check_quality(b"")
        assert result["is_acceptable"] is False
        assert "Image could not be processed" in result["issues"]


# ---------------------------------------------------------------------------
# Tests — Multiple issues reported together
# ---------------------------------------------------------------------------

class TestMultipleIssues:
    def test_small_and_dark_reports_both(self, service):
        """An image that is too small and too dark should list both issues."""
        img = np.full((50, 50, 3), 5, dtype=np.uint8)
        result = service.check_quality(_encode_jpeg(img))
        assert result["is_acceptable"] is False
        assert "Image resolution is too low" in result["issues"]
        assert "Image is too dark" in result["issues"]