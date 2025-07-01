"""Scrape UW Course Search & Enroll for given term"""

from pathlib import Path
import sys, time, contextlib

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from term_utils import term_code

# --- config & args ---
DATA_DIR = Path("d_data"); DATA_DIR.mkdir(exist_ok=True)
term_arg = sys.argv[1] if len(sys.argv) > 1 else None
TERM      = term_code(term_arg)
BASE_URL  = "https://public.enroll.wisc.edu/search"



def get_subject_codes(driver: webdriver.Chrome) -> list[str]:
    driver.get(f"{BASE_URL}?term={TERM}")
    time.sleep(1)

    mats = driver.find_elements(By.CSS_SELECTOR, "mat-select")
    if len(mats) < 2:
        raise RuntimeError(f"Expected ≥2 mat-selects, got {len(mats)}")
    subj_dd = mats[1]

    # open subject dropdown
    subj_dd.click()

    # wait for options to appear in the overlay
    try:
        WebDriverWait(driver, 8).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".cdk-overlay-pane mat-option"))
        )
    except TimeoutException:
        raise RuntimeError("Subject options never appeared – check selector `.cdk-overlay-pane mat-option`")

    # scrape codes
    opts = driver.find_elements(By.CSS_SELECTOR, ".cdk-overlay-pane mat-option")
    vals = []
    for o in opts:
        v = o.get_attribute("value")
        if v:
            vals.append(v)
        else:
            txt = o.text.strip()
            if txt:
                vals.append(txt.split()[0])

    # close via backdrop click (not subj_dd.click())
    try:
        driver.find_element(By.CSS_SELECTOR, ".cdk-overlay-backdrop").click()
    except Exception:
        pass  # if backdrop’s gone, no biggie

    if not vals:
        raise RuntimeError("Found mat-options but no codes extracted – inspect option texts")

    return vals

def scrape_subject(driver: webdriver.Chrome, subj_code: str) -> list[dict[str, str]]:
    # build the URL
    url = f"{BASE_URL}?term={TERM}&subject={subj_code}"
    driver.get(url)
    time.sleep(1)

    # fire off the search
    with contextlib.suppress(Exception):
        btn = driver.find_element(By.CSS_SELECTOR, "button[type=submit], button.k-button.k-primary")
        btn.click()

    # wait up to 10s for course cards to show
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.course-card"))
        )
    except TimeoutException:
        print(f"WARNING: no courses found for subject {subj_code}")

    out, seen, last_h = [], 0, 0
    while True:
        cards = driver.find_elements(By.CSS_SELECTOR, "div.course-card")
        new   = cards[seen:]
        for c in new:
            hdr = c.find_element(By.CSS_SELECTOR, ".course-header").text
            sub, num, *t = hdr.split(maxsplit=2)
            title = t[0] if t else ""
            with contextlib.suppress(Exception):
                c.find_element(By.CSS_SELECTOR, ".expand-icon").click()
            for row in c.find_elements(By.CSS_SELECTOR, "tbody tr"):
                cols = [td.text.strip() for td in row.find_elements(By.TAG_NAME, "td")]
                if len(cols) < 6: continue
                out.append({
                    "subject":         sub,
                    "catalog_number":  num,
                    "title":           title,
                    "section":         cols[0],
                    "mode":            cols[1],
                    "credits":         cols[2],
                    "meeting":         cols[3],
                    "instructor":      cols[4],
                    "enrollment":      cols[5],
                })
        seen = len(cards)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(0.8)
        h = driver.execute_script("return document.body.scrollHeight")
        if h == last_h: break
        last_h = h

    return out

def main():
    opts    = Options();         opts.add_argument("--headless")
    service = Service(ChromeDriverManager().install())
    drv     = webdriver.Chrome(service=service, options=opts)

    try:
        all_rows = []
        for code in get_subject_codes(drv):
            batch = scrape_subject(drv, code)
            all_rows.extend(batch)
            print(f"{code}: {len(all_rows)} rows so far")
        out = DATA_DIR / f"course_search_{TERM}.csv"
        pd.DataFrame(all_rows).to_csv(out, index=False)
        print(f"Done! Wrote {len(all_rows)} rows to {out}")
    finally:
        drv.quit()

if __name__ == "__main__":
    main()