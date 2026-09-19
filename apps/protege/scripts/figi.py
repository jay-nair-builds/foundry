"""CUSIP to ticker mapping via OpenFIGI (https://www.openfigi.com/api).

Free tier: 25 requests/minute, 10 identifiers per request. With an API key
(env OPENFIGI_API_KEY): 25 requests per 6 seconds, 100 identifiers per request.
Results are cached in data/cusips.json so each CUSIP is looked up once.
"""
import json
import os
import time
import urllib.request

URL = "https://api.openfigi.com/v3/mapping"
PREFERRED = ("Common Stock", "ETP", "REIT", "Depositary Receipt", "Closed-End Fund", "MLP")


def _post(payload, api_key):
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["X-OPENFIGI-APIKEY"] = api_key
    req = urllib.request.Request(URL, data=json.dumps(payload).encode(), headers=headers)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def pick(results):
    """Choose the best listing from an OpenFIGI result list: US-listed, preferred security type."""
    for want in PREFERRED:
        for d in results:
            if d.get("securityType2") == want or d.get("securityType") == want:
                if d.get("ticker"):
                    return {"ticker": d["ticker"], "name": d.get("name", "")}
    for d in results:
        if d.get("ticker"):
            return {"ticker": d["ticker"], "name": d.get("name", "")}
    return None


def map_cusips(cusips, cache, api_key=None, post=_post, sleep=time.sleep):
    """Fill `cache` (cusip -> {ticker, name} or {}) for any CUSIPs not already present."""
    api_key = api_key or os.environ.get("OPENFIGI_API_KEY")
    need = sorted({c for c in cusips if c and c not in cache})
    size, pause = (100, 0.3) if api_key else (10, 2.6)
    for i in range(0, len(need), size):
        batch = need[i:i + size]
        payload = [{"idType": "ID_CUSIP", "idValue": c, "exchCode": "US"} for c in batch]
        try:
            resp = post(payload, api_key)
        except Exception as e:  # network or rate limit: leave uncached, retry on the next run
            print(f"OpenFIGI batch failed ({e}); {len(batch)} CUSIPs left unmapped")
            continue
        for c, item in zip(batch, resp):
            cache[c] = pick(item.get("data", [])) or {}
        sleep(pause)
    return cache
