# app/core/risk_scorer.py
"""
XGBoost risk scoring — singleton, loaded once at startup.
3-tier decision: APPROVE / REVIEW / REJECT.
"""
import logging
import joblib
import pandas as pd

from app.config import RISK_MODEL_PATH, RISK_REVIEW_THRESHOLD, RISK_REJECT_THRESHOLD
from app.core.feature_engineer import FEATURE_COLUMNS

logger = logging.getLogger(__name__)
_model = None


def load_model() -> bool:
    global _model
    if not RISK_MODEL_PATH.exists():
        logger.warning(f"Risk model not found: {RISK_MODEL_PATH}")
        return False
    _model = joblib.load(RISK_MODEL_PATH)
    from app.core.explainer import initialise_explainer
    initialise_explainer(_model)
    logger.info("Risk model loaded")
    return True


def score_application(features: dict) -> dict:
    if _model is None:
        return {"risk_probability": 0.0, "decision": "REVIEW",
                "risk_tier": "UNKNOWN", "model_available": False}

    df = pd.DataFrame([[features.get(c, 0) for c in FEATURE_COLUMNS]], columns=FEATURE_COLUMNS)
    prob = float(_model.predict_proba(df)[0][1])

    if prob >= RISK_REJECT_THRESHOLD:
        decision, tier = "REJECT", "HIGH"
    elif prob >= RISK_REVIEW_THRESHOLD:
        decision, tier = "REVIEW", "MEDIUM"
    else:
        decision, tier = "APPROVE", "LOW"

    return {"risk_probability": round(prob, 6), "decision": decision,
            "risk_tier": tier, "model_available": True}