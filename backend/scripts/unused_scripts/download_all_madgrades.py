import os
import sys
import json
from pathlib import Path
from typing import Any, Dict, List

import requests
from tqdm import tqdm
import pandas as pd

API_BASE = "https://api.madgrades.com/v1"
TOKEN    = os.getenv("MG_TOKEN")
if not TOKEN:
    print("ERROR: set MG_TOKEN environment variable", file=sys.stderr)
    sys.exit(1)

HEADERS = {"Authorization": f"Token token={TOKEN}"}
DATA_DIR = Path("d_data")
DATA_DIR.mkdir(exist_ok=True)

def paginate(endpoint: str, params: Dict[str, Any] = None, per_page: int = 500) -> List[Dict[str, Any]]:
    """
    GET all pages from a paginated v1 endpoint.
    Only stops when an empty page comes back.
    """
    items: List[Dict[str, Any]] = []
    page = 1
    p = (params.copy() if params else {})
    while True:
        p.update({"page": page, "per_page": per_page})
        r = requests.get(f"{API_BASE}{endpoint}", headers=HEADERS, params=p, timeout=30)
        r.raise_for_status()
        data = r.json()

        # pull out the list under "results" or treat as plain list
        if isinstance(data, dict) and "results" in data:
            records = data["results"]
        elif isinstance(data, list):
            records = data
        else:
            raise RuntimeError(f"Unexpected format for {endpoint}: {type(data)}")

        if not records:
            break

        items.extend(records)
        page += 1

    return items

def main():
    # 1) courses
    print("Fetching courses…")
    courses = paginate("/courses")
    pd.DataFrame(courses).to_csv(DATA_DIR / "madgrades_courses.csv", index=False)
    print(f"→ {len(courses)} courses saved to d_data/madgrades_courses.csv")

    # 2) subjects
    print("Fetching subjects…")
    subjects = paginate("/subjects")
    pd.DataFrame(subjects).to_csv(DATA_DIR / "madgrades_subjects.csv", index=False)
    print(f"→ {len(subjects)} subjects saved to d_data/madgrades_subjects.csv")

    # 3) instructors
    print("Fetching instructors…")
    instructors = paginate("/instructors")
    pd.DataFrame(instructors).to_csv(DATA_DIR / "madgrades_instructors.csv", index=False)
    print(f"→ {len(instructors)} instructors saved to d_data/madgrades_instructors.csv")

    # 4) detailed course info
    print("Fetching course details…")
    details: List[Dict[str, Any]] = []
    for c in tqdm(courses, desc="courses"):
        uuid = c.get("uuid") if isinstance(c, dict) else None
        if not uuid:
            continue
        try:
            r = requests.get(f"{API_BASE}/courses/{uuid}", headers=HEADERS, timeout=30)
            r.raise_for_status()
            details.append(r.json())
        except Exception as e:
            print(f"⚠️ failed detail for {uuid}: {e}", file=sys.stderr)

    with open(DATA_DIR / "madgrades_course_details.json", "w", encoding="utf-8") as f:
        json.dump(details, f, ensure_ascii=False, indent=2)
    print(f"→ {len(details)} course details saved to d_data/madgrades_course_details.json")

if __name__ == "__main__":
    main()