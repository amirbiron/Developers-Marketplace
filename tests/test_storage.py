"""טסטים לוולידציית תמונת פרופיל (בלי רשת)."""

from __future__ import annotations

import pytest

from app.services.storage import AvatarUploadError, detect_image_type, validate_avatar

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 100
WEBP = b"RIFF" + b"\x00\x00\x00\x00" + b"WEBP" + b"\x00" * 100
GIF = b"GIF89a" + b"\x00" * 100


class TestDetect:
    def test_png(self):
        assert detect_image_type(PNG) == "image/png"

    def test_jpeg(self):
        assert detect_image_type(JPEG) == "image/jpeg"

    def test_webp(self):
        assert detect_image_type(WEBP) == "image/webp"

    def test_gif_not_supported(self):
        assert detect_image_type(GIF) is None

    def test_garbage(self):
        assert detect_image_type(b"not an image") is None

    def test_empty(self):
        assert detect_image_type(b"") is None


class TestValidate:
    def test_valid_png(self):
        content_type, ext = validate_avatar(PNG, max_bytes=1024)
        assert content_type == "image/png"
        assert ext == ".png"

    def test_empty_rejected(self):
        with pytest.raises(AvatarUploadError):
            validate_avatar(b"", max_bytes=1024)

    def test_oversized_rejected(self):
        big = PNG + b"\x00" * 2048
        with pytest.raises(AvatarUploadError):
            validate_avatar(big, max_bytes=1024)

    def test_unsupported_type_rejected(self):
        # לא סומכים על content-type — GIF נחסם לפי ה-bytes
        with pytest.raises(AvatarUploadError):
            validate_avatar(GIF, max_bytes=1024)
