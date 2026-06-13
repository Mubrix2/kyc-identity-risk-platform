# tests/test_risk_scorer.py
from app.core import risk_scorer
from app.core.feature_engineer import FEATURE_COLUMNS


def test_low_risk_features_approve():
    risk_scorer.load_model()
    features = {c: 0 for c in FEATURE_COLUMNS}
    features["name_match_score"] = 1.0
    features["document_quality_score"] = 0.95
    result = risk_scorer.score_application(features)
    assert result["decision"] in ("APPROVE", "REVIEW")  # model-dependent


def test_high_sanctions_similarity_increases_risk():
    risk_scorer.load_model()
    low = {c: 0 for c in FEATURE_COLUMNS}
    low["name_match_score"] = 1.0
    low["document_quality_score"] = 0.95

    high = dict(low)
    high["sanctions_name_similarity"] = 1.0
    high["is_pep_match"] = 1

    r_low  = risk_scorer.score_application(low)
    r_high = risk_scorer.score_application(high)
    assert r_high["risk_probability"] > r_low["risk_probability"]