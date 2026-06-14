# app/api/schemas.py
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field


class IDType(str, Enum):
    NIN = "NIN"
    BVN = "BVN"
    VOTERS_CARD = "VOTERS_CARD"
    DRIVERS_LICENSE = "DRIVERS_LICENSE"
    PASSPORT = "PASSPORT"


class KYCApplicationData(BaseModel):
    """
    Validated separately from the file upload — multipart/form-data
    can't use a single Pydantic body, so form fields are collected
    into a dict and validated through this model before orchestration.
    """
    model_config = ConfigDict(extra="forbid")

    declared_name: str         = Field(..., min_length=2, max_length=100)
    declared_dob: str           = Field(..., pattern=r"^\d{2}/\d{2}/\d{4}$")
    declared_id_number: str     = Field(..., min_length=6, max_length=15)
    declared_id_type: IDType
    email_domain_age_days: int  = Field(..., ge=0)
    phone_country_mismatch: bool = False
    ip_country_mismatch: bool    = False
    device_fingerprint: str      = Field(..., min_length=4, max_length=64)


class SubmitResponse(BaseModel):
    record_id: str
    status: str = "processed"
    decision: str
    risk_probability: float


class OverrideRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    record_id: str
    new_decision: str = Field(..., pattern="^(APPROVE|REVIEW|REJECT)$")
    reason: str        = Field(..., min_length=10)
    reviewer: str       = Field(..., min_length=2)