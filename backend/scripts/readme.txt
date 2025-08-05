UW Course Data Helper – Quick Usage Guide

Version: 1.2.5

1. Quickstart
-------------
- Fetch a single course and save to file:
    python uw_course_api.py course COMPSCI_300

- Fetch a single course and print to console:
    python uw_course_api.py course COMPSCI_300 --stdout

- Bulk-download all courses (default resume):
    python uw_course_api.py all

- Reset and re-download all courses:
    python uw_course_api.py all --reset

- Update only stale files, then resume:
    python uw_course_api.py all --update-existing

2. Global Options
-----------------
--safe            Run in safe mode (reduced features)
--verbose         Enable debug logs
-d, --dev         Developer mode (unlocks config and test)

3. Command: course
------------------
Usage:
    python uw_course_api.py course CODE [options]

Options:
  CODE                Course identifier (e.g. COMPSCI_300)
  -f, --field PATH    Extract nested JSON via dot-path (e.g. schedules.0.days)
  --stdout            Print JSON to terminal instead of saving
  --out FILE          Save JSON to the specified FILE

Examples:
  python uw_course_api.py course MATH_101 -f "sections.0.instructors"
  python uw_course_api.py course PHYS_201 --out physics201.json

4. Command: all
--------------
Usage:
    python uw_course_api.py all [options]

Options:
  -u, --update-existing    Re-fetch stale files before downloading new ones
  -r, --reset              Delete existing files and start from scratch
  -f, --force              With -u, re-fetch all existing files
  -p, --pretty             Pretty-print JSON (indent=2)
  -m N, --max-workers N    Use N parallel downloads (default 5, capped)
  --subjects LIST          Comma-separated list of subject codes (e.g. COMPSCI,MATH)
  --range START-END        Range for one subject, e.g. COMPSCI_1000-COMPSCI_1100

Examples:
  python uw_course_api.py all -p
  python uw_course_api.py all -u
  python uw_course_api.py all -r --subjects COMPSCI,STAT
  python uw_course_api.py all --range ART_200-ART_250 -m 10

5. Command: config (dev only)
-----------------------------
Usage:
    python uw_course_api.py config get all
    python uw_course_api.py config get max_workers_cap
    python uw_course_api.py -d config set max_workers_cap 30

6. Command: test (dev only)
---------------------------
Usage:
    python uw_course_api.py -d test

This runs the built-in test suite and prints pass/fail for each check.

7. Advanced Flags
-----------------
--subjects and --range can be combined with -u or -r.
--max-workers prompts confirmation if higher than default.
Course names cache: a full run without filters saves course list to c-data/core/course_names.json.

8. File Locations
-----------------
- Downloads: c-data/courses[/filtered/...]
- Config:   c-data/settings/config.json
- Logs:     c-data/core/logs/app.log