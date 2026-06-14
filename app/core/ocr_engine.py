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
from PIL import Image, UnidentifiedImageError

pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

FIELD_PATTERNS = {
    # Use [A-Z '-]+ (space, not \s) so matching stops at newlines
    "name": re.compile(
        r"(?:NAME|FULL NAME)\s*[:\-]?\s*([A-Z][A-Z '\-]+)",
        re.IGNORECASE
    ),
    "dob": re.compile(
        r"(?:DOB|DATE OF BIRTH)\s*[:\-]?\s*(\d{2})\D{0,2}(\d{2})\D{0,2}(\d{4})",
        re.IGNORECASE
    ),
    "id_number": re.compile(
        r"(?:NIN|ID NO|ID NUMBER)\s*[:\-]?\s*([A-Z0-9]{6,15})",
        re.IGNORECASE
    ),
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
            # Take first line only — belt-and-suspenders against multiline capture
            value = match.group(1).strip().upper()
            result[field] = value.split('\n')[0].strip()
    return result


def process_document(image) -> dict:
    try:
        raw_text = extract_text(image)
    except UnidentifiedImageError:
        # Unreadable upload → zero extraction confidence, all fields
        # mismatch downstream → feeds into risk score as a genuine signal,
        # not a crash.
        return {
            "raw_text": "",
            "extracted_fields": {"name": None, "dob": None, "id_number": None},
            "extraction_confidence": 0.0,
        }

    fields = extract_identity_fields(raw_text)
    confidence = round(sum(1 for v in fields.values() if v) / len(fields), 2)
    return {"raw_text": raw_text.strip(), "extracted_fields": fields, "extraction_confidence": confidence}