"""Valuation engine (Damodaran-style build) shared by the Excel model and the web page."""
RF, ERP, KD, TAX = 0.0494, 0.045, 0.0575, 0.15
BLUME_W = 0.67
G_FADE, G_TERM = 0.03, 0.03
WACC_FLOOR, WACC_CAP = 0.08, 0.11
WACC_STEP = 0.0075
TG_GRID = [0.02, 0.025, 0.03, 0.035, 0.04]

CO = {
 "NVDA": dict(name="NVIDIA", price=222.27, mcap=5370.0, cash=62.47, debt=38.86, beta=2.22, ttm=302.97,
   sc={"Bear": dict(r1=400, g=[.05, -.10, .00, .03], m=(.55, .45), cv=(.75, .75)),
       "Base": dict(r1=450, g=[.25, .18, .12, .08], m=(.62, .55), cv=(.75, .80)),
       "Bull": dict(r1=500, g=[.35, .25, .18, .12], m=(.65, .62), cv=(.75, .85))}),
 "META": dict(name="Meta Platforms", price=665.75, mcap=1700.0, cash=90.26, debt=112.32, beta=1.24, ttm=228.25,
   sc={"Bear": dict(r1=255, g=[.06, .04, .03, .03], m=(.30, .28), cv=(.45, .60)),
       "Base": dict(r1=268, g=[.14, .11, .09, .08], m=(.34, .36), cv=(.55, .75)),
       "Bull": dict(r1=280, g=[.18, .15, .12, .10], m=(.38, .42), cv=(.60, .85))}),
}

def wacc_parts(c):
    adj = BLUME_W * c["beta"] + (1 - BLUME_W) * 1.0
    coe = RF + adj * ERP
    e, d = c["mcap"], c["debt"]
    calc = (e * coe + d * KD * (1 - TAX)) / (e + d)
    used = min(max(calc, WACC_FLOOR), WACC_CAP)
    return dict(adj=adj, coe=coe, we=e / (e + d), wd=d / (e + d), calc=calc, used=used)

def project(s, gscale=1.0):
    g = [x * gscale for x in s["g"]]
    rev = [s["r1"]]
    for x in g:
        rev.append(rev[-1] * (1 + x))
    g_path = [None] + g
    g5 = g[-1]
    for i in range(1, 6):
        gi = g5 + (G_FADE - g5) * i / 5
        g_path.append(gi)
        rev.append(rev[-1] * (1 + gi))
    rows = []
    for t in range(10):
        k = min(t, 4) / 4
        m = s["m"][0] + (s["m"][1] - s["m"][0]) * k
        cv = s["cv"][0] + (s["cv"][1] - s["cv"][0]) * k
        fcff = rev[t] * m * (1 - TAX) * cv
        rows.append(dict(rev=rev[t], g=g_path[t], m=m, cv=cv, fcff=fcff))
    return rows

def value(c, s, wacc, tg=G_TERM, gscale=1.0):
    rows = project(s, gscale)
    pv = sum(r["fcff"] / (1 + wacc) ** (t + 1) for t, r in enumerate(rows))
    tv = rows[-1]["fcff"] * (1 + tg) / (wacc - tg)
    pvtv = tv / (1 + wacc) ** 10
    ev = pv + pvtv
    eq = ev + c["cash"] - c["debt"]
    shares = c["mcap"] / c["price"]
    return dict(rows=rows, pv=pv, tv=tv, pvtv=pvtv, ev=ev, eq=eq, ps=eq / shares, shares=shares,
                tv_share=pvtv / ev)

def run(key):
    c = CO[key]
    w = wacc_parts(c)
    out = dict(wacc=w, scen={}, shares=c["mcap"] / c["price"])
    for n, s in c["sc"].items():
        out["scen"][n] = value(c, s, w["used"])
    base = c["sc"]["Base"]
    lo, hi = -3.0, 6.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if value(c, base, w["used"], gscale=mid)["ps"] < c["price"]:
            lo = mid
        else:
            hi = mid
    gs = (lo + hi) / 2
    out["gscale"] = gs
    out["scen"]["Implied"] = value(c, base, w["used"], gscale=gs)
    waccs = [w["used"] + WACC_STEP * k for k in (-2, -1, 0, 1, 2)]
    out["sens"] = dict(waccs=waccs, tgs=TG_GRID,
                       grid=[[value(c, base, ww, tg=t)["ps"] for t in TG_GRID] for ww in waccs])
    def cagr(v):
        return (v["rows"][4]["rev"] / c["ttm"]) ** 0.2 - 1
    out["cagr"] = dict(base=cagr(out["scen"]["Base"]), implied=cagr(out["scen"]["Implied"]),
                       base_rev5=out["scen"]["Base"]["rows"][4]["rev"],
                       implied_rev5=out["scen"]["Implied"]["rows"][4]["rev"])
    return out

if __name__ == "__main__":
    for k in CO:
        r = run(k)
        print(k, {a: round(b, 4) for a, b in r["wacc"].items()}, "gscale", round(r["gscale"], 3))
        for n, v in r["scen"].items():
            print("  ", n, round(v["ps"], 2), "TV share", round(v["tv_share"], 3))
        print("   cagr", {a: round(b, 3) for a, b in r["cagr"].items()})
        for row in r["sens"]["grid"]:
            print("   ", [round(x) for x in row])
