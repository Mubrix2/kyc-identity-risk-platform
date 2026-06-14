# app/core/field_validator.py
"""
Cross-validate declared form fields against OCR-extracted document fields.
Output feeds directly into risk_scorer.py features.
"""
from rapidfuzz import fuzz


def cross_validate(declared: dict, extracted: dict) -> dict:
    """
    declared:  {"name": ..., "dob": ..., "id_number": ...} — from form
    extracted: same keys — from ocr_engine.process_document()
    """
    return {
        "name_match_score":   _fuzzy_score(declared.get("name"), extracted.get("name")),
        "dob_mismatch":       _differ(declared.get("dob"), extracted.get("dob")),
        "id_number_mismatch": _differ(declared.get("id_number"), extracted.get("id_number")),
        "fields_extracted":   sum(1 for v in extracted.values() if v),
    }


def _fuzzy_score(declared, extracted) -> float:
    """Missing extraction = 0.0 (worst case, conservative)."""
    if not declared or not extracted:
        return 0.0
    return round(fuzz.ratio(declared.upper(), extracted.upper()) / 100.0, 4)


def _differ(declared, extracted) -> int:
    """Missing extraction = mismatch (conservative)."""
    if not declared or not extracted:
        return 1
    return int(declared.strip().upper() != extracted.strip().upper())