# scripts/download_sanctions_data.py
"""
Download the OFAC Specially Designated Nationals (SDN) list.

This is REAL data — the actual sanctions list used by banks and
fintechs globally for sanctions screening. Published by the US
Treasury's Office of Foreign Assets Control, freely available,
updated regularly.

Source: https://sanctionslist.ofac.treas.gov/Home/SdnList
Direct CSV download: https://www.treasury.gov/ofac/downloads/sdn.csv

Usage:
    python scripts/download_sanctions_data.py
"""
import sys
from pathlib import Path

import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

SDN_URL = "https://www.treasury.gov/ofac/downloads/sdn.csv"
OUTPUT_PATH = Path("data/sanctions/ofac_sdn.csv")

# The raw SDN CSV has no header row — columns documented by OFAC
SDN_COLUMNS = [
    "ent_num", "sdn_name", "sdn_type", "program",
    "title", "call_sign", "vess_type", "tonnage",
    "grt", "vess_flag", "vess_owner", "remarks",
]


def main():
    print("Downloading OFAC SDN sanctions list...")
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    resp = requests.get(SDN_URL, timeout=30)
    resp.raise_for_status()

    raw_path = OUTPUT_PATH.parent / "_sdn_raw.csv"
    raw_path.write_bytes(resp.content)

    # OFAC's CSV has no header and inconsistent quoting — load carefully
    df = pd.read_csv(
        raw_path,
        names=SDN_COLUMNS,
        header=None,
        encoding="latin-1",
        on_bad_lines="skip",
    )

    # Keep only fields relevant to name screening
    # sdn_type: 'individual', 'entity', 'vessel', 'aircraft'
    # We screen against individuals primarily — KYC is identity verification
    individuals = df[df["sdn_type"].str.lower() == "individual"].copy()

    screening_df = individuals[["ent_num", "sdn_name", "program"]].copy()
    screening_df.columns = ["entity_id", "name", "sanction_program"]
    screening_df["name"] = screening_df["name"].str.strip().str.upper()
    screening_df = screening_df.dropna(subset=["name"])
    screening_df = screening_df.drop_duplicates(subset=["name"])

    screening_df.to_csv(OUTPUT_PATH, index=False)
    raw_path.unlink()  # cleanup intermediate file

    print(f"✅ Saved {len(screening_df):,} individual sanctions entries")
    print(f"   → {OUTPUT_PATH}")
    print(f"\nSample entries:")
    print(screening_df.head(5).to_string(index=False))


if __name__ == "__main__":
    main()