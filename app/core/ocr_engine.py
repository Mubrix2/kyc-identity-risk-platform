# app/core/ocr_engine.py
"""
OCR extraction via Tesseract.

Why Tesseract over EasyOCR/PaddleOCR: no PyTorch/ONNX dependency —
fits free-tier deployment RAM limits. Trade-off: lower accuracy on
poor-quality images, acceptable for portfolio scope.
"""
import re
from io import BytesIO
from pathlib import Path
from typing import Union

import pytesseract
from PIL import Image

from app.config import TESSERACT_CMD

pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

FIELD_PATTERNS = {
    "name": re.compile(r"(?:NAME|FULL NAME)\s*[:\-]?\s*([A-Z][A-Z\s'\-]+)", re.IGNORECASE),
    # Three digit groups with 0-2 non-digit chars between them — tolerates
    # "/" being read as space, "-", "|", "l", "1", or dropped entirely.
    # Real scanned IDs have the same OCR noise around separators.
    "dob": re.compile(r"(?:DOB|DATE OF BIRTH)\s*[:\-]?\s*(\d{2})\D{0,2}(\d{2})\D{0,2}(\d{4})", re.IGNORECASE),
    "id_number": re.compile(r"(?:NIN|ID NO|ID NUMBER)\s*[:\-]?\s*([A-Z0-9]{6,15})", re.IGNORECASE),
}


def extract_text(image: Union[str, Path, bytes]) -> str:
    """Run Tesseract OCR. Accepts file path or raw bytes (upload)."""
    img = Image.open(image if isinstance(image, (str, Path)) else BytesIO(image))
    img = img.convert("L")  # grayscale improves accuracy
    return pytesseract.image_to_string(img)


def extract_identity_fields(raw_text: str) -> dict:
    """Parse OCR text into name/dob/id_number. Missing fields = None."""
    result = {}
    for field, pattern in FIELD_PATTERNS.items():
        match = pattern.search(raw_text)
        if not match:
            result[field] = None
        elif field == "dob":
            result[field] = f"{match.group(1)}/{match.group(2)}/{match.group(3)}"
        else:
            result[field] = match.group(1).strip().upper()
    return result


def process_document(image: Union[str, Path, bytes]) -> dict:
    """Full pipeline: image → raw text + structured fields + confidence."""
    raw_text = extract_text(image)
    fields = extract_identity_fields(raw_text)
    confidence = round(sum(1 for v in fields.values() if v) / len(fields), 2)
    return {
        "raw_text": raw_text.strip(),
        "extracted_fields": fields,
        "extraction_confidence": confidence,
    }