# kyc-identity-risk-platform

# KYC & Identity Risk Intelligence Platform

The companion platform to [Real-Time Fraud Detection Pipeline](#).
Where Project 1 asks "is this transaction fraudulent?", this platform
asks "is this person who they claim to be, and how risky are they to
onboard?" — covering the customer risk lifecycle from application
through transaction monitoring.

## The Pipeline
Onboarding form submitted

↓

Kafka Stream (kyc-events)

↓

OCR Extraction (Tesseract) → declared vs extracted field comparison

↓

Sanctions/PEP Screening (RapidFuzz vs OFAC SDN list)

↓

Risk Feature Engineering

↓

XGBoost Risk Score + SHAP Explanation

↓

Rules Engine (sanctions match = hard REJECT override)

↓

3-Tier Decision: APPROVE / REVIEW / REJECT

↓

PostgreSQL Audit Log

↓

React Compliance Reviewer Dashboard

## Status

🚧 Under active development. See [companion fraud detection project](#)
for the completed sibling platform sharing this architecture.