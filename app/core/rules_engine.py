# app/core/rules_engine.py
"""
Rules engine — sanctions/PEP results override ML score.
Same asymmetric-escalation philosophy as Project 1: rules can only
push the decision toward REJECT, never toward APPROVE.
"""

DECISION_PRIORITY = ["APPROVE", "REVIEW", "REJECT"]


def apply_rules(ml_decision: str, screening: dict) -> dict:
    decision = ml_decision
    triggered = []

    def escalate(to: str, rule: str):
        nonlocal decision
        triggered.append(rule)
        if DECISION_PRIORITY.index(to) > DECISION_PRIORITY.index(decision):
            decision = to

    if screening["sanctions"]["is_match"]:
        escalate("REJECT", f"SANCTIONS_MATCH: {screening['sanctions']['matched_name']}")

    if screening["pep"]["is_match"]:
        escalate("REVIEW", f"PEP_MATCH: {screening['pep']['matched_name']} (EDD required)")

    return {"final_decision": decision, "triggered_rules": triggered}