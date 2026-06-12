# scripts/generate_synthetic_kyc_data.py
"""
Generate a synthetic onboarding dataset for risk model training.

Why synthetic — same reasoning as PaySim in Project 1:
  No public dataset exists for "KYC onboarding risk" — this is
  proprietary data every fintech guards closely. We generate
  realistic synthetic records with INJECTED correlations based on
  documented real-world risk patterns:

  - Low document quality + name mismatch → higher risk
  - Multiple onboarding attempts in 24h from same device → higher risk
  - Name similarity to a sanctions entry → higher risk
  - New email domain + phone/IP country mismatch → higher risk

The sanctions_name_similarity feature is computed against the REAL
OFAC data downloaded in Step 2.2 — this is the one feature in this
synthetic dataset with a genuine real-world signal behind it.

Usage:
    python scripts/generate_synthetic_kyc_data.py --n 50000
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from rapidfuzz import fuzz, process

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

TARGET_HIGH_RISK_RATE = 0.125  # ~12.5% — KYC flags are more common than confirmed fraud


SANCTIONS_PATH = Path("data/sanctions/ofac_sdn.csv")
OUTPUT_PATH    = Path("data/processed/kyc_onboarding_dataset.csv")

RANDOM_STATE = 42

FIRST_NAMES = [
    "Adekunle", "Chioma", "Ibrahim", "Ngozi", "Tunde", "Amaka",
    "Yusuf", "Funke", "Emeka", "Bukola", "Hassan", "Temitope",
    "Olumide", "Zainab", "Chinedu", "Aisha", "Babatunde", "Grace",
]
LAST_NAMES = [
    "Okafor", "Mohammed", "Adeyemi", "Eze", "Bello", "Okonkwo",
    "Abubakar", "Adewale", "Nwosu", "Yakubu", "Olawale", "Suleiman",
]
ID_TYPES = ["NIN", "BVN", "VOTERS_CARD", "DRIVERS_LICENSE", "PASSPORT"]


def compute_risk_signal(r: dict) -> float:
    return (
        (1 - r["document_quality_score"]) * 0.20
        + (1 - r["name_match_score"]) * 0.20
        + r["dob_mismatch"] * 0.15
        + r["sanctions_name_similarity"] * 0.25
        + min(r["device_fingerprint_reuse"] / 5, 1) * 0.10
        + min(r["onboarding_attempts_24h"] / 5, 1) * 0.10
    )


def load_sanctions_names() -> list[str]:
    df = pd.read_csv(SANCTIONS_PATH)
    return df["name"].tolist()


def inject_ocr_noise(name: str, noise_prob: float) -> str:
    """Simulate OCR errors — character substitution, dropped letters."""
    if np.random.random() > noise_prob:
        return name  # no noise — extraction matched perfectly

    chars = list(name)
    if len(chars) < 3:
        return name

    op = np.random.choice(["substitute", "drop", "swap"])
    idx = np.random.randint(0, len(chars) - 1)

    if op == "substitute":
        chars[idx] = np.random.choice(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
    elif op == "drop":
        chars.pop(idx)
    elif op == "swap":
        chars[idx], chars[idx + 1] = chars[idx + 1], chars[idx]

    return "".join(chars)


def generate_record(idx: int, sanctions_names: list[str]) -> dict:
    np.random.seed(RANDOM_STATE + idx)

    first = np.random.choice(FIRST_NAMES)
    last  = np.random.choice(LAST_NAMES)
    declared_name = f"{first} {last}".upper()

    # ── Document quality ────────────────────────────────────────────
    # Most uploads are decent quality; some are poor (blurry photos)
    document_quality_score = round(np.random.beta(5, 1.5), 4)  # skewed high

    # ── OCR noise increases with poor document quality ──────────────
    noise_prob = max(0.0, (1 - document_quality_score) * 0.6)
    ocr_extracted_name = inject_ocr_noise(declared_name, noise_prob)
    name_match_score = fuzz.ratio(declared_name, ocr_extracted_name) / 100.0

    # ── DOB mismatch — rarer, but a strong signal when present ────────
    dob_mismatch = int(np.random.random() < 0.03)

    # ── Sanctions similarity — computed against REAL OFAC names ──────
    # 1.5% of records are deliberately drawn close to a sanctions name
    # to create positive examples for the model to learn from
    if np.random.random() < 0.015:
        base_name = np.random.choice(sanctions_names)
        # mutate slightly — common names that partially overlap
        test_name = inject_ocr_noise(base_name, 0.3)
    else:
        test_name = declared_name

    match = process.extractOne(test_name, sanctions_names, scorer=fuzz.ratio)
    sanctions_name_similarity = round(match[1] / 100.0, 4) if match else 0.0
    is_pep_match = int(sanctions_name_similarity > 0.85)

    # ── Behavioural / device signals ──────────────────────────────────
    email_domain_age_days     = int(np.random.exponential(400))
    phone_country_mismatch    = int(np.random.random() < 0.05)
    ip_country_mismatch       = int(np.random.random() < 0.04)
    device_fingerprint_reuse  = np.random.poisson(0.3)
    onboarding_attempts_24h   = np.random.poisson(0.5) + 1

    # ── Composite risk label ────────────────────────────────────────
    # Risk increases with: poor docs, name mismatch, sanctions
    # similarity, device reuse, velocity, mismatches
    risk_signal = (
        (1 - document_quality_score) * 0.20
        + (1 - name_match_score) * 0.20
        + dob_mismatch * 0.15
        + sanctions_name_similarity * 0.25
        + min(device_fingerprint_reuse / 5, 1) * 0.10
        + min(onboarding_attempts_24h / 5, 1) * 0.10
    )
    is_high_risk = int(risk_signal + np.random.normal(0, 0.05) > 0.45)

    record = {
        "record_id": f"KYC-{idx:07d}",
        "declared_name": declared_name,
        "declared_id_type": np.random.choice(ID_TYPES),
        "ocr_extracted_name": ocr_extracted_name,
        "name_match_score": name_match_score,
        "document_quality_score": document_quality_score,
        "dob_mismatch": dob_mismatch,
        "sanctions_name_similarity": sanctions_name_similarity,
        "is_pep_match": is_pep_match,
        "email_domain_age_days": email_domain_age_days,
        "phone_country_mismatch": phone_country_mismatch,
        "ip_country_mismatch": ip_country_mismatch,
        "device_fingerprint_reuse": device_fingerprint_reuse,
        "onboarding_attempts_24h": onboarding_attempts_24h,
    }
    record["risk_signal"] = compute_risk_signal(record)
    return record

def main(n: int):
    sanctions_names = load_sanctions_names()
    records = [generate_record(i, sanctions_names) for i in range(n)]
    df = pd.DataFrame(records)

    # Percentile-based threshold — guarantees ~12.5% regardless of
    # the formula's absolute scale. Add noise so the cutoff isn't a
    # hard cliff (real-world labels are never perfectly clean).
    threshold = df["risk_signal"].quantile(1 - TARGET_HIGH_RISK_RATE)
    noise = np.random.normal(0, 0.03, size=len(df))
    df["is_high_risk"] = ((df["risk_signal"] + noise) > threshold).astype(int)
    df = df.drop(columns=["risk_signal"])

    df.to_csv(OUTPUT_PATH, index=False)
    print(f"✅ {len(df):,} records, high-risk rate: {df['is_high_risk'].mean():.4f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=50_000)
    args = parser.parse_args()
    main(args.n)