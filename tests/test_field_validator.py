# tests/test_field_validator.py
from app.core.field_validator import cross_validate


def test_exact_match():
    r = cross_validate(
        {"name": "ADEKUNLE OKAFOR", "dob": "14/03/1990", "id_number": "12345678901"},
        {"name": "ADEKUNLE OKAFOR", "dob": "14/03/1990", "id_number": "12345678901"},
    )
    assert r["name_match_score"] == 1.0
    assert r["dob_mismatch"] == 0
    assert r["id_number_mismatch"] == 0


def test_name_typo_high_similarity():
    r = cross_validate(
        {"name": "ADEKUNLE OKAFOR", "dob": "14/03/1990", "id_number": "12345678901"},
        {"name": "ADEKUNLE OKAFOR", "dob": "14/03/1990", "id_number": "12345678901"[:-1] + "0"},
    )
    assert r["name_match_score"] == 1.0
    assert r["id_number_mismatch"] == 1


def test_dob_mismatch():
    r = cross_validate(
        {"name": "X", "dob": "14/03/1990", "id_number": "1"},
        {"name": "X", "dob": "01/01/2000", "id_number": "1"},
    )
    assert r["dob_mismatch"] == 1


def test_missing_extraction_is_conservative():
    r = cross_validate(
        {"name": "X", "dob": "14/03/1990", "id_number": "1"},
        {"name": None, "dob": None, "id_number": None},
    )
    assert r["name_match_score"] == 0.0
    assert r["dob_mismatch"] == 1
    assert r["id_number_mismatch"] == 1