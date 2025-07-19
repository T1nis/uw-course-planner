# === term_utils.py ===
"""Translate human-readable academic term to PeopleSoft 4-digit code"""
import re
import sys
from datetime import datetime

SESSION_DIGITS = {
    'fall': 2,
    'spring': 4,
    'summer': 6,
    'winter': 8,
    'jterm': 8,
    'j-term': 8,
}
TERM_PATTERN = re.compile(
    r"(?P<year>\d{4})|(?P<season>spring|summer|fall|winter|jterm|j-term)",
    re.IGNORECASE
)

def _parse_term_text(text: str) -> tuple[int | None, str | None]:
    year = None
    season = None
    for match in TERM_PATTERN.finditer(text):
        if match.group('year') and year is None:
            year = int(match.group('year'))
        elif match.group('season') and season is None:
            season = match.group('season').lower()
    return year, season


def term_code(term: str | int | None = None, *, default_current=True) -> str:
    if term is None:
        if not default_current:
            raise ValueError("term must be provided when default_current=False")
        now = datetime.now()
        month = now.month
        year = now.year
        season = 'fall' if month >= 9 else 'summer' if month >= 5 else 'spring'
        return term_code(f"{season} {year}", default_current=False)
    if isinstance(term, int) or (isinstance(term, str) and term.isdigit() and len(term) == 4):
        code = int(term)
        session_digit = code % 10
        if session_digit not in SESSION_DIGITS.values():
            raise ValueError(f"Invalid session digit {session_digit} in code {code}.")
        return str(code)
    text = str(term).lower()
    text = re.sub(r"[\u2011\u2013–—]", '-', text)
    year, season = _parse_term_text(text)
    if season not in SESSION_DIGITS:
        raise ValueError(f"Could not recognize season in '{term}'")
    if year is None:
        raise ValueError(f"Could not recognize year in '{term}'")
    if not (1900 <= year <= 2100):
        raise ValueError("Year out of supported range 1900-2100.")
    code_val = (year - 1900) * 10 + SESSION_DIGITS[season]
    return str(code_val)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description="Translate academic term to PeopleSoft code"
    )
    parser.add_argument('term', nargs='?', help="e.g. 'Fall 2025' or '1262'")
    args = parser.parse_args()
    try:
        print(term_code(args.term))
    except Exception as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
