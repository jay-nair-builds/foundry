"""Track-record engine: how a mimic portfolio would have performed if copied on each filing date.

Method (deliberately simple and disclosed in the app):
  * On the day each 13F-HR is filed (public), move to the investor's top N priced positions,
    rescaled to 100% with a per-position cap. Hold until the next filing, then rebalance.
  * This includes the 45-day reporting lag, so it is what a follower could actually have done.
  * Benchmark: SPY bought on the first rebalance date and held.
  * Price return only (split-adjusted, dividends excluded), no fees, tax or slippage.
"""
from bisect import bisect_right

TOP_N = 10
CAP = 0.25


def mimic_weights(weights, cap=CAP):
    """Rescale weights to 100%, capping each at `cap` (never below 1/n) and redistributing the excess."""
    n = len(weights)
    if not n:
        return []
    cap = max(cap, 1.0 / n)
    tot = sum(weights) or 1.0
    w = [x / tot for x in weights]
    fixed = [False] * n
    for _ in range(25):
        over = False
        for i, x in enumerate(w):
            if x > cap + 1e-12:
                w[i], fixed[i], over = cap, True, True
        if not over:
            break
        fixed_sum = sum(x for i, x in enumerate(w) if fixed[i])
        free_sum = sum(x for i, x in enumerate(w) if not fixed[i]) or 1.0
        w = [x if fixed[i] else x / free_sum * (1 - fixed_sum) for i, x in enumerate(w)]
    return w


class Prices:
    """Close lookup with forward fill. history: {ticker: [(date, close), ...]} ascending by ISO date."""

    def __init__(self, history):
        self.d = {t: ([x[0] for x in h], [x[1] for x in h]) for t, h in history.items() if h}

    def has(self, t):
        return t in self.d

    def at(self, t, date):
        if t not in self.d:
            return None
        dates, closes = self.d[t]
        i = bisect_right(dates, date) - 1
        return closes[i] if i >= 0 else None


def _max_drawdown(values):
    peak, worst = values[0], 0.0
    for v in values:
        peak = max(peak, v)
        worst = min(worst, v / peak - 1)
    return worst


def compute_track(snapshots, history, benchmark="SPY", top_n=TOP_N, cap=CAP, max_points=260):
    """Return {series: [[date, portfolio, benchmark], ...], stats: {...}} or None if not computable."""
    px = Prices(history)
    if not px.has(benchmark):
        return None
    calendar = px.d[benchmark][0]
    snaps = sorted((s for s in snapshots if s["filed"] <= calendar[-1]), key=lambda s: s["filed"])
    snaps = [s for s in snaps if s["filed"] >= calendar[0]]
    if not snaps:
        return None

    def reb_date(filed):
        i = bisect_right(calendar, filed) - 1
        return calendar[i] if calendar[i] >= filed else calendar[min(i + 1, len(calendar) - 1)]

    starts = []
    for s in snaps:
        d = reb_date(s["filed"])
        if not starts or d > starts[-1][0]:
            starts.append((d, s))
    start = starts[0][0]
    days = [d for d in calendar if d >= start]

    value, holdings, cover, si = 100.0, {}, [], 0
    b0 = px.at(benchmark, start)
    series = []
    for d in days:
        if si < len(starts) and starts[si][0] == d:
            if holdings:  # mark to market before rebalancing
                value = sum(sh * (px.at(t, d) or 0) for t, sh in holdings.items()) or value
            snap = starts[si][1]
            ranked = [p for p in snap["positions"] if p.get("ticker")]
            top_all = ranked[:top_n]
            priced = [p for p in ranked if px.at(p["ticker"], d) is not None][:top_n]
            if priced:
                w = mimic_weights([p["weight"] for p in priced], cap)
                holdings = {p["ticker"]: value * wi / px.at(p["ticker"], d) for p, wi in zip(priced, w)}
                denom = sum(p["weight"] for p in top_all) or 1.0
                cover.append(sum(p["weight"] for p in priced if p in top_all) / denom)
            si += 1
        if holdings:
            pv = sum(sh * (px.at(t, d) or 0) for t, sh in holdings.items())
            if pv <= 0:
                continue
            value = pv
        series.append([d, round(value, 4), round(100.0 * px.at(benchmark, d) / b0, 4)])
    if len(series) < 2:
        return None

    vals, bench = [x[1] for x in series], [x[2] for x in series]
    from datetime import date
    y0, y1 = date.fromisoformat(series[0][0]), date.fromisoformat(series[-1][0])
    years = (y1 - y0).days / 365.25
    stats = {
        "start": series[0][0], "end": series[-1][0], "years": round(years, 2), "rebalances": len(starts),
        "return": round(vals[-1] / 100 - 1, 4), "benchmarkReturn": round(bench[-1] / 100 - 1, 4),
        "maxDrawdown": round(_max_drawdown(vals), 4), "benchmarkMaxDrawdown": round(_max_drawdown(bench), 4),
        "coverage": round(sum(cover) / len(cover), 3) if cover else 0.0,
    }
    if years >= 1:
        stats["cagr"] = round((vals[-1] / 100) ** (1 / years) - 1, 4)
        stats["benchmarkCagr"] = round((bench[-1] / 100) ** (1 / years) - 1, 4)
    step = max(1, len(series) // max_points)
    thin = series[::step]
    if thin[-1] != series[-1]:
        thin.append(series[-1])
    return {"series": thin, "stats": stats}
