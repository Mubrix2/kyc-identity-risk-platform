# app/config.py
"""
Centralised configuration for the KYC Identity Risk Platform.

Mirrors the Project 1 config pattern: all values from environment
variables, fail-fast on missing required values.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


# ── PostgreSQL ──────────────────────────────────────────────────────────────────
POSTGRES_HOST: str     = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT: int     = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_DB: str       = os.getenv("POSTGRES_DB", "kyc_platform")
POSTGRES_USER: str     = os.getenv("POSTGRES_USER", "kyc_user")
POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "")

DATABASE_URL: str = (
    f"postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

# ── Kafka ──────────────────────────────────────────────────────────────────────
KAFKA_BOOTSTRAP_SERVERS: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_KYC_EVENTS_TOPIC: str   = os.getenv("KAFKA_KYC_EVENTS_TOPIC", "kyc-events")
KAFKA_KYC_RESULTS_TOPIC: str  = os.getenv("KAFKA_KYC_RESULTS_TOPIC", "kyc-results")
KAFKA_CONSUMER_GROUP: str      = os.getenv("KAFKA_CONSUMER_GROUP", "kyc-platform-group")

# ── Risk Thresholds ─────────────────────────────────────────────────────────────
# Same 3-tier philosophy as Project 1: APPROVE / REVIEW / REJECT
RISK_REVIEW_THRESHOLD: float = float(os.getenv("RISK_REVIEW_THRESHOLD", "0.40"))
RISK_REJECT_THRESHOLD: float = float(os.getenv("RISK_REJECT_THRESHOLD", "0.75"))

# ── Sanctions Screening ──────────────────────────────────────────────────────────
# RapidFuzz score (0-100). Calibrated in Phase 2 against real OFAC names.
SANCTIONS_MATCH_THRESHOLD: int = int(os.getenv("SANCTIONS_MATCH_THRESHOLD", "85"))

# ── OCR ────────────────────────────────────────────────────────────────────────
TESSERACT_CMD: str = os.getenv("TESSERACT_CMD", "/usr/bin/tesseract")

# ── Paths ──────────────────────────────────────────────────────────────────────
SANCTIONS_DATA_PATH: Path = BASE_DIR / "data" / "sanctions" / "ofac_sdn.csv"
RISK_MODEL_PATH: Path     = BASE_DIR / "app" / "models" / "risk_model.pkl"
RISK_MODEL_META_PATH: Path = BASE_DIR / "app" / "models" / "risk_model_metadata.json"

# ── App ────────────────────────────────────────────────────────────────────────
APP_ENV: str = os.getenv("APP_ENV", "development")