# tests/test_api.py
import pytest
from app.core import sanctions_screener, risk_scorer
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
SAMPLE = Path("data/sample_ids/clean_match.png")

@pytest.fixture(scope="module", autouse=True)
def load_models():
    """
    TestClient(app) without `with` doesn't run lifespan(). Even `with
    TestClient(app)` would also try init_db()/Kafka via lifespan,
    coupling API tests to live Postgres/Kafka. Load only what scoring
    actually needs — keeps these tests fast and infra-independent.
    """
    sanctions_screener.load_screening_lists()
    risk_scorer.load_model()


client = TestClient(app)

def test_submit_clean_application():
    with open(SAMPLE, "rb") as f:
        resp = client.post("/api/v1/kyc/submit", data={
            "declared_name": "ADEKUNLE OKAFOR",
            "declared_dob": "14/03/1990",
            "declared_id_number": "12345678901",
            "declared_id_type": "NIN",
            "email_domain_age_days": "500",
            "phone_country_mismatch": "false",
            "ip_country_mismatch": "false",
            "device_fingerprint": "device-abc-123",
        }, files={"document": ("id.png", f, "image/png")})

    assert resp.status_code == 202
    body = resp.json()
    assert body["decision"] in ("APPROVE", "REVIEW", "REJECT")


def test_sanctions_match_triggers_reject():
    with open(SAMPLE, "rb") as f:
        resp = client.post("/api/v1/kyc/submit", data={
            "declared_name": "ABBAS, ABU",  # real OFAC entry
            "declared_dob": "14/03/1990",
            "declared_id_number": "12345678901",
            "declared_id_type": "NIN",
            "email_domain_age_days": "500",
            "phone_country_mismatch": "false",
            "ip_country_mismatch": "false",
            "device_fingerprint": "device-xyz-999",
        }, files={"document": ("id.png", f, "image/png")})

    assert resp.json()["decision"] == "REJECT"