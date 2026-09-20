"""SEC EDGAR helpers: fetching 13F-HR filings and parsing their information tables.

Standard library only. SEC fair-access rules: descriptive User-Agent with contact details,
at most 10 requests per second (this module stays near 4).
"""
import json
import re
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

# Issuer-name fragments to tickers, used only when OpenFIGI mapping is unavailable.
TICKERS = {
    "APPLE INC": "AAPL", "AMERICAN EXPRESS": "AXP", "BANK OF AMERICA": "BAC", "COCA COLA CO": "KO",
    "CHEVRON": "CVX", "OCCIDENTAL PETE": "OXY", "MOODYS": "MCO", "KRAFT HEINZ": "KHC",
    "ALPHABET INC": "GOOGL", "AMAZON COM": "AMZN", "MICROSOFT": "MSFT", "NVIDIA": "NVDA",
    "META PLATFORMS": "META", "BROOKFIELD": "BN", "UNIVERSAL MUSIC": "UMG", "HILTON WORLDWIDE": "HLT",
    "RESTAURANT BRANDS": "QSR", "CHIPOTLE": "CMG", "HOWARD HUGHES": "HHH", "LOWES": "LOW",
    "FANNIE MAE": "FNMA", "FEDERAL NATL MTG": "FNMA", "VISA INC": "V", "MASTERCARD": "MA",
    "TESLA": "TSLA", "NETFLIX": "NFLX", "JPMORGAN": "JPM", "ELI LILLY": "LLY", "UNITEDHEALTH": "UNH",
    "CONSTELLATION BRANDS": "STZ", "DAVITA": "DVA", "SIRIUSXM": "SIRI", "SIRIUS XM": "SIRI",
    "PROCTER & GAMBLE": "PG", "JOHNSON & JOHNSON": "JNJ", "WELLS FARGO": "WFC",
}


def http_get(url, ua, retries=4):
    """GET with retry and polite pacing. Returns bytes."""
    delay = 1.0
    for attempt in range(retries):
        req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept-Encoding": "identity"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                body = r.read()
            time.sleep(0.25)
            return body
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < retries - 1:
                time.sleep(delay)
                delay *= 2
                continue
            raise
        except urllib.error.URLError:
            if attempt < retries - 1:
                time.sleep(delay)
                delay *= 2
                continue
            raise


def latest_filings(cik, ua, n=9, get=http_get):
    """Return (entity name, [{accession, filed, period}, ...]) newest first, 13F-HR only."""
    sub = json.loads(get(f"https://data.sec.gov/submissions/CIK{cik}.json", ua))
    rec = sub["filings"]["recent"]
    out = []
    for i, form in enumerate(rec["form"]):
        if form == "13F-HR":
            out.append({"accession": rec["accessionNumber"][i], "filed": rec["filingDate"][i], "period": rec["reportDate"][i]})
        if len(out) == n:
            break
    return sub["name"], out


def info_table_rows(cik, accession, ua, get=http_get):
    base = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession.replace('-', '')}/"
    index = json.loads(get(base + "index.json", ua))
    names = [f["name"] for f in index["directory"]["item"] if f["name"].lower().endswith(".xml")]
    for name in [n for n in names if "primary_doc" not in n.lower()]:
        rows = parse_info_table(get(base + name, ua))
        if rows:
            return rows
    raise RuntimeError(f"No information table found for {accession}")


def _local(tag):
    return tag.rsplit("}", 1)[-1]


def _find(el, tag):
    for c in el.iter():
        if _local(c.tag) == tag:
            return (c.text or "").strip()
    return ""


def parse_info_table(xml_bytes):
    """Parse an information table into plain dicts. Skips options and bond principal lines."""
    root = ET.fromstring(xml_bytes)
    rows = []
    for e in root.iter():
        if _local(e.tag) != "infoTable":
            continue
        if _find(e, "putCall") or _find(e, "sshPrnamtType").upper() == "PRN":
            continue
        rows.append({
            "name": _find(e, "nameOfIssuer"), "cls": _find(e, "titleOfClass"), "cusip": _find(e, "cusip"),
            "value": float(_find(e, "value") or 0), "shares": float(_find(e, "sshPrnamt") or 0),
        })
    return rows


def value_scale(rows):
    """Return 1000 if the filing reports <value> in thousands of dollars, else 1.

    Since 2023 the SEC asks for whole dollars, but some filers still report thousands. Real equity
    prices rarely sit below $1, so a median value per share under $1 means the values are in thousands.
    """
    prices = sorted(r["value"] / r["shares"] for r in rows if r["shares"] > 0 and r["value"] > 0)
    if not prices:
        return 1
    return 1000 if prices[len(prices) // 2] < 1.0 else 1


def aggregate(rows, max_positions=60):
    """Combine lines per security, compute weights against the full portfolio, keep the top N."""
    scale = value_scale(rows)
    rows = [{**r, "value": r["value"] * scale} for r in rows]
    pos = {}
    for r in rows:
        key = r["cusip"] or f"{r['name']}|{r['cls']}"
        p = pos.setdefault(key, {"name": r["name"].title(), "cls": r["cls"], "cusip": r["cusip"], "value": 0.0, "shares": 0.0})
        p["value"] += r["value"]
        p["shares"] += r["shares"]
    total = sum(p["value"] for p in pos.values())
    ranked = sorted(pos.values(), key=lambda p: -p["value"])
    out = [{"name": p["name"], "cls": p["cls"], "cusip": p["cusip"], "ticker": "",
            "value": round(p["value"]), "shares": round(p["shares"]),
            "weight": round(p["value"] / total, 6) if total else 0.0} for p in ranked[:max_positions]]
    return total, len(ranked), out


def name_ticker(name):
    up = re.sub(r"[.,]", "", name.upper())
    for frag, t in TICKERS.items():
        if frag in up:
            return t
    return ""
