# tests/test_rules_engine.py
from app.core.rules_engine import apply_rules


def test_sanctions_match_forces_reject():
    screening = {"sanctions": {"is_match": True, "matched_name": "X"},
                  "pep": {"is_match": False, "matched_name": None}}
    result = apply_rules("APPROVE", screening)
    assert result["final_decision"] == "REJECT"


def test_pep_match_forces_review_minimum():
    screening = {"sanctions": {"is_match": False, "matched_name": None},
                  "pep": {"is_match": True, "matched_name": "Y"}}
    result = apply_rules("APPROVE", screening)
    assert result["final_decision"] == "REVIEW"


def test_clean_screening_keeps_ml_decision():
    screening = {"sanctions": {"is_match": False, "matched_name": None},
                  "pep": {"is_match": False, "matched_name": None}}
    result = apply_rules("APPROVE", screening)
    assert result["final_decision"] == "APPROVE"
    assert result["triggered_rules"] == []


def test_rules_never_de_escalate():
    """REJECT from ML stays REJECT even with clean screening."""
    screening = {"sanctions": {"is_match": False, "matched_name": None},
                  "pep": {"is_match": False, "matched_name": None}}
    result = apply_rules("REJECT", screening)
    assert result["final_decision"] == "REJECT"