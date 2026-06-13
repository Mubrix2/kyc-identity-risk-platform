# app/services/kyc_orchestrator.py
"""
Full KYC pipeline orchestration — equivalent to Project 1's
detection_service.assess_transaction().

7-step pipeline:
  OCR → field validation → sanctions/PEP screening → velocity →
  feature vector → risk scoring → rules engine → SHAP → audit log
"""
import time
from datetime import datetime, timezone

from app.core import onboarding_velocity, rules_engine, sanctions_screener
from app.core.audit_logger import log_decision
from app.core.explainer import explain_application
from app.core.feature_engineer import build_feature_vector
from app.core.field_validator import cross_validate
from app.core.ocr_engine import process_document
from app.core.risk_scorer import score_application


def assess_application(record_id: str, application: dict, document_image: bytes) -> dict:
    """
    application: {declared_name, declared_dob, declared_id_number,
                   email_domain_age_days, phone_country_mismatch,
                   ip_country_mismatch, device_fingerprint}
    document_image: raw bytes of uploaded ID document
    """
    start = time.perf_counter()

    # 1. OCR
    ocr_result = process_document(document_image)
    extracted = ocr_result["extracted_fields"]

    # 2. Field cross-validation
    declared = {
        "name": application["declared_name"],
        "dob": application["declared_dob"],
        "id_number": application["declared_id_number"],
    }
    validation = cross_validate(declared, extracted)

    # 3. Sanctions/PEP screening
    screening = sanctions_screener.screen_individual(application["declared_name"])

    # 4. Onboarding velocity
    device = application["device_fingerprint"]
    onboarding_velocity.record_attempt(device, record_id)
    velocity = onboarding_velocity.get_velocity_features(device)

    # 5. Feature vector
    behavioral = {
        "document_quality_score": ocr_result["extraction_confidence"],
        "email_domain_age_days": application["email_domain_age_days"],
        "phone_country_mismatch": application["phone_country_mismatch"],
        "ip_country_mismatch": application["ip_country_mismatch"],
        **velocity,
    }
    features = build_feature_vector(validation, screening, behavioral)

    # 6. Risk scoring
    risk_result = score_application(features)

    # 7. Rules engine — sanctions/PEP can only escalate
    rules_result = rules_engine.apply_rules(risk_result["decision"], screening)
    final_decision = rules_result["final_decision"]

    # 8. SHAP
    explanation = explain_application(features)

    elapsed = (time.perf_counter() - start) * 1000

    assessment = {
        "record_id": record_id,
        "declared_name": application["declared_name"],
        "risk_probability": risk_result["risk_probability"],
        "decision": final_decision,
        "risk_tier": risk_result["risk_tier"],
        "requires_edd": screening["requires_edd"],
        "triggered_rules": rules_result["triggered_rules"],
        "field_validation": validation,
        "screening": screening,
        "top_reasons": explanation["top_reasons"],
        "processing_ms": round(elapsed, 2),
        "scored_at": datetime.now(timezone.utc).isoformat(),
    }

    log_decision(assessment)
    return assessment