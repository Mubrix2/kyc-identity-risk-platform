# app/core/explainer.py
"""SHAP TreeExplainer for KYC risk model — same pattern as Project 1."""
import logging
import pandas as pd
from app.core.feature_engineer import FEATURE_COLUMNS

logger = logging.getLogger(__name__)
_explainer = None

FEATURE_DESCRIPTIONS = {
    "name_match_score":          "Similarity between declared and document name",
    "document_quality_score":    "Quality of uploaded ID document image",
    "dob_mismatch":                "Date of birth mismatch between form and document",
    "sanctions_name_similarity":  "Similarity to a sanctions list entry",
    "is_pep_match":                "Politically Exposed Person match",
    "email_domain_age_days":       "Age of email domain",
    "phone_country_mismatch":      "Phone number country mismatch with IP",
    "ip_country_mismatch":          "IP address country mismatch with declared address",
    "device_fingerprint_reuse":     "Device used by other accounts",
    "onboarding_attempts_24h":       "Onboarding attempts in last 24 hours",
}


def initialise_explainer(model) -> None:
    global _explainer
    import shap
    _explainer = shap.TreeExplainer(model)
    logger.info("SHAP explainer initialised")


def explain_application(features: dict, top_n: int = 5) -> dict:
    if _explainer is None:
        return {"top_reasons": [], "explanation_available": False}

    df = pd.DataFrame([[features.get(c, 0) for c in FEATURE_COLUMNS]], columns=FEATURE_COLUMNS)
    shap_values = _explainer.shap_values(df)
    values = shap_values[1][0] if isinstance(shap_values, list) else shap_values[0]

    ranked = sorted(zip(FEATURE_COLUMNS, values), key=lambda x: abs(x[1]), reverse=True)[:top_n]
    top_reasons = [{
        "feature": f, "description": FEATURE_DESCRIPTIONS.get(f, f),
        "shap_value": round(float(v), 4),
        "direction": "increased_risk" if v > 0 else "decreased_risk",
    } for f, v in ranked]

    return {"top_reasons": top_reasons, "explanation_available": True}