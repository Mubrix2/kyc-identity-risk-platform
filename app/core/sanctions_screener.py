# app/core/sanctions_screener.py
"""
Sanctions + PEP screening via fuzzy name matching.

Sanctions: REAL OFAC SDN data (7,469 individuals) — production-grade.
PEP: ILLUSTRATIVE list — real screening requires licensed databases
(Refinitiv World-Check, Dow Jones, ComplyAdvantage). Documented as
roadmap, same pattern as Project 1's AML scope decisions.

Singleton: both lists loaded once at startup. RapidFuzz's C++ backend
matches against thousands of entries in single-digit milliseconds.
"""
import logging
from pathlib import Path

import pandas as pd
from rapidfuzz import fuzz, process

from app.config import SANCTIONS_DATA_PATH, SANCTIONS_MATCH_THRESHOLD

logger = logging.getLogger(__name__)

PEP_DATA_PATH = Path("data/sanctions/illustrative_pep_list.csv")

_sanctions_names: list[str] = []
_sanctions_df: pd.DataFrame | None = None
_pep_names: list[str] = []
_pep_df: pd.DataFrame | None = None


def load_screening_lists() -> bool:
    global _sanctions_names, _sanctions_df, _pep_names, _pep_df

    if SANCTIONS_DATA_PATH.exists():
        _sanctions_df = pd.read_csv(SANCTIONS_DATA_PATH)
        _sanctions_names = _sanctions_df["name"].tolist()
        logger.info(f"Loaded {len(_sanctions_names):,} OFAC sanctions entries")
    else:
        logger.warning(f"Sanctions list not found: {SANCTIONS_DATA_PATH}")

    if PEP_DATA_PATH.exists():
        _pep_df = pd.read_csv(PEP_DATA_PATH)
        _pep_names = _pep_df["name"].tolist()
        logger.info(f"Loaded {len(_pep_names):,} illustrative PEP entries")

    return bool(_sanctions_names)


def screen_sanctions(name: str) -> dict:
    if not _sanctions_names:
        return {"is_match": False, "matched_name": None, "score": 0.0, "program": None}

    match = process.extractOne(name.upper(), _sanctions_names, scorer=fuzz.ratio)
    if not match:
        return {"is_match": False, "matched_name": None, "score": 0.0, "program": None}

    matched_name, score, idx = match
    is_match = score >= SANCTIONS_MATCH_THRESHOLD
    program = _sanctions_df.iloc[idx]["sanction_program"] if is_match else None

    return {
        "is_match": is_match,
        "matched_name": matched_name if is_match else None,
        "score": round(score / 100.0, 4),
        "program": program,
    }


def screen_pep(name: str) -> dict:
    """LIMITATION: illustrative list only — see module docstring."""
    if not _pep_names:
        return {"is_match": False, "matched_name": None, "score": 0.0, "category": None}

    match = process.extractOne(name.upper(), _pep_names, scorer=fuzz.ratio)
    if not match:
        return {"is_match": False, "matched_name": None, "score": 0.0, "category": None}

    matched_name, score, idx = match
    is_match = score >= SANCTIONS_MATCH_THRESHOLD
    category = _pep_df.iloc[idx]["category"] if is_match else None

    return {
        "is_match": is_match,
        "matched_name": matched_name if is_match else None,
        "score": round(score / 100.0, 4),
        "category": category,
    }


def screen_individual(name: str) -> dict:
    """Combined screening — single entry point for the orchestrator."""
    sanctions = screen_sanctions(name)
    pep = screen_pep(name)
    return {
        "sanctions": sanctions,
        "pep": pep,
        # EDD = Enhanced Due Diligence, standard AML/KYC term
        "requires_edd": sanctions["is_match"] or pep["is_match"],
    }