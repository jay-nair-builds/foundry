"""Historical P&L data (USD millions, as reported) and forward P&L assumptions.
Sources: NVIDIA and Meta earnings releases (fiscal-year results), StockAnalysis.com (TTM). See notes in the workbook."""
import engine as E

HIST = {
 "NVDA": dict(
   name="Nvidia", fy_note="Fiscal years end late January (FY2026 = year ended 25 Jan 2026).",
   labels=["FY2017", "FY2018", "FY2019", "FY2020", "FY2021", "FY2022", "FY2023", "FY2024", "FY2025", "FY2026"],
   ends=["Jan-17", "Jan-18", "Jan-19", "Jan-20", "Jan-21", "Jan-22", "Jan-23", "Jan-24", "Jan-25", "Jan-26"],
   short=["FY17", "FY18", "FY19", "FY20", "FY21", "FY22", "FY23", "FY24", "FY25", "FY26"],
   rev=[6910, 9714, 11716, 10918, 16675, 26914, 26974, 60922, 130497, 215938],
   cogs=[2847, 3892, 4545, 4150, 6279, 9439, 11618, 16621, 32639, 62475],
   rd=[1466, 1797, 2376, 2829, 3924, 5268, 7339, 8675, 12914, 18497],
   sga=[663, 815, 991, 1093, 1940, 2166, 2440, 2654, 3491, 4579],
   other_op=[0, 0, 0, 0, 0, 0, 1353, 0, 0, 0],
   ebit_rep=[1934, 3210, 3804, 2846, 4532, 10041, 4224, 32972, 81453, 130387],
   int_other=[-29, -14, 92, 124, -123, -100, -43, 846, 2573, 11063],
   tax=[239, 149, -245, 174, 77, 189, -187, 4058, 11146, 21383],
   ni_rep=[1666, 3047, 4141, 2796, 4332, 9752, 4368, 29760, 72880, 120067],
   shares=[25960, 25280, 25000, 24720, 25100, 25350, 25070, 24940, 24804, 24514],
   capex=[176, 593, 600, 489, 1128, 976, 1833, 1069, 3236, 6042],
   fcf=[1496, 2909, 3143, 4272, 4694, 8132, 3808, 27021, 60853, 96676],
   ltm=dict(label="TTM Jul-26", rev=302970, gp=226241, ebit=197579, ni=192880, eps=7.91, fcf=127006),
   notes={
     "other_op": "FY2023: $1,353M cost of the terminated Arm acquisition.",
     "int_other": "Interest income less interest expense plus other, net. FY2026 includes $9,022M of other income (gains on investments).",
     "shares": "Diluted shares in millions, adjusted for the 4-for-1 (Jul 2021) and 10-for-1 (Jun 2024) stock splits, so EPS is comparable across years.",
     "capex": "Purchases of property, equipment and intangibles.",
     "fcf": "Operating cash flow minus capex.",
   }),
 "META": dict(
   name="Meta", fy_note="Fiscal years end 31 December.",
   labels=["FY2016", "FY2017", "FY2018", "FY2019", "FY2020", "FY2021", "FY2022", "FY2023", "FY2024", "FY2025"],
   ends=["Dec-16", "Dec-17", "Dec-18", "Dec-19", "Dec-20", "Dec-21", "Dec-22", "Dec-23", "Dec-24", "Dec-25"],
   short=["FY16", "FY17", "FY18", "FY19", "FY20", "FY21", "FY22", "FY23", "FY24", "FY25"],
   rev=[27638, 40653, 55838, 70697, 85965, 117929, 116609, 134902, 164501, 200966],
   cogs=[3789, 5454, 9355, 12770, 16692, 22649, 25249, 25959, 30161, 36175],
   rd=[5919, 7754, 10273, 13600, 18447, 24655, 35338, 38483, 43873, 57372],
   sga=[3772 + 1731, 4725 + 2517, 7846 + 3451, 9876 + 10465, 11591 + 6564, 14043 + 9829, 15262 + 11816, 12301 + 11408, 11347 + 9740, 11991 + 12152],
   other_op=[0] * 10,
   ebit_rep=[12427, 20203, 24913, 23986, 32671, 46753, 28944, 46751, 69380, 83276],
   int_other=[91, 391, 448, 826, 509, 531, -125, 677, 1283, 2656],
   tax=[2301, 4660, 3249, 6327, 4034, 7914, 5619, 8330, 8303, 25474],
   ni_rep=[10217, 15934, 22112, 18485, 29146, 39370, 23200, 39098, 62360, 60458],
   shares=[2925, 2956, 2921, 2876, 2888, 2859, 2702, 2629, 2614, 2574],
   capex=[4491, 6733, 13915, 15650, 15115, 19240, 31431, 28100, 37256, 72220],
   fcf=[11617, 17483, 15359, 20656, 23028, 38439, 18439, 43010, 52103, 43585],
   ltm=dict(label="TTM Jun-26", rev=228247, gp=186586, ebit=86926, ni=68098, eps=26.54, fcf=41070),
   notes={
     "sga": "Marketing and sales plus general and administrative. 2019 includes a $5.0B FTC settlement accrual; 2022 includes about $4.6B of restructuring charges (spread across cost lines).",
     "int_other": "Interest and other income, net.",
     "tax": "Effective tax rate was 11.8% in 2024 and 29.6% in 2025.",
     "capex": "Purchases of property and equipment plus finance-lease principal payments, as Meta reports them.",
     "fcf": "Operating cash flow minus capex, as reported by Meta. TTM figure derived from market cap divided by price-to-FCF (41.39).",
   }),
}

# Forward P&L assumptions (Base scenario drives revenue, operating margin, FCFF; these drive the rest)
FWD = {
 "NVDA": dict(gm=(0.73, 0.69), rd_share=0.80, other_pct=0.010, share_chg=-0.005,
              labels=["NTM", "Year 2", "Year 3", "Year 4", "Year 5"], ends=["Sep-27", "Sep-28", "Sep-29", "Sep-30", "Sep-31"],
              short=["NTM", "Y2", "Y3", "Y4", "Y5"]),
 "META": dict(gm=(0.78, 0.77), rd_share=0.70, other_pct=0.008, share_chg=0.0,
              labels=["NTM", "Year 2", "Year 3", "Year 4", "Year 5"], ends=["Sep-27", "Sep-28", "Sep-29", "Sep-30", "Sep-31"],
              short=["NTM", "Y2", "Y3", "Y4", "Y5"]),
}

def hist_calc(k):
    h = HIST[k]
    n = 10
    out = dict(gp=[], gm=[], opex=[], ebit=[], om=[], pretax=[], etr=[], ni=[], nm=[], eps=[], growth=[], fcfm=[], capexp=[])
    for i in range(n):
        gp = h["rev"][i] - h["cogs"][i]
        opex = h["rd"][i] + h["sga"][i] + h["other_op"][i]
        ebit = gp - opex
        assert ebit == h["ebit_rep"][i], (k, i, ebit, h["ebit_rep"][i])
        pretax = ebit + h["int_other"][i]
        ni = pretax - h["tax"][i]
        assert ni == h["ni_rep"][i], (k, i, ni, h["ni_rep"][i])
        out["gp"].append(gp); out["gm"].append(gp / h["rev"][i]); out["opex"].append(opex)
        out["ebit"].append(ebit); out["om"].append(ebit / h["rev"][i]); out["pretax"].append(pretax)
        out["etr"].append(h["tax"][i] / pretax); out["ni"].append(ni); out["nm"].append(ni / h["rev"][i])
        out["eps"].append(ni / h["shares"][i])
        out["growth"].append(None if i == 0 else h["rev"][i] / h["rev"][i - 1] - 1)
        out["fcfm"].append(h["fcf"][i] / h["rev"][i]); out["capexp"].append(h["capex"][i] / h["rev"][i])
    return out

def fwd_calc(k):
    """Five forward 12-month periods tied to the Base scenario (USD millions)."""
    c, f, h = E.CO[k], FWD[k], HIST[k]
    base = E.run(k)["scen"]["Base"]["rows"][:5]
    out = dict(rev=[], growth=[], gm=[], om=[], gp=[], opex=[], ebit=[], other=[], pretax=[], tax=[], ni=[], nm=[], shares=[], eps=[], fcff=[], rd=[], sga=[])
    prev = c["ttm"] * 1000
    for t in range(5):
        r = base[t]
        rev = r["rev"] * 1000
        gm = f["gm"][0] + (f["gm"][1] - f["gm"][0]) * t / 4
        om = r["m"]
        gp = rev * gm; ebit = rev * om; opex = gp - ebit
        rd = opex * f["rd_share"]; sga = opex - rd
        other = rev * f["other_pct"]
        pretax = ebit + other; tax = pretax * E.TAX; ni = pretax - tax
        shares = h["shares"][-1] * (1 + f["share_chg"]) ** (t + 1)
        out["rev"].append(rev); out["growth"].append(rev / prev - 1); prev = rev
        out["gm"].append(gm); out["om"].append(om); out["gp"].append(gp); out["opex"].append(opex)
        out["ebit"].append(ebit); out["other"].append(other); out["pretax"].append(pretax); out["tax"].append(tax)
        out["ni"].append(ni); out["nm"].append(ni / rev); out["shares"].append(shares); out["eps"].append(ni / shares)
        out["fcff"].append(r["fcff"] * 1000); out["rd"].append(rd); out["sga"].append(sga)
    return out

# P/E and valuation multiples (StockAnalysis.com statistics pages, 19 Sep 2026)
MULT = {
 "NVDA": dict(pe_t=28.11, pe_f=18.45, peg=0.35, ev_ebitda=26.55, ps=17.72),
 "META": dict(pe_t=25.09, pe_f=20.57, peg=1.02, ev_ebitda=15.67, ps=7.43),
}
# Benchmarks
BENCH = dict(
 sp_f=19.1, sp_f5=19.8, sp_f10=19.0, sp_t=25.5,
 semi_t=61.52, semi_f=None,
 comm_t=15.50, comm_f=12.63,
)

if __name__ == "__main__":
    for k in HIST:
        h = hist_calc(k)
        print(k, "hist ok; EPS", [round(x, 3) for x in h["eps"]])
        f = fwd_calc(k)
        print("  fwd rev", [round(x) for x in f["rev"]], "EPS", [round(x, 2) for x in f["eps"]], "OM", [round(x, 3) for x in f["om"]])
        print("  fwd NI", [round(x) for x in f["ni"]], "fcff", [round(x) for x in f["fcff"]])
        ps = E.CO[k]["price"]
        fw_eps = ps / MULT[k]["pe_f"]
        base = E.run(k)["scen"]["Base"]["ps"]
        print("  cons fwd EPS", round(fw_eps, 2), "Base value", round(base, 1), "implied fwd PE", round(base / fw_eps, 1), "model NTM EPS", round(f["eps"][0], 2), "PE on model NTM", round(ps / f["eps"][0], 1))
