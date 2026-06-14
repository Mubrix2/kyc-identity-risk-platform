# scripts/generate_illustrative_pep_list.py
"""
ILLUSTRATIVE PEP list — fictional names, demonstrates the screening
pattern only. Production requires licensed PEP databases.

Usage: python scripts/generate_illustrative_pep_list.py
"""
from pathlib import Path
import pandas as pd

OUTPUT_PATH = Path("data/sanctions/illustrative_pep_list.csv")

# All fictional — FATF-standard PEP categories for demo coverage
ILLUSTRATIVE_PEPS = [
    ("ADEBAYO JOHNSON",  "Head of State (Former)"),
    ("FATIMA YUSUF",     "Senior Minister"),
    ("CHUKWUDI OBI",     "Senior Judiciary"),
    ("MUSA IBRAHIM",     "Senior Military Officer"),
    ("NGOZI ADEYEMI",    "State-Owned Enterprise Executive"),
    ("TUNDE BAKARE",     "Senior Minister"),
    ("AISHA MOHAMMED",   "Senior Judiciary"),
    ("EMEKA NWANKWO",    "Head of State (Former)"),
    ("HALIMA ABUBAKAR",  "Senior Military Officer"),
    ("OLUSEGUN ADESOLA", "State-Owned Enterprise Executive"),
]

if __name__ == "__main__":
    df = pd.DataFrame(ILLUSTRATIVE_PEPS, columns=["name", "category"])
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"✅ {len(df)} illustrative PEP entries → {OUTPUT_PATH}")
    print("NOTE: Fictional data — demonstrates pattern only.")