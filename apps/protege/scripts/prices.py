"""Daily price history from free public endpoints (Stooq first, Yahoo Finance chart API as fallback).

Both are unofficial, keyless sources: fine for a hobby data pipeline, not for anything commercial.
Prices are split-adjusted closes, dividends excluded.
"""
import json
import time
from datetime import datetime, timezone

from sec import http_get

UA_DEFAULT = "Protege data pipeline (github.com/jay-nair-builds/foundry)"


def stooq_symbol(ticker):
    return ticker.lower().replace(".", "-").replace("/", "-") + ".us"


def parse_stooq_csv(text):
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    if not lines or not lines[0].lower().startswith("date,"):
        return []
    out = []
    for l in lines[1:]:
        parts = l.split(",")
        try:
            out.append((parts[0], float(parts[4])))
        except (IndexError, ValueError):
            continue
    return sorted(out)


def parse_yahoo_json(obj):
    try:
        r = obj["chart"]["result"][0]
        ts, closes = r["timestamp"], r["indicators"]["quote"][0]["close"]
    except (KeyError, IndexError, TypeError):
        return []
    out = []
    for t, c in zip(ts, closes):
        if c is not None:
            out.append((datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%d"), float(c)))
    return sorted(out)


def fetch_history(ticker, start, end, get=http_get, ua=UA_DEFAULT):
    """start/end are ISO dates. Returns [(date, close)] ascending, or [] when no source has the ticker."""
    d1, d2 = start.replace("-", ""), end.replace("-", "")
    try:
        rows = parse_stooq_csv(get(f"https://stooq.com/q/d/l/?s={stooq_symbol(ticker)}&i=d&d1={d1}&d2={d2}", ua).decode("utf-8", "replace"))
        if len(rows) >= 20:
            return rows
    except Exception:
        pass
    try:
        p1 = int(datetime.fromisoformat(start).replace(tzinfo=timezone.utc).timestamp())
        p2 = int(datetime.fromisoformat(end).replace(tzinfo=timezone.utc).timestamp()) + 86400
        sym = ticker.replace(".", "-")
        raw = get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?period1={p1}&period2={p2}&interval=1d", ua)
        rows = parse_yahoo_json(json.loads(raw))
        return rows if len(rows) >= 20 else []
    except Exception:
        return []
