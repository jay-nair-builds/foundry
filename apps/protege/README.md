# Protégé

**Invest like the greats.** See what the world's best investors own, what they changed last quarter, how copying them would have performed, and turn their top holdings into your own dollar and share plan.

A zero-dependency web app on GitHub Pages, fed by a small Python pipeline that runs in GitHub Actions. No server, no database, no API keys required.

## What it does

| Feature | How it works |
|---|---|
| Investor gallery | 13 investors to start, filterable by style. Add any 13F filer (see below). |
| Holdings and changes | Latest 13F portfolio, plus new, added, trimmed and exited positions vs the prior filing. |
| Track record | What copying would have returned: buy the top 10 holdings (max 25% each) on each filing date, rebalance at the next filing, against the S&P 500 (SPY). Includes the reporting delay. |
| Mimic portfolio | Enter an amount, positions to copy and a max weight. Get dollars, whole shares at the last close and leftover cash. Export CSV. |
| Compare | Overlap between any two investors. |
| Follow and alerts | Star investors (saved in your browser). A "New filing" badge appears when a followed investor files; optional browser notification. RSS/Atom feeds per investor and for all filings work with any feed reader or RSS-to-email service. |
| Add an investor | "+ Add investor" opens a pre-filled GitHub request. An Action checks the SEC, adds the fund, loads its filings and redeploys, usually within minutes. |

No brokerage connection and no order placement. It is a study and planning tool.

## Set it up (one time, about 10 minutes)

1. **Push the app** to `main` in this repository (the `apps/protege` folder, the three workflows in `.github/workflows` and the issue form in `.github/ISSUE_TEMPLATE`).
2. **Turn on Pages:** Settings, Pages, Source: **GitHub Actions**.
3. **Set your SEC identity:** Settings, Secrets and variables, Actions, Variables, new variable `SEC_USER_AGENT` = `Your Name you@example.com`. The SEC requires contact details.
4. **Allow Actions to write:** Settings, Actions, General, Workflow permissions, **Read and write**.
5. **Load real data:** Actions tab, "Refresh 13F data", Run workflow. It fetches filings, builds feeds, commits and deploys. Your site is then live at `https://jay-nair-builds.github.io/foundry/apps/protege/`.

Optional: add a repository secret `OPENFIGI_API_KEY` (free at openfigi.com) to speed up CUSIP-to-ticker mapping. Without it the pipeline still works, just more slowly.

Until step 5 runs, the site shows a "data files are missing" notice. The repository ships no sample data, so nothing invented is ever shown.

## How the data flows

```
SEC EDGAR 13F-HR ──> fetch_13f.py ──> data/holdings.*  (committed, quarterly)
                          │ OpenFIGI: CUSIP -> ticker (cached in data/cusips.json)
                          └──> feeds.py ──> feeds/*.xml  (committed, quarterly)
Stooq / Yahoo closes ──> refresh_prices.py ──> data/prices.*, data/track.*  (built at each deploy, weekdays)
GitHub issue "Add investor: ..." ──> add_investor.py ──> data/investors.json ──> fetch + deploy
```

## Run it locally

Open `index.html` in a browser. To refresh data on your own machine:

```bash
python3 scripts/fetch_13f.py --ua "Your Name you@example.com"   # holdings
python3 scripts/feeds.py                                          # alert feeds
python3 scripts/refresh_prices.py                                 # prices and track records
python3 -m unittest discover -s tests                             # offline tests
```

Python 3.9+, standard library only. Use `--only buffett,ackman` to refresh a subset.

## Limits, said plainly

- **13F shows the past.** Long US-listed equity only, filed up to 45 days after quarter end. Shorts, bonds, cash, options and non-US holdings are missing, and so is anything traded since. Bridgewater, Oaktree and Soros run far larger books than their 13F slice.
- **Track record is a simulation.** Price return only (no dividends), no fees, tax or slippage. It uses only information public on each filing date, but past results do not predict future ones. Investors with few priced positions show low coverage; the app reports it.
- **Prices are delayed daily closes**, not live quotes. Share counts are for planning, not order tickets.
- **Alerts are pull, not push.** The feeds update when the pipeline runs (quarterly for filings). Email alerts need a free RSS-to-email service pointed at a feed; there is no mailing list to leak.
- **Follows live in your browser** (local storage), not in an account.
- **Add-investor uses public search.** If a name matches several filers, the bot replies with candidates and asks for the CIK. Anyone with a GitHub account can file a request, so input is strictly validated and the roster is capped at 100; revert the bot's commit to remove an unwanted entry. Changes shown for quarters older than the latest three compare the top 25 positions only.
- **Tickers** come from OpenFIGI, with a small name map as fallback; unmapped issuers show by name and are left out of prices and track records.
- **Not tested against the live services.** The SEC, OpenFIGI, Stooq and Yahoo endpoints were not reachable from the environment this was built in. Parsers, the track-record maths, feeds and the add-investor logic are covered by offline tests with fixtures; the first Action run is the live test. Check its log.
- **Educational only. Nothing here is investment advice.**

## Files

```
index.html, styles.css, app.js     the app
data/investors.json                roster: name, fund, SEC CIK, style, tags (edit or extend by hand)
data/*.js, *.json                  generated data (written by the first refresh)
feeds/                             Atom feeds (generated)
scripts/                           sec.py, figi.py, prices.py, track.py, feeds.py, add_investor.py, fetch_13f.py, refresh_prices.py
tests/test_pipeline.py             offline tests
```

Sources: SEC EDGAR Form 13F-HR; OpenFIGI; Stooq and Yahoo Finance daily closes. Licensed under Apache-2.0 (see the repository [LICENSE](../../LICENSE)). A standalone build, separate from the Brand-to-Balance-Sheet method.

Protégé by Jay Nair · github.com/jay-nair-builds/foundry
