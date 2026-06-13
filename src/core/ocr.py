"""OCR extraction using Tesseract."""
import pytesseract
from PIL import Image
from pathlib import Path


def extract_text(image_path: str | Path) -> str:
    """Extract text from an image file using Tesseract OCR."""
    img = Image.open(image_path)
    # Upscale small images for better OCR accuracy
    if img.width < 800:
        scale = 800 / img.width
        img = img.resize((int(img.width * scale), int(img.height * scale)), Image.LANCZOS)
    text = pytesseract.image_to_string(img, config="--psm 6")
    return text.strip()


def extract_text_from_bytes(data: bytes) -> str:
    """Extract text from raw image bytes."""
    import io
    img = Image.open(io.BytesIO(data))
    if img.width < 800:
        scale = 800 / img.width
        img = img.resize((int(img.width * scale), int(img.height * scale)), Image.LANCZOS)
    text = pytesseract.image_to_string(img, config="--psm 6")
    return text.strip()
