#!/usr/bin/env python3
"""Refresh Protégé holdings from SEC EDGAR.

For each investor in data/investors.json, pulls up to N recent 13F-HR filings, aggregates positions,
maps CUSIPs to tickers with OpenFIGI, and writes data/holdings.json, data/holdings.js, data/investors.js.

Usage:
    python3 scripts/fetch_13f.py --ua "Your Name you@example.com" [--only buffett,ackman] [--quarters 9]

SEC requires a User-Agent with contact details. Python 3.9+, standard library only.
Source: SEC EDGAR, https://www.sec.gov/edgar
"""
import argparse
import sys
from datetime import datetime, timezone

import figi
import sec
from common import read_json, write_js, write_json, write_pair


def build(inv, ua, quarters, max_positions):
    entity, filings = sec.latest_filings(inv["cik"], ua, quarters)
    if not filings:
        raise RuntimeError("no 13F-HR filings found")
    snaps = []
    for i, f in enumerate(filings):
        rows = sec.info_table_rows(inv["cik"], f["accession"], ua)
        # Older filings only feed track records (top 10), so keep them lean to limit page weight.
        total, count, positions = sec.aggregate(rows, max_positions if i < 3 else min(25, max_positions))
        snaps.append({**f, "total": round(total), "count": count, "positions": positions})
    return {"id": inv["id"], "entity": entity, "snapshots": snaps}


def apply_tickers(results, cache):
    cusips = {p["cusip"] for r in results for s in r["snapshots"] for p in s["positions"]}
    figi.map_cusips(cusips, cache)
    for r in results:
        for s in r["snapshots"]:
            for p in s["positions"]:
                hit = cache.get(p["cusip"]) or {}
                p["ticker"] = hit.get("ticker") or sec.name_ticker(p["name"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ua", required=True, help='e.g. "Jane Doe jane@example.com"')
    ap.add_argument("--only", help="comma-separated investor ids to refresh")
    ap.add_argument("--quarters", type=int, default=9)
    ap.add_argument("--max-positions", type=int, default=60)
    args = ap.parse_args()

    investors = read_json("investors.json")
    only = set(args.only.split(",")) if args.only else None
    results, failed = [], []
    for inv in investors:
        if only and inv["id"] not in only:
            continue
        try:
            res = build(inv, args.ua, args.quarters, args.max_positions)
            s0 = res["snapshots"][0]
            print(f"ok   {inv['id']:<16} {res['entity']}  ({s0['count']} positions, period {s0['period']}, {len(res['snapshots'])} filings)")
            results.append(res)
        except Exception as e:  # one bad filer must not sink the refresh
            print(f"FAIL {inv['id']:<16} {e}", file=sys.stderr)
            failed.append(inv["id"])
    if not results:
        sys.exit("No data fetched; leaving existing files untouched.")

    cache = read_json("cusips.json", {})
    apply_tickers(results, cache)
    write_json("cusips.json", cache)

    if only:
        old = read_json("holdings.json", {"investors": []})
        if old.get("sample"):
            old = {"investors": []}  # never mix real filings into the sample set
        fresh = {r["id"] for r in results}
        results = [r for r in old.get("investors", []) if r["id"] not in fresh] + results
    order = {inv["id"]: i for i, inv in enumerate(investors)}
    results.sort(key=lambda r: order.get(r["id"], 999))

    write_pair("holdings", "PROTEGE_HOLDINGS", {
        "sample": False, "source": "SEC EDGAR Form 13F-HR",
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d"), "investors": results})
    write_js("investors", "PROTEGE_INVESTORS", investors)
    print(f"Wrote {len(results)} investors. Failed: {failed or 'none'}")
    if failed and len(failed) == len(investors if not only else only):
        sys.exit(1)


if __name__ == "__main__":
    main()
