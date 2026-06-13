# app/db/models.py
"""SQLAlchemy 2.0 model for the KYC audit trail."""
from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class KYCAudit(Base):
    __tablename__ = "kyc_audit"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    record_id: Mapped[str] = mapped_column(String, index=True)
    declared_name: Mapped[str] = mapped_column(String)
    risk_probability: Mapped[float] = mapped_column(Float)
    decision: Mapped[str] = mapped_column(String, index=True)
    risk_tier: Mapped[str] = mapped_column(String)
    requires_edd: Mapped[bool] = mapped_column(Boolean, default=False)
    triggered_rules: Mapped[list] = mapped_column(JSON, default=list)
    top_reasons: Mapped[list] = mapped_column(JSON, default=list)
    processing_ms: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )