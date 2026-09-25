#!/usr/bin/env python3
"""
Al-Tariq oil & gas tender scraper.

Fetches tender listings from public company pages and writes data/tenders.json.
Run on a schedule by .github/workflows/scrape.yml — no manual work needed once set up.

IMPORTANT — read this before relying on it:
  - PARCO publishes a real, public, structured tender-listing page. That scraper
    (scrape_parco) is a working implementation against the page as it looked
    when this was built.
  - PSO, SNGPL, SSGC, ARL, NRL and PRL do not have an equivalent public listing
    page as far as could be found — most of their tenders are distributed
    through SAP Ariba or the government EPADS portal, both of which require a
    login and cannot be scraped by an anonymous script. Those functions below
    are left as clearly-marked stubs so you (or I, in a future session) can
    fill them in if/when a public listing page is found for them.
  - Websites change their HTML periodically. If scrape_parco() ever returns
    zero tenders, the page structure has probably changed and the selectors
    below need updating — check the Action's run log, it prints what it finds.
"""
import json
import re
import sys
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ATL-TenderBoard/1.0; +https://atlpk.com)"
}


def parse_date(raw):
    """Convert DD.MM.YYYY (or similar) into ISO YYYY-MM-DD. Returns '' if unparseable."""
    if not raw:
        return ""
    raw = raw.strip()
    for fmt in ("%d.%m.%Y", "%d-%m-%Y", "%d/%m/%Y", "%d.%m.%y"):
        try:
            return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return ""


def scrape_parco():
    """PARCO's public tender-notices page — a plain HTML table, no login required."""
    url = "https://parco.com.pk/?p=16189"
    out = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
    except Exception as e:
        print(f"[parco] fetch failed: {e}", file=sys.stderr)
        return out

    soup = BeautifulSoup(r.text, "html.parser")
    tables = soup.find_all("table")
    for table in tables:
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all(["td"])
            if len(cells) < 5:
                continue
            texts = [c.get_text(strip=True) for c in cells]
            # Skip header rows
            if texts[0].lower() in ("tender type", "type"):
                continue
            ttype = texts[0] if texts[0] else "Tender"
            title = texts[1] if len(texts) > 1 else ""
            no = texts[2] if len(texts) > 2 else ""
            issue_date = texts[3] if len(texts) > 3 else ""
            close_date = texts[4] if len(texts) > 4 else ""
            link_tag = row.find("a", href=True)
            link = link_tag["href"] if link_tag else url
            if not title:
                continue
            out.append({
                "org": "PARCO",
                "title": title,
                "no": no,
                "type": "Prequalification" if "pre-qual" in ttype.lower() or "prequal" in ttype.lower() else "Tender",
                "close": parse_date(close_date),
                "bond": "",
                "link": link if link.startswith("http") else url,
                "notes": f"Tender documents issued {issue_date}".strip() if issue_date else "",
            })
    print(f"[parco] found {len(out)} tenders")
    return out


def scrape_pso():
    """
    STUB — PSO's own procurement page (psopk.com/procurement) mainly links out to
    SAP Ariba per-tender pages rather than listing structured data on the page
    itself. Fetch + inspect it here if you want to extend this; left empty for now
    so the pipeline doesn't silently publish stale/wrong data.
    """
    return []


def scrape_sngpl():
    """STUB — no confirmed public listing page found; tenders route via EPADS (login required)."""
    return []


def scrape_ssgc():
    """STUB — no confirmed public listing page found; tenders route via EPADS (login required)."""
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
