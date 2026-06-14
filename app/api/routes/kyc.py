# app/api/routes/kyc.py
"""
KYC application endpoints.

POST /submit: multipart (form fields + ID document image) →
  synchronous orchestration → store result → publish to Kafka → return.

GET /cases, /cases/{id}, /stats: dashboard polling (same pattern as
Project 1's /recent, /results/{id}, /stats).

POST /override: manual reviewer decision. Logs a NEW audit row
(immutability preserved — overrides are events, not edits) and
updates the in-memory result for the dashboard.
"""
import uuid
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from pydantic import ValidationError

from app.api.schemas import IDType, KYCApplicationData, OverrideRequest, SubmitResponse
from app.core.audit_logger import log_decision
from app.services.kyc_orchestrator import assess_application
from app.streaming.consumer import get_all_results, get_result, store_result
from app.streaming.producer import publish_assessment

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/kyc", tags=["kyc"])


@router.post("/submit", response_model=SubmitResponse, status_code=status.HTTP_202_ACCEPTED)
async def submit_application(
    declared_name: str = Form(...),
    declared_dob: str = Form(...),
    declared_id_number: str = Form(...),
    declared_id_type: IDType = Form(...),
    email_domain_age_days: int = Form(...),
    phone_country_mismatch: bool = Form(False),
    ip_country_mismatch: bool = Form(False),
    device_fingerprint: str = Form(...),
    document: UploadFile = File(...),
):
    try:
        data = KYCApplicationData(
            declared_name=declared_name, declared_dob=declared_dob,
            declared_id_number=declared_id_number, declared_id_type=declared_id_type,
            email_domain_age_days=email_domain_age_days,
            phone_country_mismatch=phone_country_mismatch,
            ip_country_mismatch=ip_country_mismatch,
            device_fingerprint=device_fingerprint,
        )
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())

    image_bytes = await document.read()
    record_id = f"KYC-{uuid.uuid4().hex[:10].upper()}"

    assessment = assess_application(record_id, data.model_dump(mode="json"), image_bytes)
    store_result(record_id, assessment)
    publish_assessment(assessment)

    return SubmitResponse(
        record_id=record_id, decision=assessment["decision"],
        risk_probability=assessment["risk_probability"],
    )


@router.get("/cases/{record_id}")
async def get_case(record_id: str):
    result = get_result(record_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"{record_id} not found")
    return result


@router.get("/cases")
async def list_cases(limit: int = 100):
    results = get_all_results()[:limit]
    return {"cases": results, "total": len(results)}


@router.get("/stats")
async def stats():
    all_results = get_all_results()
    total = len(all_results)
    approve = sum(1 for r in all_results if r["decision"] == "APPROVE")
    review  = sum(1 for r in all_results if r["decision"] == "REVIEW")
    reject  = sum(1 for r in all_results if r["decision"] == "REJECT")
    edd     = sum(1 for r in all_results if r.get("requires_edd"))

    avg_ms = round(sum(r.get("processing_ms", 0) for r in all_results) / total, 2) if total else 0

    return {
        "total": total, "approve": approve, "review": review, "reject": reject,
        "requires_edd": edd, "avg_processing_ms": avg_ms,
    }


@router.post("/override")
async def override_decision(req: OverrideRequest):
    """Reviewer override — logs a NEW audit event, updates live result."""
    existing = get_result(req.record_id)
    if existing is None:
        raise HTTPException(status_code=404, detail=f"{req.record_id} not found")

    override_event = {
        **existing,
        "decision": req.new_decision,
        "triggered_rules": existing.get("triggered_rules", []) + [
            f"MANUAL_OVERRIDE by {req.reviewer}: {req.reason}"
        ],
        "scored_at": datetime.now(timezone.utc).isoformat(),
    }

    log_decision(override_event)   # new audit row — immutability preserved
    store_result(req.record_id, override_event)

    logger.info(f"Override {req.record_id}: {existing['decision']} → {req.new_decision} by {req.reviewer}")
    return {"record_id": req.record_id, "decision": req.new_decision, "status": "overridden"}