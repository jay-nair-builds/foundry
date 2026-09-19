"""Shared paths and data file helpers."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def read_json(name, default=None):
    p = DATA / name
    return json.loads(p.read_text()) if p.exists() else default


def _dump(payload):
    return json.dumps(payload, separators=(",", ":"), ensure_ascii=False)


def write_json(name, payload, pretty=False):
    text = json.dumps(payload, indent=1, ensure_ascii=False) if pretty else _dump(payload)
    (DATA / name).write_text(text + "\n")


def write_js(stem, var, payload):
    (DATA / f"{stem}.js").write_text(f"window.{var} = {_dump(payload)};\n")


def write_pair(stem, var, payload):
    """Write data/<stem>.json and data/<stem>.js so the app also works when opened from disk."""
    write_json(f"{stem}.json", payload)
    write_js(stem, var, payload)
