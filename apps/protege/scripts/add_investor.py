#!/usr/bin/env python3
"""Add an investor to data/investors.json from a GitHub issue created by the 'add investor' form.

Reads the raw issue body from env ISSUE_BODY (never from the command line) and writes
result.json for the workflow to post back on the issue. Exit code is always 0 unless something
unexpected breaks; the status field says what happened.

status: added | exists | ambiguous | invalid | not_found | full
"""
import json
import os
import re
import sys
import urllib.parse
from pathlib import Path

import sec
from common import DATA, read_json

MAX_ROSTER = 100
NAME_OK = re.compile(r"^[A-Za-z0-9 .,&'()\-]{2,100}$")


def section(body, heading):
    m = re.search(r"###\s*" + re.escape(heading) + r"\s*\n+(.*?)(?=\n###|\Z)", body, re.S)
    if not m:
        return ""
    lines = [l.strip() for l in m.group(1).splitlines() if l.strip()]
    return lines[0] if lines else ""


def slug(name):
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return re.sub(r"-(inc|llc|lp|ltd|corp|co|capital|management|partners)$", "", s)[:32] or "investor"


def search_candidates(query, ua, get=sec.http_get):
    """Find 13F filers by name using EDGAR full-text search. Returns [(name, cik10)] best first."""
    url = "https://efts.sec.gov/LATEST/search-index?q=" + urllib.parse.quote(f'"{query}"') + "&forms=13F-HR"
    data = json.loads(get(url, ua))
    seen, out = set(), []
    for hit in data.get("hits", {}).get("hits", []):
        for disp in hit.get("_source", {}).get("display_names", []):
            m = re.match(r"^(.*?)\s+\(CIK (\d+)\)", disp)
            if m and m.group(2) not in seen:
                seen.add(m.group(2))
                out.append((m.group(1).strip(), m.group(2).zfill(10)))
    q = query.lower()
    out.sort(key=lambda c: (c[0].lower() != q, q not in c[0].lower(), len(c[0])))
    return out


def run(body, ua, get=sec.http_get, roster_path=None):
    roster_path = Path(roster_path or DATA / "investors.json")
    roster = json.loads(roster_path.read_text())
    raw = section(body, "Fund name or CIK")
    if not raw and body.strip() and "###" not in body:
        raw = body.strip().splitlines()[0].strip()
    if not NAME_OK.match(raw):
        return {"status": "invalid", "message": "Please give a fund name (letters, numbers and basic punctuation) or a numeric CIK."}
    if len(roster) >= MAX_ROSTER:
        return {"status": "full", "message": f"The roster is capped at {MAX_ROSTER} investors."}

    if re.fullmatch(r"\d{1,10}", raw):
        cik = raw.zfill(10)
    else:
        cands = search_candidates(raw, ua, get)
        if not cands:
            return {"status": "not_found", "message": f"No 13F filer found for \"{raw}\". Try the exact legal name or the numeric CIK from sec.gov."}
        exact = [c for c in cands if c[0].lower() == raw.lower()]
        if len(exact) == 1 or len(cands) == 1:
            cik = (exact or cands)[0][1]
        else:
            lines = "\n".join(f"- {n} (CIK {c})" for n, c in cands[:8])
            return {"status": "ambiguous", "message": "Several filers match. Open a new request with the CIK of the right one:\n" + lines}

    for r in roster:
        if r["cik"] == cik:
            return {"status": "exists", "id": r["id"], "message": f"{r['name']} is already tracked."}
    try:
        entity, filings = sec.latest_filings(cik, ua, 1, get)
    except Exception as e:
        return {"status": "not_found", "message": f"Could not read SEC filings for CIK {cik}: {type(e).__name__}."}
    if not filings:
        return {"status": "not_found", "message": f"{entity} has no 13F-HR filings, so there is nothing to mimic."}

    name = entity.title()
    base = slug(name)
    ids = {r["id"] for r in roster}
    iid, n = base, 2
    while iid in ids:
        iid, n = f"{base}-{n}", n + 1
    roster.append({"id": iid, "name": name, "fund": "Added by request", "cik": cik, "style": "Community pick",
                   "tags": ["Community"], "blurb": "Added on request from a public 13F filer. Style not yet classified."})
    roster_path.write_text(json.dumps(roster, indent=1, ensure_ascii=False) + "\n")
    return {"status": "added", "id": iid, "name": name, "cik": cik, "message": f"Added {name} (CIK {cik})."}


def main():
    ua = os.environ.get("SEC_USER_AGENT", "").strip()
    if not ua:
        sys.exit("SEC_USER_AGENT is not set")
    result = run(os.environ.get("ISSUE_BODY", ""), ua)
    Path("result.json").write_text(json.dumps(result))
    # Comment text for the workflow. SEC-sourced names are untrusted: defuse @mentions.
    msg = result["message"].replace("@", "@​")
    tail = {"added": "\n\nHistory and prices are loading; the site rebuilds in a few minutes.",
            "exists": "", "ambiguous": "", "invalid": "", "not_found": "", "full": ""}.get(result["status"], "")
    Path("comment.md").write_text(msg + tail + "\n")
    print(result["status"], "-", result["message"].splitlines()[0])


if __name__ == "__main__":
    main()
