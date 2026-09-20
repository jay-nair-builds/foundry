"""Offline tests for the Protégé data pipeline. Run: python3 -m unittest discover -s tests -v (from apps/protege)."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import add_investor
import feeds
import figi
import prices
import sec
import track

INFO = b"""<?xml version="1.0"?>
<informationTable xmlns="http://www.sec.gov/edgar/document/thirteenf/informationtable">
 <infoTable><nameOfIssuer>APPLE INC</nameOfIssuer><titleOfClass>COM</titleOfClass><cusip>037833100</cusip><value>800</value>
  <shrsOrPrnAmt><sshPrnamt>8</sshPrnamt><sshPrnamtType>SH</sshPrnamtType></shrsOrPrnAmt></infoTable>
 <infoTable><nameOfIssuer>APPLE INC</nameOfIssuer><titleOfClass>COM</titleOfClass><cusip>037833100</cusip><value>200</value>
  <shrsOrPrnAmt><sshPrnamt>2</sshPrnamt><sshPrnamtType>SH</sshPrnamtType></shrsOrPrnAmt></infoTable>
 <infoTable><nameOfIssuer>COCA COLA CO</nameOfIssuer><titleOfClass>COM</titleOfClass><cusip>191216100</cusip><value>1000</value>
  <shrsOrPrnAmt><sshPrnamt>10</sshPrnamt><sshPrnamtType>SH</sshPrnamtType></shrsOrPrnAmt></infoTable>
 <infoTable><nameOfIssuer>SOME BOND</nameOfIssuer><titleOfClass>NOTE</titleOfClass><cusip>111111111</cusip><value>500</value>
  <shrsOrPrnAmt><sshPrnamt>500</sshPrnamt><sshPrnamtType>PRN</sshPrnamtType></shrsOrPrnAmt></infoTable>
 <infoTable><nameOfIssuer>TESLA INC</nameOfIssuer><titleOfClass>COM</titleOfClass><cusip>88160R101</cusip><value>300</value>
  <shrsOrPrnAmt><sshPrnamt>3</sshPrnamt><sshPrnamtType>SH</sshPrnamtType></shrsOrPrnAmt><putCall>Put</putCall></infoTable>
</informationTable>"""


class Sec(unittest.TestCase):
    def test_parse_skips_options_and_bonds(self):
        rows = sec.parse_info_table(INFO)
        self.assertEqual(len(rows), 3)
        self.assertEqual({r["cusip"] for r in rows}, {"037833100", "191216100"})

    def test_aggregate_merges_lines_and_weights(self):
        total, count, pos = sec.aggregate(sec.parse_info_table(INFO))
        self.assertEqual(total, 2000)
        self.assertEqual(count, 2)
        self.assertEqual(pos[0]["value"], 1000)
        self.assertAlmostEqual(sum(p["weight"] for p in pos), 1.0, places=5)
        apple = [p for p in pos if p["cusip"] == "037833100"][0]
        self.assertEqual(apple["shares"], 10)

    def test_max_positions_keeps_full_portfolio_weights(self):
        total, count, pos = sec.aggregate(sec.parse_info_table(INFO), max_positions=1)
        self.assertEqual(len(pos), 1)
        self.assertAlmostEqual(pos[0]["weight"], 0.5)

    def test_values_in_thousands_are_scaled_to_dollars(self):
        # $200 shares reported as 0.2 per share means <value> is in thousands of dollars.
        rows = [{"name": "A", "cls": "COM", "cusip": "1", "value": 200.0, "shares": 1000.0},
                {"name": "B", "cls": "COM", "cusip": "2", "value": 100.0, "shares": 500.0}]
        self.assertEqual(sec.value_scale(rows), 1000)
        total, _, pos = sec.aggregate(rows)
        self.assertEqual(total, 300000)
        self.assertEqual(pos[0]["value"], 200000)

    def test_values_in_dollars_are_left_alone(self):
        rows = [{"name": "A", "cls": "COM", "cusip": "1", "value": 200000.0, "shares": 1000.0}]
        self.assertEqual(sec.value_scale(rows), 1)
        self.assertEqual(sec.value_scale([]), 1)


class Figi(unittest.TestCase):
    def test_pick_prefers_common_stock(self):
        r = figi.pick([{"ticker": "AAPL34", "securityType": "Depositary Receipt"}, {"ticker": "AAPL", "securityType": "Common Stock"}])
        self.assertEqual(r["ticker"], "AAPL")

    def test_map_cusips_caches_and_handles_missing(self):
        calls = []

        def fake_post(payload, key):
            calls.append(len(payload))
            return [{"data": [{"ticker": "AAA", "securityType": "Common Stock", "name": "A"}]} if i["idValue"] == "1" else {"warning": "No identifier found."} for i in payload]

        cache = {"9": {"ticker": "OLD"}}
        figi.map_cusips(["1", "2", "9"], cache, api_key="k", post=fake_post, sleep=lambda s: None)
        self.assertEqual(cache["1"]["ticker"], "AAA")
        self.assertEqual(cache["2"], {})
        self.assertEqual(cache["9"]["ticker"], "OLD")
        figi.map_cusips(["1", "2"], cache, api_key="k", post=fake_post, sleep=lambda s: None)
        self.assertEqual(len(calls), 1)  # second run hits the cache only

    def test_failed_batch_is_left_for_retry(self):
        def boom(payload, key):
            raise OSError("rate limited")
        cache = {}
        figi.map_cusips(["1"], cache, post=boom, sleep=lambda s: None)
        self.assertNotIn("1", cache)


class Prices(unittest.TestCase):
    def test_stooq_symbol(self):
        self.assertEqual(prices.stooq_symbol("BRK.B"), "brk-b.us")

    def test_parse_stooq(self):
        csv = "Date,Open,High,Low,Close,Volume\n2026-01-02,1,2,0.5,1.5,100\n2026-01-05,1,2,0.5,1.7,100\n"
        self.assertEqual(prices.parse_stooq_csv(csv), [("2026-01-02", 1.5), ("2026-01-05", 1.7)])
        self.assertEqual(prices.parse_stooq_csv("No data"), [])

    def test_parse_yahoo_skips_nulls(self):
        obj = {"chart": {"result": [{"timestamp": [1767312000, 1767398400], "indicators": {"quote": [{"close": [10.0, None]}]}}]}}
        self.assertEqual(len(prices.parse_yahoo_json(obj)), 1)
        self.assertEqual(prices.parse_yahoo_json({}), [])

    def test_fetch_falls_back_to_yahoo(self):
        ts = list(range(1767312000, 1767312000 + 86400 * 30, 86400))
        yahoo = json.dumps({"chart": {"result": [{"timestamp": ts, "indicators": {"quote": [{"close": [1.0] * len(ts)}]}}]}}).encode()

        def get(url, ua):
            if "stooq" in url:
                return b"No data"
            return yahoo
        self.assertEqual(len(prices.fetch_history("AAPL", "2026-01-01", "2026-03-01", get=get)), 30)


def days(n, start=1):
    return [f"2026-02-{d:02d}" for d in range(start, start + n)]


class Track(unittest.TestCase):
    def test_mimic_weights_cap(self):
        w = track.mimic_weights([0.6, 0.2, 0.1, 0.1], cap=0.25)
        self.assertAlmostEqual(sum(w), 1.0)
        self.assertLessEqual(max(w), 0.25 + 1e-9)
        self.assertAlmostEqual(w[0], 0.25)

    def test_cap_never_below_equal_weight(self):
        w = track.mimic_weights([0.9, 0.1], cap=0.1)
        self.assertEqual(w, [0.5, 0.5])

    def test_two_stock_return(self):
        d = days(10)
        hist = {
            "SPY": [(x, 100.0) for x in d],
            "AAA": [(x, 100.0 * (1.10 if i >= 5 else 1.0)) for i, x in enumerate(d)],
            "BBB": [(x, 50.0) for x in d],
        }
        snaps = [{"filed": d[0], "positions": [{"ticker": "AAA", "weight": 0.5}, {"ticker": "BBB", "weight": 0.5}]}]
        res = track.compute_track(snaps, hist, cap=1.0)
        self.assertAlmostEqual(res["series"][-1][1], 105.0, places=2)
        self.assertAlmostEqual(res["stats"]["return"], 0.05, places=3)
        self.assertAlmostEqual(res["stats"]["benchmarkReturn"], 0.0, places=3)
        self.assertEqual(res["stats"]["maxDrawdown"], 0.0)

    def test_rebalance_at_next_filing(self):
        d = days(10)
        hist = {"SPY": [(x, 100.0) for x in d],
                "AAA": [(x, 100.0 if i < 4 else 200.0) for i, x in enumerate(d)],
                "BBB": [(x, 100.0 if i < 4 else 100.0) for i, x in enumerate(d)],
                "CCC": [(x, 100.0 if i < 6 else 150.0) for i, x in enumerate(d)]}
        s1 = {"filed": d[0], "positions": [{"ticker": "AAA", "weight": 1.0}]}
        s2 = {"filed": d[5], "positions": [{"ticker": "CCC", "weight": 1.0}]}  # switch after AAA doubled
        res = track.compute_track([s1, s2], hist, cap=1.0)
        self.assertAlmostEqual(res["series"][-1][1], 300.0, places=1)  # 100 -> 200 (AAA) -> 300 (CCC +50%)
        self.assertEqual(res["stats"]["rebalances"], 2)

    def test_unpriced_positions_are_dropped_and_coverage_reported(self):
        d = days(6)
        hist = {"SPY": [(x, 100.0) for x in d], "AAA": [(x, 100.0) for x in d]}
        snaps = [{"filed": d[0], "positions": [{"ticker": "AAA", "weight": 0.5}, {"ticker": "ZZZ", "weight": 0.5}]}]
        res = track.compute_track(snaps, hist, cap=1.0)
        self.assertLess(res["stats"]["coverage"], 1.01)
        self.assertAlmostEqual(res["series"][-1][1], 100.0)

    def test_no_benchmark_returns_none(self):
        self.assertIsNone(track.compute_track([], {"AAA": [("2026-02-01", 1.0)]}))


class Feeds(unittest.TestCase):
    def test_diff_classification(self):
        prev = {"positions": [{"name": "A", "cls": "COM", "shares": 100, "ticker": "A"}, {"name": "B", "cls": "COM", "shares": 100, "ticker": "B"},
                              {"name": "C", "cls": "COM", "shares": 100, "ticker": "C"}, {"name": "D", "cls": "COM", "shares": 100, "ticker": "D"}]}
        cur = {"positions": [{"name": "A", "cls": "COM", "shares": 150, "ticker": "A"}, {"name": "B", "cls": "COM", "shares": 50, "ticker": "B"},
                             {"name": "C", "cls": "COM", "shares": 102, "ticker": "C"}, {"name": "E", "cls": "COM", "shares": 10, "ticker": "E"}]}
        d = feeds.diff(cur, prev)
        self.assertEqual([p["ticker"] for p in d["added"]], ["A"])
        self.assertEqual([p["ticker"] for p in d["trimmed"]], ["B"])
        self.assertEqual([p["ticker"] for p in d["new"]], ["E"])
        self.assertEqual([p["ticker"] for p in d["exited"]], ["D"])

    def test_entry_escapes_xml(self):
        inv = {"id": "x", "name": "A & B <Fund>"}
        snap = {"accession": "1", "filed": "2026-08-14", "period": "2026-06-30", "count": 1, "positions": []}
        xml = feeds.entry(inv, snap, None)
        self.assertIn("A &amp; B &lt;Fund&gt;", xml)
        import xml.dom.minidom as md
        md.parseString(feeds.feed("t", "id", "http://x/", [xml], "2026-08-14"))


class AddInvestor(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "investors.json"
        self.path.write_text(json.dumps([{"id": "buffett", "name": "Warren Buffett", "cik": "0001067983", "fund": "x", "style": "s", "tags": [], "blurb": ""}]))

    def tearDown(self):
        self.tmp.cleanup()

    def fake_get(self, hits, subs_name="NEW FUND LP", filings=True):
        def get(url, ua):
            if "efts" in url:
                return json.dumps({"hits": {"hits": [{"_source": {"display_names": [h]}} for h in hits]}}).encode()
            rec = {"form": ["13F-HR"] if filings else ["8-K"], "accessionNumber": ["0001-26-1"], "filingDate": ["2026-08-14"], "reportDate": ["2026-06-30"]}
            return json.dumps({"name": subs_name, "filings": {"recent": rec}}).encode()
        return get

    def body(self, v):
        return f"### Fund name or CIK\n\n{v}\n\n### Anything else\n\n_No response_"

    def test_add_by_name(self):
        r = add_investor.run(self.body("New Fund LP"), "ua", self.fake_get(["NEW FUND LP (CIK 0001234567)"]), self.path)
        self.assertEqual(r["status"], "added")
        roster = json.loads(self.path.read_text())
        self.assertEqual(roster[-1]["cik"], "0001234567")
        self.assertEqual(roster[-1]["id"], "new-fund")

    def test_add_by_cik(self):
        r = add_investor.run(self.body("1234567"), "ua", self.fake_get([]), self.path)
        self.assertEqual(r["status"], "added")

    def test_existing_is_not_duplicated(self):
        r = add_investor.run(self.body("1067983"), "ua", self.fake_get([]), self.path)
        self.assertEqual(r["status"], "exists")
        self.assertEqual(len(json.loads(self.path.read_text())), 1)

    def test_ambiguous(self):
        r = add_investor.run(self.body("Alpha"), "ua", self.fake_get(["ALPHA ONE (CIK 1)", "ALPHA TWO (CIK 2)"]), self.path)
        self.assertEqual(r["status"], "ambiguous")

    def test_rejects_hostile_input(self):
        for bad in ["$(rm -rf /)", "<script>alert(1)</script>", "a", "x" * 300, "name; drop table"]:
            r = add_investor.run(self.body(bad), "ua", self.fake_get([]), self.path)
            self.assertEqual(r["status"], "invalid", bad)

    def test_no_13f_filings(self):
        r = add_investor.run(self.body("1234567"), "ua", self.fake_get([], filings=False), self.path)
        self.assertEqual(r["status"], "not_found")


if __name__ == "__main__":
    unittest.main()
