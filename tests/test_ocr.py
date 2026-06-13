"""OCR tests — requires Tesseract installed."""
import io
import pytest
from PIL import Image, ImageDraw, ImageFont
from src.core.ocr import extract_text_from_bytes


def _make_image(text: str) -> bytes:
    img = Image.new("RGB", (400, 100), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((10, 30), text, fill=(0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_extract_text_basic():
    data = _make_image("Hello World")
    result = extract_text_from_bytes(data)
    assert "Hello" in result or "World" in result


def test_extract_empty_image():
    img = Image.new("RGB", (200, 50), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    result = extract_text_from_bytes(buf.getvalue())
    assert isinstance(result, str)
