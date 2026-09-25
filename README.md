# Al-Tariq Oil & Gas Tender Board — self-refreshing version

This is the standalone tender board app, plus a scraper that GitHub runs for you
on a schedule (every 6 hours by default), so the board updates itself with no
manual work and no dependency on anyone re-running searches.

## What's honestly live vs. not

- **PARCO** — genuinely scraped from their public tender-notices page. Real, working.
- **PSO, SNGPL, SSGC, ARL, NRL, PRL** — no public listing page could be found for
  these; most distribute tenders through SAP Ariba or the government EPADS portal,
  both of which require a login and can't be scraped anonymously. The scraper has
  stub functions for these (`scripts/scrape.py`) so they can be filled in later if
  a public page turns up — right now they contribute nothing, so you'll still want
  to check those six source buttons in the app yourself, or add tenders you find
  through the "Add tender" form (those are saved in your browser, separate from
  the auto-scraped data).

## One-time setup

1. Turn on GitHub Pages: repo → Settings → Pages → Source = "Deploy from a
   branch" → Branch = `main`, folder = `/ (root)` → Save.
2. Turn on Actions: repo → Actions tab → enable workflows if prompted.
3. Run it once manually: Actions → "Scrape tenders" → "Run workflow" → Run workflow.
4. Open your Pages URL — the header should show "Live data — auto-refreshed …"

From here it re-runs automatically every 6 hours, commits the updated
`data/tenders.json`, and your published page picks it up on next load.

## Changing the schedule

Edit `.github/workflows/scrape.yml`, the line `cron: "0 */6 * * *"`.
Cron syntax is `minute hour day month weekday`. E.g. `0 8 * * *` = once daily at
08:00 UTC.

## If PARCO's page layout changes and scraping breaks

Check Actions → the failed run's log — `scripts/scrape.py` prints how many
tenders it found. If PARCO returns 0, their page HTML changed; paste the log or
current page HTML to Claude and ask for a fix to `scrape_parco()`.

## Extending to other companies

If a public (no-login) tender listing page turns up for PSO, SNGPL, SSGC, ARL,
NRL or PRL, give Claude the URL and ask it to fill in the matching stub function
in `scripts/scrape.py`.
