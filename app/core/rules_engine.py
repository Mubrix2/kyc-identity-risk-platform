# app/core/rules_engine.py
"""
Rules engine — sanctions/PEP results override ML score.
Same asymmetric-escalation philosophy as Project 1: rules can only
push the decision toward REJECT, never toward APPROVE.
"""

DECISION_PRIORITY = ["APPROVE", "REVIEW", "REJECT"]


def apply_rules(
    ml_decision: str,
    screening: dict,
    face_result=None,
    field_validation: dict | None = None,  
) -> dict:
    decision  = ml_decision
    triggered = []

    def escalate(to: str, rule: str):
        nonlocal decision
        triggered.append(rule)
        if DECISION_PRIORITY.index(to) > DECISION_PRIORITY.index(decision):
            decision = to

    # ── Existing rules ────────────────────────────────────────────────
    if screening["sanctions"]["is_match"]:
        escalate("REJECT", f"SANCTIONS_MATCH: {screening['sanctions']['matched_name']}")

    if screening["pep"]["is_match"]:
        escalate("REVIEW", f"PEP_MATCH: {screening['pep']['matched_name']} (EDD required)")

    if face_result and face_result.get("face_match_score") is not None:
        if face_result["is_match"] is False:
            escalate("REVIEW", f"FACE_MISMATCH: score={face_result['face_match_score']:.2f}")

    # ── New: document field mismatch rules ────────────────────────────
    if field_validation:
        name_score = field_validation.get("name_match_score", 1.0)
        dob_mismatch = field_validation.get("dob_mismatch", 0)
        id_mismatch = field_validation.get("id_number_mismatch", 0)

        # Significant name difference between declared form and document
        if name_score < 0.50:
            escalate(
                "REVIEW",
                f"NAME_MISMATCH: declared name matches document at "
                f"{name_score*100:.0f}% — manual verification required"
            )

        # DOB on document doesn't match declared DOB
        if dob_mismatch:
            escalate("REVIEW", "DOB_MISMATCH: date of birth differs between form and document")

        # ID number on document doesn't match declared ID number
        if id_mismatch:
            escalate(
                "REVIEW",
                "ID_NUMBER_MISMATCH: ID number differs between form and document"
            )

    return {"final_decision": decision, "triggered_rules": triggered}