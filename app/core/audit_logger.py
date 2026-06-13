# app/core/audit_logger.py
"""Immutable PostgreSQL audit log — insert only, same principle as Project 1."""
import logging
from app.db.database import SessionLocal
from app.db.models import KYCAudit

logger = logging.getLogger(__name__)


def log_decision(assessment: dict) -> None:
    db = SessionLocal()
    try:
        db.add(KYCAudit(
            record_id=assessment["record_id"],
            declared_name=assessment["declared_name"],
            risk_probability=assessment["risk_probability"],
            decision=assessment["decision"],
            risk_tier=assessment["risk_tier"],
            requires_edd=assessment["requires_edd"],
            triggered_rules=assessment["triggered_rules"],
            top_reasons=assessment["top_reasons"],
            processing_ms=assessment["processing_ms"],
        ))
        db.commit()
    except Exception as e:
        logger.error(f"Audit log write failed: {e}")
        db.rollback()
    finally:
        db.close()