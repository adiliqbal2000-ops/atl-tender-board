#!/usr/bin/env python3
"""
Al-Tariq oil & gas tender scraper.

Fetches tender listings from public company pages and writes data/tenders.json.
Run on a schedule by .github/workflows/scrape.yml — no manual work needed once set up.

Uses a headless browser (Playwright) rather than a plain HTTP request, because
PARCO's tender table loads via JavaScript after the page opens — a plain
`requests.get()` only sees the empty page shell and finds nothing.

IMPORTANT — read this before relying on it:
  - PARCO: working — renders the page, then parses the text pattern the table
    prints in (type / title / number / issue date / close date / action).
  - PSO, SNGPL, SSGC, ARL, NRL, PRL: stub functions — no public listing page
    was found for these; most tenders route through SAP Ariba or the
    government EPADS portal, both login-gated and unscrapable anonymously.
  - If scrape_parco() ever returns 0 again, PARCO's page layout changed.
    Check the Action's run log — it prints how many tenders were found and
    the first few raw lines it parsed, to help debug.
"""
import json
import re
import sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

USER_AGENT = "Mozilla/5.0 (compatible; ATL-TenderBoard/1.0; +https://atlpk.com)"

DATE_RE = re.compile(r"^\d{2}\.\d{2}\.\d{4}$|^\d{4}-\d{2}-\d{2}$")
ACTION_RE = re.compile(r"^(Apply Here|Download|Apply)$", re.I)
TYPE_RE = re.compile(r"(tender\s*(notice|enquiry|type)|pre-?qualification|addendum|invitation for pre-?qualification)", re.I)


def parse_date(raw):
    """Convert DD.MM.YYYY or YYYY-MM-DD into ISO YYYY-MM-DD. Returns '' if unparseable."""
    if not raw:
        return ""
    raw = raw.strip()
    for fmt in ("%d.%m.%Y", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return ""


def fetch_rendered_html(url, timeout_ms=45000):
    """Load a page in a headless browser and return its fully-rendered HTML."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(user_agent=USER_AGENT)
        page.goto(url, timeout=timeout_ms, wait_until="networkidle")
        html = page.content()
        browser.close()
    return html


def parse_tender_lines(lines, org, source_url):
    """
    Generic parser for the repeating pattern PARCO's (and possibly similar
    WordPress-table) pages use once flattened to plain text:
        TYPE
        TITLE (one or more lines)
        TENDER NUMBER
        ISSUE DATE
        CLOSE DATE
        ACTION WORD (Apply Here / Download)
    Anchors on consecutive date-like lines, then works backward to the previous
    action line (or start) to recover the type + title block.
    """
    out = []
    n = len(lines)
    last_action_idx = -1
    i = 0
    while i < n - 1:
        if DATE_RE.match(lines[i]) and DATE_RE.match(lines[i + 1]):
            issue_date, close_date = lines[i], lines[i + 1]
            action = lines[i + 2] if i + 2 < n and ACTION_RE.match(lines[i + 2]) else ""
            no = lines[i - 1] if i - 1 >= 0 else ""

            j = i - 2
            block = []
            while j > last_action_idx:
                block.insert(0, lines[j])
                j -= 1

            ttype, title = "Tender", " ".join(block).strip()
            if block and TYPE_RE.search(block[0]) and len(block[0]) < 70:
                ttype = block[0]
                title = " ".join(block[1:]).strip()

            if title and no and len(title) < 400:
                out.append({
                    "org": org,
                    "title": title,
                    "no": no,
                    "type": "Prequalification" if "qualif" in ttype.lower() else "Tender",
                    "close": parse_date(close_date),
                    "bond": "",
                    "link": source_url,
                    "notes": f"Tender documents issued {issue_date}" if issue_date else "",
                })

            last_action_idx = i + 2 if action else i + 1
            i = last_action_idx + 1
            continue
        i += 1
    return out


def scrape_parco():
    url = "https://parco.com.pk/?p=16189"
    out = []
    try:
        html = fetch_rendered_html(url)
    except Exception as e:
        print(f"[parco] render failed: {e}", file=sys.stderr)
        return out

    soup = BeautifulSoup(html, "html.parser")
    lines = [l.strip() for l in soup.get_text("\n").split("\n") if l.strip()]

    # Start just after the "Tender Notices" heading, to skip nav/menu text
    start = 0
    for idx, l in enumerate(lines):
        if l.lower() == "tender notices":
            start = idx + 1
            break
    lines = lines[start:]

    print(f"[parco] {len(lines)} text lines after heading; first 10: {lines[:10]}", file=sys.stderr)
    out = parse_tender_lines(lines, org="PARCO", source_url=url)
    print(f"[parco] found {len(out)} tenders")
    return out


def scrape_pso():
    """STUB — PSO's procurement page mostly links out to per-tender SAP Ariba pages."""
    return []


def scrape_sngpl():
    """STUB — no confirmed public listing page; tenders route via EPADS (login required)."""
    return []


def scrape_ssgc():
    """STUB — no confirmed public listing page; tenders route via EPADS (login required)."""
    return []


def scrape_arl():
    """STUB — no confirmed public listing page found."""
    return []


def scrape_nrl():
    """STUB — no confirmed public listing page found."""
    return []


def scrape_prl():
    """STUB — no confirmed public listing page found."""
    return []


def main():
    all_tenders = []
    for fn in (scrape_parco, scrape_pso, scrape_sngpl, scrape_ssgc, scrape_arl, scrape_nrl, scrape_prl):
        try:
            all_tenders.extend(fn())
        except Exception as e:
            print(f"[{fn.__name__}] crashed: {e}", file=sys.stderr)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "tenders": all_tenders,
    }
    with open("data/tenders.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print(f"Wrote {len(all_tenders)} tenders to data/tenders.json")


if __name__ == "__main__":
    main()
