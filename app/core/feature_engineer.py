# app/core/feature_engineer.py
"""
Assembles the 10-feature risk vector from pipeline stage outputs.
Same column order must be used at training and inference time.
"""

FEATURE_COLUMNS = [
    "name_match_score",
    "document_quality_score",
    "dob_mismatch",
    "sanctions_name_similarity",
    "is_pep_match",
    "email_domain_age_days",
    "phone_country_mismatch",
    "ip_country_mismatch",
    "device_fingerprint_reuse",
    "onboarding_attempts_24h",
]


def build_feature_vector(field_validation: dict, screening: dict, behavioral: dict) -> dict:
    """
    field_validation: output of field_validator.cross_validate()
    screening:        output of sanctions_screener.screen_individual()
    behavioral:       {document_quality_score, email_domain_age_days,
                       phone_country_mismatch, ip_country_mismatch,
                       device_fingerprint_reuse, onboarding_attempts_24h}
    """
    return {
        "name_match_score":          field_validation["name_match_score"],
        "document_quality_score":    behavioral["document_quality_score"],
        "dob_mismatch":               field_validation["dob_mismatch"],
        "sanctions_name_similarity":  screening["sanctions"]["score"],
        "is_pep_match":                int(screening["pep"]["is_match"]),
        "email_domain_age_days":       behavioral["email_domain_age_days"],
        "phone_country_mismatch":      behavioral["phone_country_mismatch"],
        "ip_country_mismatch":          behavioral["ip_country_mismatch"],
        "device_fingerprint_reuse":     behavioral["device_fingerprint_reuse"],
        "onboarding_attempts_24h":       behavioral["onboarding_attempts_24h"],
    }