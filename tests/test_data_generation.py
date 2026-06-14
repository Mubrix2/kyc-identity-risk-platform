# tests/test_data_generation.py
"""
Schema and range validation for the generated synthetic dataset.
Run after generate_synthetic_kyc_data.py to confirm output integrity.
"""
import pandas as pd
import pytest

from pathlib import Path

DATA_PATH = Path("data/processed/kyc_onboarding_dataset.csv")


@pytest.fixture(scope="module")
def df():
    if not DATA_PATH.exists():
        pytest.skip("Run generate_synthetic_kyc_data.py first")
    return pd.read_csv(DATA_PATH)


def test_expected_columns_present(df):
    expected = {
        "record_id", "declared_name", "declared_id_type",
        "ocr_extracted_name", "name_match_score",
        "document_quality_score", "dob_mismatch",
        "sanctions_name_similarity", "is_pep_match",
        "email_domain_age_days", "phone_country_mismatch",
        "ip_country_mismatch", "device_fingerprint_reuse",
        "onboarding_attempts_24h", "is_high_risk",
    }
    assert expected.issubset(set(df.columns))


def test_no_missing_values(df):
    assert df.isnull().sum().sum() == 0


def test_score_ranges(df):
    assert df["name_match_score"].between(0, 1).all()
    assert df["document_quality_score"].between(0, 1).all()
    assert df["sanctions_name_similarity"].between(0, 1).all()


def test_binary_flags(df):
    for col in ["dob_mismatch", "is_pep_match", "phone_country_mismatch",
                 "ip_country_mismatch", "is_high_risk"]:
        assert set(df[col].unique()).issubset({0, 1})


def test_high_risk_rate_realistic(df):
    """KYC risk rate should be meaningfully higher than fraud rate (0.3%)."""
    rate = df["is_high_risk"].mean()
    assert 0.08 < rate < 0.18, f"High-risk rate {rate:.4f} outside expected range"


def test_record_ids_unique(df):
    assert df["record_id"].is_unique