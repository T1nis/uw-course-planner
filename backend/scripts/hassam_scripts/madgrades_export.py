"""
Export UW-Madison course catalogue and grade data from the MadGrades API.

Usage:
  MG_TOKEN=yourtoken python madgrades_export.py           # full dump
  python madgrades_export.py Spring 2025                  # filter to a single term
"""
#madgrades_export.py
import os
import sys
from pathlib import Path

import pandas as pd
import requests
from tqdm import tqdm

from term_utils import term_code

# — config & auth —
DATA_DIR = Path("d_data")
DATA_DIR.mkdir(exist_ok=True)

API_BASE = "https://api.madgrades.com"
TOKEN = os.getenv("MG_TOKEN")
if not TOKEN:
    print("ERROR: please set MG_TOKEN env var", file=sys.stderr)
    sys.exit(1)
HEADERS = {"Authorization": f"Token token={TOKEN}"}

# optional term filter
term_arg = sys.argv[1] if len(sys.argv) > 1 else None
TERM_FILTER = term_code(term_arg) if term_arg else None

def get_paginated(endpoint: str, *, per_page: int = 500):
    """Yield all pages from a MadGrades endpoint."""
    page = 1
    while True:
        resp = requests.get(
            f"{API_BASE}{endpoint}",
            params={"per_page": per_page, "page": page},
            headers=HEADERS,
            timeout=30,
        )
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        yield from batch
        if len(batch) < per_page:
            break
        page += 1

def main():
    # 1) download course catalogue
    print("Downloading course catalogue")
    courses = list(get_paginated("/courses"))
    pd.DataFrame(courses).to_csv(DATA_DIR / "madgrades_courses.csv", index=False)
    print(f"{len(courses):,} courses written to {DATA_DIR/'madgrades_courses.csv'}")

    # 2) download grade distributions
    print("Downloading grade distributions")
    grade_rows: list[dict[str, int | str]] = []
    for course in tqdm(courses, unit="course"):
        cid = course["id"]
        resp = requests.get(
            f"{API_BASE}/course_grades",
            params={"course_id": cid},
            headers=HEADERS,
            timeout=30,
        )
        resp.raise_for_status()
        for term in resp.json():
            tc = str(term["term"])
            if TERM_FILTER and tc != TERM_FILTER:
                continue
            row = {"course_id": cid}
            row.update(term)
            grade_rows.append(row)

    out_name = "madgrades_course_grades"
    if TERM_FILTER:
        out_name += f"_{TERM_FILTER}"
    out_path = DATA_DIR / f"{out_name}.csv"
    pd.DataFrame(grade_rows).to_csv(out_path, index=False)
    print(f"Completed – {len(grade_rows):,} grade rows written to {out_path}")

if __name__ == "__main__":
    main()