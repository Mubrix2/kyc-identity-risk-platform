# tests/test_ocr_engine.py
from pathlib import Path
import pytest
from app.core.ocr_engine import process_document

SAMPLES_DIR = Path("data/sample_ids")


@pytest.mark.skipif(not SAMPLES_DIR.exists(), reason="Run generate_sample_id_images.py first")
def test_clean_image_extracts_all_fields():
    result = process_document(SAMPLES_DIR / "clean_match.png")
    fields = result["extracted_fields"]
    assert "OKAFOR" in (fields["name"] or "")
    assert fields["dob"] == "14/03/1990"
    assert result["extraction_confidence"] >= 0.6


@pytest.mark.skipif(not SAMPLES_DIR.exists(), reason="Run generate_sample_id_images.py first")
def test_low_quality_image_still_processes():
    result = process_document(SAMPLES_DIR / "low_quality.png")
    assert "raw_text" in result
    assert 0 <= result["extraction_confidence"] <= 1


pytest.mark.skipif(not SAMPLES_DIR.exists(), reason="Run generate_sample_id_images.py first")
def test_invalid_image_returns_zero_confidence():
    result = process_document(b"not an image")
    assert result["extraction_confidence"] == 0.0
    assert result["extracted_fields"]["name"] is None