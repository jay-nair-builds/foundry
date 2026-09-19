#!/usr/bin/env python3
"""Generate Atom feeds so users get new-filing alerts in any feed reader or RSS-to-email service.

Writes feeds/all.xml (latest filing per investor) and feeds/<id>.xml (recent filings of one investor).
Env SITE_URL sets the public base URL (default: the GitHub Pages address).
"""
import os
from xml.sax.saxutils import escape

from common import ROOT, read_json

SITE = os.environ.get("SITE_URL", "https://jay-nair-builds.github.io/foundry/apps/protege/").rstrip("/") + "/"


def diff(cur, prev):
    """Classify positions vs the prior filing. A >5% change in shares counts as added or trimmed."""
    if not prev:
        return None
    pm = {(p["name"] + "|" + p["cls"]).lower(): p for p in prev["positions"]}
    seen, out = set(), {"new": [], "added": [], "trimmed": [], "exited": []}
    for p in cur["positions"]:
        k = (p["name"] + "|" + p["cls"]).lower()
        seen.add(k)
        o = pm.get(k)
        if not o:
            out["new"].append(p)
        elif o["shares"]:
            ch = (p["shares"] - o["shares"]) / o["shares"]
            if ch > 0.05:
                out["added"].append(p)
            elif ch < -0.05:
                out["trimmed"].append(p)
    out["exited"] = [p for k, p in pm.items() if k not in seen]
    return out


def label(p):
    return p["ticker"] or p["name"]


def summary(inv_name, snap, prev):
    d = diff(snap, prev)
    head = f"{inv_name} filed a 13F-HR for the period ending {snap['period']} ({snap['count']} positions)."
    if not d:
        return head
    bits = []
    for key, title in (("new", "New"), ("added", "Added"), ("trimmed", "Trimmed"), ("exited", "Exited")):
        if d[key]:
            bits.append(f"{title} ({len(d[key])}): " + ", ".join(label(p) for p in d[key][:6]))
    return head + " " + " | ".join(bits)


def entry(inv, snap, prev):
    ident = f"tag:protege,2026:{inv['id']}:{snap['accession']}"
    return (
        "<entry>"
        f"<id>{escape(ident)}</id>"
        f"<title>{escape(inv['name'])}: new 13F for {escape(snap['period'])}</title>"
        f"<link href=\"{escape(SITE)}#{escape(inv['id'])}\"/>"
        f"<updated>{escape(snap['filed'])}T12:00:00Z</updated>"
        f"<summary>{escape(summary(inv['name'], snap, prev))}</summary>"
        "</entry>"
    )


def feed(title, feed_id, self_href, entries, updated):
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n<feed xmlns="http://www.w3.org/2005/Atom">'
        f"<title>{escape(title)}</title><id>{escape(feed_id)}</id>"
        f'<link rel="self" href="{escape(self_href)}"/><link href="{escape(SITE)}"/>'
        f"<updated>{escape(updated)}T12:00:00Z</updated>" + "".join(entries) + "</feed>\n"
    )


def main():
    h = read_json("holdings.json")
    if not h or h.get("sample"):
        print("Holdings are sample data; no feeds written.")
        return
    roster = {i["id"]: i for i in read_json("investors.json")}
    out = ROOT / "feeds"
    out.mkdir(exist_ok=True)
    latest = []
    for r in h["investors"]:
        inv = roster.get(r["id"])
        if not inv or not r["snapshots"]:
            continue
        snaps = r["snapshots"]
        ents = [entry(inv, s, snaps[i + 1] if i + 1 < len(snaps) else None) for i, s in enumerate(snaps[:6])]
        (out / f"{inv['id']}.xml").write_text(feed(f"Protégé: {inv['name']}", f"tag:protege,2026:{inv['id']}", f"{SITE}feeds/{inv['id']}.xml", ents, snaps[0]["filed"]))
        latest.append((snaps[0]["filed"], entry(inv, snaps[0], snaps[1] if len(snaps) > 1 else None)))
    latest.sort(reverse=True)
    if latest:
        (out / "all.xml").write_text(feed("Protégé: new 13F filings", "tag:protege,2026:all", f"{SITE}feeds/all.xml", [e for _, e in latest[:60]], latest[0][0]))
    print(f"Wrote {len(latest) + 1} feeds")


if __name__ == "__main__":
    main()
