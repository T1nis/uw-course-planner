

#!/usr/bin/env python3
"""
uw_course_api.py – CLI client for the UW Course Map content API v1.2.5

Usage examples (normal mode):
  uw_course_api.py course COMPSCI_300
  uw_course_api.py all
  uw_course_api.py all -p               # pretty-print JSON
  uw_course_api.py all -m 10            # 10 parallel downloads
  uw_course_api.py all -u
  uw_course_api.py all -r
  uw_course_api.py all --subjects COMPSCI,MATH
  uw_course_api.py all --range COMPSCI_1000-COMPSCI_1100

Global flags:
  --safe                               # force “safe mode” (reduced functionality)
  --verbose                            # enable debug logging

Developer mode:
  -d, --dev                            # show extra commands
  config <get|set> <key|all> [value]   # inspect or modify settings
  test                                  # run built-in test suite
"""
from __future__ import annotations
import sys
import signal
import importlib.util
import argparse
import json
import time
import logging
import threading
from pathlib import Path
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
import requests

# -------------------------------------------------------------------
#constants
# -------------------------------------------------------------------
VERSION = "1.2.5"
VERSION_BANNER = f"UW Course Data Helper {VERSION} by Hassam Nizami"
BASE_URL = "https://static.uwcourses.com"
ROOT = Path("c-data")
SETTINGS_DIR = ROOT / "settings"
CONFIG_FILE = SETTINGS_DIR / "config.json"
LOG_DIR = ROOT / "core" / "logs"
ETAG_CACHE = LOG_DIR / "etag_cache.json"
LOG_FILE = LOG_DIR / "app.log"
COURSE_NAMES = ROOT / "core" / "course_names.json"
DEFAULT_DIR = ROOT

print(VERSION_BANNER)

# -------------------------------------------------------------------
# check files/folders
# -------------------------------------------------------------------
for d in (SETTINGS_DIR, LOG_DIR, COURSE_NAMES.parent):
    d.mkdir(parents=True, exist_ok=True)
if not ETAG_CACHE.exists():
    ETAG_CACHE.write_text("{}", encoding="utf-8")

# -------------------------------------------------------------------
# Config
# -------------------------------------------------------------------
_default_config = {"max_workers_cap": 20}
def load_config() -> dict:
    if not CONFIG_FILE.exists():
        save_config(_default_config)
        return dict(_default_config)
    return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))

def save_config(cfg: dict) -> None:
    SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2), encoding="utf-8")

_cfg = load_config()

# -------------------------------------------------------------------
# Logging
# -------------------------------------------------------------------
logger = logging.getLogger("uw_course_api")
logger.setLevel(logging.INFO)
fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.addHandler(fh)
ch = logging.StreamHandler(sys.stderr)
ch.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
logger.addHandler(ch)

# -------------------------------------------------------------------
# SIGINT handler for clean exit
# -------------------------------------------------------------------
def _sigint_handler(signum, frame):
    print("\nInterrupted, shutting down.")
    sys.exit(1)
signal.signal(signal.SIGINT, _sigint_handler)

# -------------------------------------------------------------------
# Dependency check & safe mode
# -------------------------------------------------------------------
REQUIRED = {"requests": ">=2.0.0", "rich": ">=9.0.0", "tenacity": ">=8.0.0"}
_missing = [name for name in REQUIRED if importlib.util.find_spec(name) is None]
SAFE_MODE = False
if _missing:
    SAFE_MODE = True
    msg = f"SAFE MODE: missing packages: {', '.join(_missing)}. Reduced functionality."
    logger.warning(msg)
    print(msg)

# -------------------------------------------------------------------
# Pre-parse global flags
# -------------------------------------------------------------------
_pre = argparse.ArgumentParser(add_help=False)
_pre.add_argument("--safe", action="store_true", help="force safe mode")
_pre.add_argument("--verbose", action="store_true", help="enable debug logging")
_pre.add_argument("-d", "--dev", action="store_true", help="developer mode")
_known, _rest = _pre.parse_known_args()

if _known.safe:
    SAFE_MODE = True
    print("SAFE MODE forced: reduced functionality enabled")
    logger.warning("SAFE MODE forced via --safe")

if _known.verbose:
    logger.setLevel(logging.DEBUG)
    logger.debug("Verbose logging enabled")

# -------------------------------------------------------------------
# Conditional imports
# -------------------------------------------------------------------
if not SAFE_MODE:
    from rich import print as rprint
    from rich.live import Live
    from rich.panel import Panel
    from rich.text import Text
    from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

# -------------------------------------------------------------------
# Shared HTTP session
# -------------------------------------------------------------------
session = requests.Session()
session.headers.update({"User-Agent": f"uw_course_api/{VERSION}"})

# -------------------------------------------------------------------
# ETag cache utilities
# -------------------------------------------------------------------
_etag_lock = threading.Lock()
def load_etags() -> dict[str, str]:
    with _etag_lock:
        return json.loads(ETAG_CACHE.read_text(encoding="utf-8"))
def save_etags(d: dict[str, str]) -> None:
    with _etag_lock:
        ETAG_CACHE.write_text(json.dumps(d, indent=2), encoding="utf-8")

# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------
def human_bytes(n: float) -> str:
    for u in ("B","KB","MB","GB"):
        if n < 1024:
            return f"{n:.2f}{u}"
        n /= 1024
    return f"{n:.2f}TB"

def write_json(obj: object, dest: Path, indent: int|None = 2) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(obj, indent=indent) if indent is not None else json.dumps(obj, separators=(",",":"))
    dest.write_text(text, encoding="utf-8")
    logger.debug(f"Wrote JSON to {dest}")
    
def fmt_dur(seconds: float) -> str:
    """
    Turn a duration in seconds into:
      • “123 ms” if under 1 s
      • “12.34 s” if under 60 s
      • “M:SS” for longer durations
    """
    if seconds < 1:
        return f"{int(seconds * 1000)} ms"
    if seconds < 60:
        return f"{seconds:.2f} s"
    minutes = int(seconds // 60)
    sec = int(seconds % 60)
    return f"{minutes}:{sec:02d}"

# -------------------------------------------------------------------
# HTTP GET with ETag & retry (no retry on 404)
# -------------------------------------------------------------------
if not SAFE_MODE:
    @retry(
        retry=retry_if_exception_type(requests.RequestException),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=5),
        stop=stop_after_attempt(3),
    )
    def http_get(path: str, etag: str|None = None) -> requests.Response:
        url = BASE_URL + path
        headers = {}
        if etag:
            headers["If-None-Match"] = etag
        logger.debug(f"GET {url}")
        r = session.get(url, headers=headers, timeout=10)
        if r.status_code == 404 or r.status_code == 304:
            return r
        r.raise_for_status()
        return r
else:
    def http_get(path: str, etag: str|None = None) -> requests.Response:
        url = BASE_URL + path
        logger.debug(f"GET {url}")
        return session.get(url, timeout=10)


def cmd_update(_: argparse.Namespace):
    data = http_get("/update.json").json()
    print(json.dumps(data, indent=2))

def cmd_subjects(args: argparse.Namespace):
    data = http_get("/subjects.json").json()
    if args.code:
        c = args.code.upper()
        if c not in data:
            sys.exit(f"ERROR: '{c}' not found")
        print(f"{c}: {data[c]}")
    else:
        print(json.dumps(data, indent=2))

def cmd_terms(_: argparse.Namespace):
    print(json.dumps(http_get("/terms.json").json(), indent=2))

def cmd_course(args: argparse.Namespace) -> None:
    """
    Fetch a single course and report how long it took.
    """
    code = args.course_code.replace("/","_").replace(" ","_").upper()
    path = f"/course/{code}.json"
    etags = load_etags()
    et = etags.get(code)

    t0 = time.monotonic()
    r = http_get(path, et)
    elapsed = time.monotonic() - t0

    if r.status_code == 404:
        logger.info(f"{code} not found (404), skipping")
        print(f"{code}: not found (took {fmt_dur(elapsed)})")
        return

    if r.status_code == 304:
        logger.info(f"{code} not modified, skipping write")
        print(f"{code}: not modified (took {fmt_dur(elapsed)})")
        return

    data = r.json()
    outp = Path(args.out) if args.out else DEFAULT_DIR/f"{code}.json"
    write_json(data, outp, indent=2)

    if (E := r.headers.get("ETag")):
        etags[code] = E
        save_etags(etags)

    msg = f"Saved {code} to {outp} (took {fmt_dur(elapsed)})"
    if args.stdout:
        print(json.dumps(data, indent=2))
        print(msg)
    else:
        print(msg)
def cmd_all(args: argparse.Namespace) -> None:
    """
    Bulk fetch courses, resuming from progress.json unless reset or update-existing,
    displaying last attempted/saved, per-task timing, and an overall summary.
    """
    indent = 2 if args.pretty else None
    cap = _cfg["max_workers_cap"]


    if args.max_workers is not None:
        req = args.max_workers
        if req > cap:
            print(f"Note: max-workers capped at {cap} (requested {req})")
            req = cap
        if not input(f"Proceed with {req} workers? [y/N]: ").strip().lower().startswith("y"):
            sys.exit("Aborted.")
        workers = req
    else:
        workers = min(5, cap)

    print(f"Starting with up to {workers} workers (cap={cap})...")


    use_cache = (
        COURSE_NAMES.exists()
        and not args.reset
        and not args.update_existing
        and not args.subjects
        and not args.range
        and args.max_workers is None
    )
    if use_cache:
        created = datetime.fromtimestamp(COURSE_NAMES.stat().st_mtime).isoformat()
        print(f"Using cached course list from {created}")
        codes = json.loads(COURSE_NAMES.read_text(encoding="utf-8"))
    else:
        subs_map = http_get("/subjects.json").json()
        if args.subjects:
            subjects = args.subjects.split(",")
        else:
            subjects = list(subs_map.keys())

        if args.range:
            try:
                start, end = args.range.split("-")
                sub_s, num_s = start.split("_")
                sub_e, num_e = end.split("_")
                if sub_s != sub_e:
                    raise ValueError
                subjects = [sub_s]
                num_start, num_end = int(num_s), int(num_e)
            except ValueError:
                sys.exit("Invalid --range format; expected SUBJECT_start-SUBJECT_end")
        else:
            num_start, num_end = 0, 999

        codes = [
            f"{subj}_{n}"
            for subj in subjects
            for n in range(num_start, (num_end if args.range else 1000))
        ]

    total = len(codes)
    t_start = time.monotonic()
    total_bytes = 0


    if args.subjects or args.range:
        filt = (args.subjects or args.range).replace("/", "_")
        out_root = ROOT / "courses" / "filtered" / filt
    else:
        out_root = ROOT / "courses"
    out_root.mkdir(parents=True, exist_ok=True)
    prog_file = out_root / "progress.json"


    if args.reset:

        for p in out_root.glob("*.json"):
            p.unlink()

        if prog_file.exists():
            prog_file.unlink()


    if prog_file.exists() and not args.reset and not args.update_existing:
        prog = json.loads(prog_file.read_text(encoding="utf-8"))
        last_done = prog.get("last_downloaded")
        if last_done:
            try:
                idx = codes.index(last_done) + 1
                codes = codes[idx:]
                total = len(codes)
            except ValueError:
                pass


    if args.update_existing:
        api_ts = http_get("/update.json").json()["updated_on"]
        api_dt = datetime.fromisoformat(api_ts.replace("Z", "+00:00"))
        existing = [p.stem for p in out_root.glob("*.json")]
        stale = []
        for code in existing:
            m = datetime.fromtimestamp(
                (out_root / f"{code}.json").stat().st_mtime,
                timezone.utc
            )
            if args.force or m <= api_dt:
                stale.append(code)
        codes = stale + codes
        total = len(codes)


    last_attempted: str | None = None
    last_saved:     str | None = None
    saved_count = 0

    def task(code: str) -> tuple[str, int, float]:
        t0 = time.monotonic()
        etags = load_etags()
        et = etags.get(code)
        r = http_get(f"/course/{code}.json", et)
        took = time.monotonic() - t0

        if r.status_code in (404, 304):
            return code, 0, took

        data = r.json()
        write_json(data, out_root / f"{code}.json", indent)
        if (etag := r.headers.get("ETag")):
            etags[code] = etag
            save_etags(etags)
        return code, len(r.content), took


    live_ctx = None
    if not SAFE_MODE:
        from rich.live import Live
        from rich.panel import Panel
        from rich.text import Text
        live_ctx = Live(refresh_per_second=4)
        live_ctx.__enter__()


    try:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            for i, (code, got, took) in enumerate(pool.map(task, codes), start=1):
                last_attempted = code
                if got > 0:
                    last_saved = code
                    saved_count += 1
  
                    write_json(
                        {"last_downloaded": last_saved, "target_end": codes[-1]},
                        prog_file,
                        indent=2
                    )
                total_bytes += got

                elapsed = time.monotonic() - t_start
                speed = total_bytes / elapsed if elapsed > 0 else 0.0

                parts = [
                    ("Last attempted: ", "bold"), last_attempted or "<none>", "\n",
                    ("Last saved:     ", "bold"), last_saved    or "<none>", "\n",
                    ("Saved count:    ", "bold"), f"{saved_count}/{total}", "\n",
                    ("Last task time: ", "bold"), fmt_dur(took), "\n",
                    ("Downloaded:     ", "bold"), human_bytes(total_bytes),
                    (" @ ", None), human_bytes(speed) + "/s"
                ]

                if live_ctx:
                    live_ctx.update(Panel(Text.assemble(*parts), title="Progress"))
                else:
                    print(
                        f"[{i}/{total}] Attempted={last_attempted} | "
                        f"Saved={last_saved or '-'} ({saved_count}) | "
                        f"TaskTime={fmt_dur(took)} | "
                        f"TotalDown={human_bytes(total_bytes)}@{human_bytes(speed)}/s"
                    )

    except KeyboardInterrupt:
        if live_ctx:
            live_ctx.update(Text("Interrupted by user.", style="bold red"))
        sys.exit(1)
    finally:
        if live_ctx:
            live_ctx.__exit__(None, None, None)


    print(
        f"Done: {saved_count}/{total} courses saved, "
        f"{human_bytes(total_bytes)} downloaded in {fmt_dur(time.monotonic() - t_start)}"
    )

  
    if not (args.subjects or args.range or args.update_existing) and saved_count == total:
        names = sorted(p.stem for p in (ROOT/"courses").glob("*.json"))
        write_json(names, COURSE_NAMES, indent=2)
        print(f"Wrote complete course list ({len(names)}) to {COURSE_NAMES}")



def cmd_config(args: argparse.Namespace):
    cfg = load_config()
    if args.action == "get":
        if args.key == "all":
            print(json.dumps(cfg, indent=2))
        else:
            val = cfg.get(args.key)
            if val is None:
                sys.exit(f"Unknown config key '{args.key}'")
            print(f"{args.key} = {val}")
    else:  # set
        if not args.dev:
            sys.exit("Config set only in dev mode")
        if args.key not in cfg:
            sys.exit(f"Unknown config key '{args.key}'")
        try:
            new = int(args.value)
        except:
            sys.exit("Value must be integer")
        cfg[args.key] = new
        save_config(cfg)
        print(f"Set {args.key} = {new}")

def cmd_test(_: argparse.Namespace) -> None:
    tests: list[tuple[str,str]] = []

    #update.json endpoint
    try:
        data = http_get("/update.json").json()
        assert isinstance(data, dict) and "updated_on" in data
        tests.append(("update.json", "pass"))
    except Exception as e:
        tests.append(("update.json", f"fail: {e}"))

    #subjects.json endpoint
    try:
        subs = http_get("/subjects.json").json()
        assert isinstance(subs, dict) and subs
        tests.append(("subjects.json", "pass"))
    except Exception as e:
        tests.append(("subjects.json", f"fail: {e}"))

    #erms.json endpoint
    try:
        terms = http_get("/terms.json").json()
        assert isinstance(terms, dict) and terms
        tests.append(("terms.json", "pass"))
    except Exception as e:
        tests.append(("terms.json", f"fail: {e}"))

    #single course endpoint
    try:
        course = http_get("/course/COMPSCI_300.json").json()
        assert isinstance(course, dict)
        assert "course_reference" in course and "course_title" in course
        tests.append(("course COMPSCI_300", "pass"))
    except Exception as e:
        tests.append(("course COMPSCI_300", f"fail: {e}"))

    #write_json
    try:
        tmp = DEFAULT_DIR/"test_write.json"
        write_json({"x":1}, tmp, indent=2)
        loaded = json.loads(tmp.read_text())
        assert loaded == {"x":1}
        tmp.unlink()
        tests.append(("write_json", "pass"))
    except Exception as e:
        tests.append(("write_json", f"fail: {e}"))

    #config default
    try:
        cfg = load_config()
        assert "max_workers_cap" in cfg and isinstance(cfg["max_workers_cap"], int)
        tests.append(("config default", "pass"))
    except Exception as e:
        tests.append(("config default", f"fail: {e}"))

    #config set/get
    try:
        old = cfg["max_workers_cap"]
        cfg["max_workers_cap"] = old + 1
        save_config(cfg)
        assert load_config()["max_workers_cap"] == old + 1
        cfg["max_workers_cap"] = old
        save_config(cfg)
        tests.append(("config set/get", "pass"))
    except Exception as e:
        tests.append(("config set/get", f"fail: {e}"))

    #help
    try:
        norm = build_parser(False).format_help()
        for flag in ["-p","--pretty","-m","--max-workers","--subjects","--range","config <get|set>","--safe","--verbose"]:
            assert flag in norm
        assert "update" not in norm
        tests.append(("help normal", "pass"))
    except AssertionError as e:
        tests.append(("help normal", f"fail: {e}"))

    #dev -h
    try:
        devh = build_parser(True).format_help()
        for cmd in ["update","subjects","terms","course","all","config","test"]:
            assert cmd in devh
        tests.append(("help dev", "pass"))
    except AssertionError as e:
        tests.append(("help dev", f"fail: {e}"))

   
    try:
        assert VERSION_BANNER == f"UW Course Data Helper {VERSION} by Hassam Nizami"
        tests.append(("version banner", "pass"))
    except AssertionError as e:
        tests.append(("version banner", f"fail: {e}"))

    
    try:
        assert LOG_DIR.exists() and ETAG_CACHE.exists()
        assert isinstance(load_etags(), dict)
        tests.append(("etag & logs", "pass"))
    except Exception as e:
        tests.append(("etag & logs", f"fail: {e}"))

    for name, result in tests:
        print(f"{name}: {result}")

def build_parser(dev_mode: bool) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="uw_course_api.py",
        formatter_class=argparse.RawTextHelpFormatter,
        description="UW Course Data Fetcher",
    )
    p.add_argument("--safe", action="store_true", help="force safe mode")
    p.add_argument("--verbose", action="store_true", help="enable debug logging")
    p.add_argument("-d","--dev", action="store_true", help="developer mode")
    subs = p.add_subparsers(dest="cmd")

    subs.add_parser("update", help="show last-updated").set_defaults(func=cmd_update)

    sj = subs.add_parser("subjects", help="list/look up subjects")
    sj.add_argument("-c","--code", help="single subject code")
    sj.set_defaults(func=cmd_subjects)

    subs.add_parser("terms", help="list terms").set_defaults(func=cmd_terms)

    cr = subs.add_parser("course", help="fetch one course")
    cr.add_argument("course_code")
    cr.add_argument("-f","--field", help="nested field path")
    cr.add_argument("--stdout", action="store_true")
    cr.add_argument("--out", help="output file")
    cr.set_defaults(func=cmd_course)

    ap = subs.add_parser("all", help="fetch all or filtered courses")
    ap.add_argument("-u","--update-existing", action="store_true")
    ap.add_argument("-r","--reset", action="store_true")
    ap.add_argument("-f","--force", action="store_true")
    ap.add_argument("-p","--pretty", action="store_true")
    ap.add_argument("-m","--max-workers", type=int, help="parallel downloads")
    ap.add_argument("--subjects", help="comma-separated subjects")
    ap.add_argument("--range", help="SUBJECT_start-SUBJECT_end")
    ap.set_defaults(func=cmd_all)

    if dev_mode:
        cfgp = subs.add_parser("config", help="get or set config")
        cfgp.add_argument("action", choices=["get","set"])
        cfgp.add_argument("key", help="config key or 'all'")
        cfgp.add_argument("value", nargs="?", help="value when setting")
        cfgp.set_defaults(func=cmd_config)

        tt = subs.add_parser("test", help="run test suite")
        tt.set_defaults(func=cmd_test)

    return p

def main() -> None:
    parser = build_parser(dev_mode=_known.dev)
    args    = parser.parse_args(_rest)
    if not args.cmd:
        parser.print_help()
        sys.exit(0)
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        logger.exception("Unhandled error")
        sys.exit(f"ERROR: {e}")

if __name__ == "__main__":
    main()