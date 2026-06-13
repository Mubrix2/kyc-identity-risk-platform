# scripts/train_risk_model.py
"""
Train XGBoost risk classifier on the synthetic KYC dataset.

Uses scale_pos_weight instead of SMOTE (Project 1's choice).
At ~12.5% positive rate, the imbalance is moderate enough that
class weighting works well — SMOTE oversampling is more useful
at Project 1's 0.3% extreme imbalance. Demonstrates that the
right rebalancing technique depends on imbalance severity.

Usage: python scripts/train_risk_model.py
"""
import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.core.feature_engineer import FEATURE_COLUMNS

DATA_PATH   = Path("data/processed/kyc_onboarding_dataset.csv")
MODELS_DIR  = Path("app/models")
MODELS_DIR.mkdir(parents=True, exist_ok=True)
RANDOM_STATE = 42


def main():
    df = pd.read_csv(DATA_PATH)
    X = df[FEATURE_COLUMNS]
    y = df["is_high_risk"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y
    )

    scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()
    print(f"scale_pos_weight: {scale_pos_weight:.2f}")

    model = XGBClassifier(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.1,
        scale_pos_weight=scale_pos_weight,
        eval_metric="aucpr",
        early_stopping_rounds=30,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=30)

    probs = model.predict_proba(X_test)[:, 1]
    roc_auc = roc_auc_score(y_test, probs)

    # Report at configured thresholds (0.40 REVIEW, 0.75 REJECT)
    from app.config import RISK_REVIEW_THRESHOLD, RISK_REJECT_THRESHOLD
    decisions = np.where(
        probs >= RISK_REJECT_THRESHOLD, "REJECT",
        np.where(probs >= RISK_REVIEW_THRESHOLD, "REVIEW", "APPROVE"),
    )
    print(f"\nDecision distribution at configured thresholds:")
    print(pd.Series(decisions).value_counts())
    print(f"\nROC-AUC: {roc_auc:.4f}")
    print(classification_report(y_test, (probs >= RISK_REVIEW_THRESHOLD).astype(int)))

    joblib.dump(model, MODELS_DIR / "risk_model.pkl")
    json.dump(
        {"roc_auc": round(roc_auc, 4), "best_iteration": int(model.best_iteration),
         "features": FEATURE_COLUMNS},
        open(MODELS_DIR / "risk_model_metadata.json", "w"), indent=2,
    )
    print(f"\n✅ Saved risk_model.pkl")


if __name__ == "__main__":
    main()