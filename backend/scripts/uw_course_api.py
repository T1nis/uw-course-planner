#!/usr/bin/env python3
"""
uw_course_api.py - CLI client for the UW Course Map content API

Endpoints implemented
  update            -> /update.json
  subjects          -> /subjects.json
  terms             -> /terms.json
  course <code>     -> /course/{courseCode}.json

By default the *course* sub‑command now saves the JSON response to
`queried_data/<COURSECODE>.json` (folder is created if absent).  Use
`--stdout` to override and print to the console, or `--out FILEPATH` to pick a
custom file.

Examples
--------
# Save COMPSCI 300 to queried_data/COMPSCI_300.json
python uw_course_api.py course COMPSCI_300

# Same request but stream to the terminal instead
python uw_course_api.py course COMPSCI_300 --stdout

# Custom output location
python uw_course_api.py course COMPSCI_300 --out cs300.json

# All other commands remain unchanged
python uw_course_api.py subjects
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import requests

BASE_URL = "https://static.uwcourses.com"
DEFAULT_DIR = Path("queried_data")


def _fetch(endpoint: str) -> dict | list:
    """GET <BASE_URL>/<endpoint> and return parsed JSON (raise on error)."""
    url = f"{BASE_URL}{endpoint}"
    res = requests.get(url, timeout=10)
    res.raise_for_status()
    return res.json()


# ---------- sub‑command handlers ----------------------------------------------

def _cmd_update(_: argparse.Namespace) -> None:
    print(json.dumps(_fetch("/update.json"), indent=2))


def _cmd_subjects(args: argparse.Namespace) -> None:
    data: dict[str, str] = _fetch("/subjects.json")
    if args.code:
        key = args.code.upper()
        if key not in data:
            sys.exit(f"ERROR: subject code {key!r} not found")
        print(f"{key}: {data[key]}")
    else:
        print(json.dumps(data, indent=2))


def _cmd_terms(_: argparse.Namespace) -> None:
    print(json.dumps(_fetch("/terms.json"), indent=2))


def _write_json(obj: object, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2)
    print(f"Saved to {path}")


def _cmd_course(args: argparse.Namespace) -> None:
    # sanitize identifier
    code_raw = args.course_code
    code = code_raw.replace("/", "_").replace(" ", "_").upper()
    data = _fetch(f"/course/{code}.json")

    # only a field?
    if args.field is not None:
        cursor: object = data
        for part in args.field.split("."):
            try:
                cursor = (
                    cursor[int(part)] if isinstance(cursor, list) and part.isdigit() else cursor[part]  # type: ignore[index]
                )
            except (KeyError, IndexError, TypeError):
                sys.exit(f"ERROR: field path '{args.field}' not found in object")
        data = cursor  # redefine so we output the extracted fragment

    # decide destination
    if args.stdout:
        print(json.dumps(data, indent=2))
    else:
        out_path = Path(args.out) if args.out else DEFAULT_DIR / f"{code}.json"
        _write_json(data, out_path)


# ---------- CLI plumbing -------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="uw_course_api",
        description="Query the UW Course Map public JSON API from the command line.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("update", help="show last-updated timestamp").set_defaults(
        func=_cmd_update
    )

    ps = sub.add_parser("subjects", help="list or look up departments")
    ps.add_argument("-c", "--code", help="single subject code (e.g. COMPSCI)")
    ps.set_defaults(func=_cmd_subjects)

    sub.add_parser("terms", help="list all academic terms").set_defaults(func=_cmd_terms)

    pc = sub.add_parser("course", help="retrieve a course by code (saves to file by default)")
    pc.add_argument("course_code", help="course identifier (slashes or spaces allowed)")
    pc.add_argument("-f", "--field", metavar="PATH", help="return only a nested field (dot-separated path)")
    pc.add_argument("--stdout", action="store_true", help="print JSON to terminal instead of saving to file")
    pc.add_argument("--out", metavar="FILE", help="explicit output filepath (implies --stdout is false)")
    pc.set_defaults(func=_cmd_course)

    sub.add_parser("help", help="show this help message and exit")
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.command == "help":
        parser.print_help()
        sys.exit(0)

    try:
        args.func(args)  # type: ignore[attr-defined]
    except requests.HTTPError as e:
        code = e.response.status_code
        msg = "resource not found" if code == 404 else str(e)
        sys.exit(f"ERROR HTTP {code}: {msg}")
    except requests.RequestException as e:
        sys.exit(f"ERROR: network error: {e}")


if __name__ == "__main__":
    main()
