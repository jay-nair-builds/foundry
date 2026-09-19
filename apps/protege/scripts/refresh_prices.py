#!/usr/bin/env python3
"""Build data/prices.* (latest closes, for share counts) and data/track.* (mimic track records).

Runs after holdings are real (not sample). Needs internet access to Stooq / Yahoo Finance.
Usage: python3 scripts/refresh_prices.py
"""
import sys
from datetime import date, timedelta

import prices as pr
import track
from common import read_json, write_pair

BENCH = "SPY"
TOP_FOR_PRICES = 25


def main():
    h = read_json("holdings.json")
    if not h or h.get("sample"):
        print("Holdings are sample data; run fetch_13f.py first. Nothing to do.")
        return 0

    earliest = min(s["filed"] for r in h["investors"] for s in r["snapshots"])
    start = (date.fromisoformat(earliest) - timedelta(days=7)).isoformat()
    end = date.today().isoformat()

    tickers = {BENCH}
    for r in h["investors"]:
        for s in r["snapshots"]:
            tickers.update(p["ticker"] for p in s["positions"][:TOP_FOR_PRICES] if p.get("ticker"))

    history, missing = {}, []
    for t in sorted(tickers):
        rows = pr.fetch_history(t, start, end)
        (history.__setitem__(t, rows) if rows else missing.append(t))
    if BENCH not in history:
        print(f"Could not load benchmark {BENCH}; leaving existing price and track files untouched.", file=sys.stderr)
        return 1
    print(f"Loaded {len(history)} tickers; no data for {len(missing)}: {', '.join(missing[:20])}")

    asof = history[BENCH][-1][0]
    write_pair("prices", "PROTEGE_PRICES", {
        "sample": False, "asof": asof, "source": "Stooq / Yahoo Finance daily closes (delayed, split-adjusted)",
        "prices": {t: round(rows[-1][1], 4) for t, rows in history.items()}})

    out = {}
    for r in h["investors"]:
        res = track.compute_track(r["snapshots"], history, BENCH)
        if res:
            out[r["id"]] = res
    write_pair("track", "PROTEGE_TRACK", {
        "sample": False, "asof": asof, "benchmark": BENCH,
        "params": {"top": track.TOP_N, "cap": track.CAP},
        "method": "Copied on each filing date: top priced positions, capped, rebalanced at each new filing. Price return, no fees or tax.",
        "investors": out})
    print(f"Track records for {len(out)} investors, as of {asof}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
