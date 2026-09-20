(function () {
  "use strict";
  var REPO = "jay-nair-builds/foundry";
  var DATA = window.PROTEGE_HOLDINGS, ROSTER = window.PROTEGE_INVESTORS;
  var PRICES = window.PROTEGE_PRICES || null, TRACK = window.PROTEGE_TRACK || null;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var esc = function (s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  };
  if (!DATA || !ROSTER) {
    $("main").innerHTML = '<p class="empty">Data files are missing. Run <code>python3 scripts/fetch_13f.py --ua "Your Name you@email.com"</code>.</p>';
    return;
  }

  var byId = {};
  DATA.investors.forEach(function (d) { byId[d.id] = d; });
  var investors = ROSTER.filter(function (r) { return byId[r.id]; });

  var state = { id: null, q: 0, tag: "All", tab: "holdings", mimic: { amount: 10000, n: 10, cap: 25 }, other: null };

  // ---------- per-viewer storage (follows, last-seen filings); never required for the app to work ----------
  var store = {
    get: function (k, d) { try { var v = localStorage.getItem("protege." + k); return v ? JSON.parse(v) : d; } catch (e) { return d; } },
    set: function (k, v) { try { localStorage.setItem("protege." + k, JSON.stringify(v)); } catch (e) { /* private mode */ } }
  };
  var follows = store.get("follow", []), seen = store.get("seen", {}), notified = store.get("notified", {});
  var latestPeriod = function (id) { return byId[id] && byId[id].snapshots[0] ? byId[id].snapshots[0].period : ""; };
  var isFollowing = function (id) { return follows.indexOf(id) >= 0; };
  var hasNew = function (id) { return isFollowing(id) && seen[id] && seen[id] !== latestPeriod(id); };

  // ---------- formatting ----------
  var pct = function (x, d) { return (x * 100).toFixed(d == null ? 1 : d) + "%"; };
  var money = function (v) {
    var a = Math.abs(v);
    if (a >= 1e9) return "$" + (v / 1e9).toFixed(1) + "B";
    if (a >= 1e6) return "$" + (v / 1e6).toFixed(1) + "M";
    if (a >= 1e3) return "$" + (v / 1e3).toFixed(0) + "K";
    return "$" + v.toFixed(0);
  };
  var usd = function (v) { return "$" + Math.round(v).toLocaleString("en-US"); };
  var num = function (v) { return Math.round(v).toLocaleString("en-US"); };
  var key = function (p) { return (p.name + "|" + p.cls).toLowerCase(); };
  var label = function (p) { return esc(p.name) + (p.ticker ? "<small>" + esc(p.ticker) + "</small>" : ""); };

  // ---------- header ----------
  $("#asof").textContent = "Source: " + DATA.source + " · data built " + DATA.generated;
  if (DATA.sample) {
    var b = $("#banner");
    b.hidden = false;
    b.textContent = "Sample data. Holdings shown are illustrative, not real filings. Run scripts/fetch_13f.py to load SEC EDGAR 13F data.";
  }

  // ---------- gallery ----------
  var tags = ["All"];
  investors.forEach(function (i) { i.tags.forEach(function (t) { if (tags.indexOf(t) < 0) tags.push(t); }); });

  function renderChips() {
    var all = follows.length ? tags.concat(["Following"]) : tags;
    $("#chips").innerHTML = all.map(function (t) {
      return '<button class="chip" aria-pressed="' + (t === state.tag) + '" data-tag="' + esc(t) + '">' + esc(t) + "</button>";
    }).join("");
  }
  function renderGallery() {
    var list = investors.filter(function (i) {
      if (state.tag === "All") return true;
      if (state.tag === "Following") return isFollowing(i.id);
      return i.tags.indexOf(state.tag) >= 0;
    });
    $("#gallery").innerHTML = list.map(function (i) {
      var s = byId[i.id].snapshots[0];
      s = { total: s.total, positions: s.positions, count_label: (s.count || s.positions.length) + " positions" };
      var top = s.positions.slice(0, 3).map(function (p) { return '<span class="tick">' + esc(p.ticker || p.name.split(" ")[0]) + "</span>"; }).join("");
      return '<div class="card" data-id="' + i.id + '">' +
        '<button class="open" data-open="' + i.id + '" aria-current="' + (state.id === i.id) + '">' +
        "<h3>" + esc(i.name) + (hasNew(i.id) ? '<span class="badge">New filing</span>' : "") + '</h3><div class="f">' + esc(i.fund) + "</div>" +
        '<div class="f">' + esc(i.style) + '</div><div class="top3">' + top + "</div>" +
        '<div class="meta"><span>' + money(s.total) + "</span><span>" + s.count_label + "</span></div></button>" +
        '<button class="star" data-star="' + i.id + '" aria-pressed="' + isFollowing(i.id) + '" aria-label="Follow ' + esc(i.name) + '" title="Follow">' + (isFollowing(i.id) ? "★" : "☆") + "</button></div>";
    }).join("") || '<p class="empty">No investors match this filter.</p>';
  }

  // ---------- detail ----------
  function snap() { return byId[state.id].snapshots[state.q]; }
  function prevSnap() { return byId[state.id].snapshots[state.q + 1] || null; }

  function renderDetail() {
    var inv = investors.filter(function (i) { return i.id === state.id; })[0];
    $("#detail").hidden = false;
    $("#d-name").textContent = inv.name;
    $("#d-fund").textContent = inv.fund + " · " + inv.style;
    var lp = latestPeriod(inv.id), age = (Date.parse(DATA.generated) - Date.parse(lp)) / 864e5;
    $("#d-blurb").textContent = inv.blurb + (age > 200 ? " Note: the latest 13F on file is for the period ending " + lp + ", so this investor may have stopped filing or moved to another filer ID." : "");
    var snaps = byId[state.id].snapshots;
    $("#d-quarter").innerHTML = snaps.map(function (s, i) {
      return '<option value="' + i + '"' + (i === state.q ? " selected" : "") + ">Period " + esc(s.period) + " (filed " + esc(s.filed) + ")</option>";
    }).join("");
    var f = $("#d-follow");
    f.setAttribute("aria-pressed", isFollowing(inv.id));
    f.innerHTML = isFollowing(inv.id) ? "&#9733; Following" : "&#9734; Follow";
    var rss = $("#d-rss");
    rss.hidden = !!DATA.sample;
    rss.href = "feeds/" + inv.id + ".xml";
    if (isFollowing(inv.id)) { seen[inv.id] = latestPeriod(inv.id); store.set("seen", seen); }
    renderKpis();
    renderTab();
  }

  function renderKpis() {
    var s = snap(), pos = s.positions;
    var top10 = pos.slice(0, 10).reduce(function (a, p) { return a + p.weight; }, 0);
    var top1 = pos[0] ? pos[0].weight : 0;
    var pv = prevSnap(), turnover = null;
    if (pv) {
      var pm = {}; pv.positions.forEach(function (p) { pm[key(p)] = p.weight; });
      var cm = {}; pos.forEach(function (p) { cm[key(p)] = p.weight; });
      var all = {}; Object.keys(pm).concat(Object.keys(cm)).forEach(function (k) { all[k] = 1; });
      turnover = Object.keys(all).reduce(function (a, k) { return a + Math.abs((cm[k] || 0) - (pm[k] || 0)); }, 0) / 2;
    }
    var k = [
      [money(s.total), "13F portfolio value"],
      [s.count || pos.length, "Positions"],
      [pct(top1), "Largest position"],
      [pct(top10), "Top 10 concentration"],
      [turnover == null ? "n/a" : pct(turnover), "Weight shifted vs prior quarter"]
    ];
    $("#kpis").innerHTML = k.map(function (x) { return '<div class="kpi"><b>' + x[0] + "</b><span>" + x[1] + "</span></div>"; }).join("");
  }

  function renderTab() {
    ["holdings", "changes", "track", "mimic", "overlap"].forEach(function (t) { $("#tab-" + t).hidden = t !== state.tab; });
    document.querySelectorAll(".tabs button").forEach(function (b) { b.setAttribute("aria-selected", b.dataset.tab === state.tab); });
    ({ holdings: renderHoldings, changes: renderChanges, track: renderTrack, mimic: renderMimic, overlap: renderOverlap })[state.tab]();
  }

  function renderHoldings() {
    var pos = snap().positions.slice(0, 40), max = pos[0] ? pos[0].weight : 1;
    $("#tab-holdings").innerHTML = "<table><thead><tr><th>Holding</th><th class='hide-s'>Shares</th><th class='hide-s'>Value</th><th>Weight</th></tr></thead><tbody>" +
      pos.map(function (p) {
        return "<tr><td class='name'>" + label(p) + "</td><td class='hide-s'>" + num(p.shares) + "</td><td class='hide-s'>" + money(p.value) +
          "</td><td><div class='wcell'><span>" + pct(p.weight) + "</span><div class='bar' style='width:" + Math.max(1, Math.round(p.weight / max * 90)) + "px'></div></div></td></tr>";
      }).join("") + "</tbody></table>" +
      (snap().positions.length > 40 ? "<p class='note'>Showing the top 40 of " + (snap().count || snap().positions.length) + " positions.</p>" : "");
  }

  function diff() {
    var cur = snap().positions, pv = prevSnap();
    if (!pv) return null;
    var pm = {}; pv.positions.forEach(function (p) { pm[key(p)] = p; });
    var seen = {}, out = { neu: [], add: [], trim: [], exit: [] };
    cur.forEach(function (p) {
      var o = pm[key(p)]; seen[key(p)] = 1;
      if (!o) { out.neu.push({ p: p }); return; }
      var ch = o.shares ? (p.shares - o.shares) / o.shares : 0;
      if (ch > 0.05) out.add.push({ p: p, ch: ch });
      else if (ch < -0.05) out.trim.push({ p: p, ch: ch });
    });
    pv.positions.forEach(function (p) { if (!seen[key(p)]) out.exit.push({ p: p }); });
    out.add.sort(function (a, b) { return b.p.weight - a.p.weight; });
    out.trim.sort(function (a, b) { return b.p.weight - a.p.weight; });
    return out;
  }

  function renderChanges() {
    var d = diff(), el = $("#tab-changes");
    if (!d) { el.innerHTML = "<p class='empty'>No earlier quarter available to compare.</p>"; return; }
    function grp(title, cls, rows, fmt) {
      return "<div><h3>" + title + " <span class='pill " + cls + "'>" + rows.length + "</span></h3>" +
        (rows.length ? "<table><tbody>" + rows.slice(0, 12).map(function (r) {
          return "<tr><td class='name'>" + label(r.p) + "</td><td>" + fmt(r) + "</td></tr>";
        }).join("") + "</tbody></table>" : "<p class='empty'>None</p>") + "</div>";
    }
    var sign = function (c) { return (c > 0 ? "+" : "") + (c * 100).toFixed(0) + "% shares"; };
    el.innerHTML = "<div class='groups'>" +
      grp("New positions", "new", d.neu, function (r) { return pct(r.p.weight); }) +
      grp("Added to", "up", d.add, function (r) { return "<span class='up'>" + sign(r.ch) + "</span> · " + pct(r.p.weight); }) +
      grp("Trimmed", "down", d.trim, function (r) { return "<span class='down'>" + sign(r.ch) + "</span> · " + pct(r.p.weight); }) +
      grp("Exited", "down", d.exit, function (r) { return "was " + pct(r.p.weight); }) +
      "</div><p class='note'>Compared with the prior filing. A change of more than 5% in share count counts as added or trimmed. Share counts are not adjusted for splits.</p>";
  }

  // ---------- mimic builder ----------
  function buildMimic() {
    var m = state.mimic, pos = snap().positions.slice(0, m.n);
    var n = pos.length; if (!n) return [];
    var cap = Math.max(m.cap / 100, 1 / n);
    var tot = pos.reduce(function (a, p) { return a + p.weight; }, 0) || 1;
    var w = pos.map(function (p) { return p.weight / tot; }), fixed = pos.map(function () { return false; });
    for (var it = 0; it < 25; it++) {
      var over = false, freeSum = 0, fixedSum = 0;
      w.forEach(function (x, i) { if (x > cap + 1e-12) { w[i] = cap; fixed[i] = true; over = true; } });
      if (!over) break;
      w.forEach(function (x, i) { if (fixed[i]) fixedSum += x; else freeSum += x; });
      w.forEach(function (x, i) { if (!fixed[i]) w[i] = x / (freeSum || 1) * (1 - fixedSum); });
    }
    return pos.map(function (p, i) {
      var px = PRICES && p.ticker && PRICES.prices[p.ticker] ? PRICES.prices[p.ticker] : null;
      var amt = w[i] * m.amount;
      return { p: p, w: w[i], amt: amt, px: px, sh: px ? Math.floor(amt / px) : null };
    });
  }

  function renderMimic() {
    var m = state.mimic, max = Math.min(30, snap().positions.length);
    if (m.n > max) m.n = max;
    var el = $("#tab-mimic");
    el.innerHTML =
      "<div class='controls'>" +
      "<div><label for='m-amt'>Amount to allocate (USD)</label><input id='m-amt' type='number' min='100' step='100' value='" + m.amount + "'></div>" +
      "<div><label for='m-n'>Positions to copy: <output id='m-n-o'>" + m.n + "</output></label><input id='m-n' type='range' min='1' max='" + max + "' value='" + m.n + "'></div>" +
      "<div><label for='m-cap'>Max weight per holding: <output id='m-cap-o'>" + m.cap + "%</output></label><input id='m-cap' type='range' min='5' max='100' step='5' value='" + m.cap + "'></div>" +
      "</div><div id='m-out'></div>" +
      "<div class='actions'><button class='btn' id='m-csv'>Download CSV</button><button class='btn alt' id='m-copy'>Copy as text</button></div>" +
      "<p class='note'>Weights are the investor's top positions rescaled to 100% with your cap applied. This is a model allocation for study, not an order or a recommendation. Check prices, tax, fees and suitability before acting on anything.</p>";
    drawMimic();
    $("#m-amt").oninput = function (e) { state.mimic.amount = Math.max(0, +e.target.value || 0); drawMimic(); };
    $("#m-n").oninput = function (e) { state.mimic.n = +e.target.value; $("#m-n-o").textContent = e.target.value; drawMimic(); };
    $("#m-cap").oninput = function (e) { state.mimic.cap = +e.target.value; $("#m-cap-o").textContent = e.target.value + "%"; drawMimic(); };
    $("#m-csv").onclick = function () {
      var rows = [["Holding", "Ticker", "Weight", "Amount_USD", "Price_USD", "Whole_shares"]].concat(buildMimic().map(function (r) {
        return ['"' + r.p.name.replace(/"/g, '""') + '"', r.p.ticker, (r.w * 100).toFixed(2) + "%", r.amt.toFixed(2), r.px == null ? "" : r.px, r.sh == null ? "" : r.sh];
      }));
      var a = document.createElement("a");
      a.href = URL.createObjectURL(new Blob([rows.map(function (r) { return r.join(","); }).join("\n")], { type: "text/csv" }));
      a.download = "mimic-" + state.id + ".csv"; a.click(); URL.revokeObjectURL(a.href);
    };
    $("#m-copy").onclick = function () {
      var t = buildMimic().map(function (r) { return r.p.name + (r.p.ticker ? " (" + r.p.ticker + ")" : "") + ": " + pct(r.w) + " = " + usd(r.amt) + (r.sh != null ? " (" + r.sh + " sh @ " + usd(r.px) + ")" : ""); }).join("\n");
      if (navigator.clipboard) navigator.clipboard.writeText(t);
      $("#m-copy").textContent = "Copied";
      setTimeout(function () { $("#m-copy").textContent = "Copy as text"; }, 1500);
    };
  }
  function drawMimic() {
    var rows = buildMimic(), max = rows.reduce(function (a, r) { return Math.max(a, r.w); }, 0) || 1;
    var hasPx = rows.some(function (r) { return r.px != null; });
    var spent = rows.reduce(function (a, r) { return a + (r.sh != null ? r.sh * r.px : r.amt); }, 0);
    var totalAmt = rows.reduce(function (a, r) { return a + r.amt; }, 0);
    $("#m-out").innerHTML = "<table><thead><tr><th>Holding</th><th>Weight</th><th>Amount</th>" +
      (hasPx ? "<th class='hide-s'>Price</th><th>Whole shares</th>" : "") + "</tr></thead><tbody>" +
      rows.map(function (r) {
        return "<tr><td class='name'>" + label(r.p) + "</td><td><div class='wcell'><span>" + pct(r.w) + "</span><div class='bar' style='width:" +
          Math.max(1, Math.round(r.w / max * 90)) + "px'></div></div></td><td>" + usd(r.amt) + "</td>" +
          (hasPx ? "<td class='hide-s'>" + (r.px == null ? "n/a" : usd(r.px)) + "</td><td>" + (r.sh == null ? "n/a" : num(r.sh)) + "</td>" : "") + "</tr>";
      }).join("") + "<tr><td><strong>Total</strong></td><td><strong>" + pct(rows.reduce(function (a, r) { return a + r.w; }, 0)) +
      "</strong></td><td><strong>" + usd(totalAmt) + "</strong></td>" + (hasPx ? "<td class='hide-s'></td><td></td>" : "") + "</tr></tbody></table>" +
      (hasPx ? "<p class='note'>Whole shares at the last close (" + esc(PRICES.asof) + ", delayed). Cash left over after rounding down: <strong>" + usd(Math.max(0, totalAmt - spent)) + "</strong>.</p>"
        : "<p class='note'>No price data loaded, so share counts are not shown.</p>");
  }

  // ---------- track record ----------
  function renderTrack() {
    var el = $("#tab-track"), t = TRACK && TRACK.investors && TRACK.investors[state.id];
    if (!t) { el.innerHTML = "<p class='empty'>No track record yet. It needs at least two price points after a filing date and a loaded price history.</p>"; return; }
    var st = t.stats, W = 720, H = 260, L = 44, R = 12, T = 12, B = 26;
    var xs = t.series.map(function (r) { return Date.parse(r[0]); });
    var all = t.series.reduce(function (a, r) { return a.concat([r[1], r[2]]); }, []);
    var lo = Math.floor(Math.min.apply(null, all) / 10) * 10, hi = Math.ceil(Math.max.apply(null, all) / 10) * 10;
    if (hi === lo) hi = lo + 10;
    var x = function (v) { return L + (v - xs[0]) / ((xs[xs.length - 1] - xs[0]) || 1) * (W - L - R); };
    var y = function (v) { return T + (1 - (v - lo) / (hi - lo)) * (H - T - B); };
    var line = function (i) { return t.series.map(function (r, k) { return (k ? "L" : "M") + x(xs[k]).toFixed(1) + " " + y(r[i]).toFixed(1); }).join(" "); };
    var grid = [0, 1, 2, 3, 4].map(function (k) {
      var v = lo + (hi - lo) * k / 4;
      return "<line class='g' x1='" + L + "' x2='" + (W - R) + "' y1='" + y(v).toFixed(1) + "' y2='" + y(v).toFixed(1) + "'/><text x='" + (L - 6) + "' y='" + (y(v) + 4).toFixed(1) + "' text-anchor='end'>" + Math.round(v) + "</text>";
    }).join("");
    var sgn = function (v) { return (v >= 0 ? "+" : "") + pct(v); };
    var ahead = st["return"] - st.benchmarkReturn;
    var kp = [
      [sgn(st["return"]), "Mimic portfolio, " + st.years.toFixed(1) + " yrs"],
      [sgn(st.benchmarkReturn), "S&P 500 (" + esc(TRACK.benchmark) + ") same period"],
      [(ahead >= 0 ? "+" : "") + (ahead * 100).toFixed(1) + " pts", ahead >= 0 ? "Ahead of the index" : "Behind the index"],
      [pct(st.maxDrawdown), "Worst peak-to-trough fall"]
    ];
    if (st.cagr != null) kp.splice(2, 0, [sgn(st.cagr) + " / yr", "Annualised (index " + sgn(st.benchmarkCagr) + ")"]);
    el.innerHTML = "<div class='kpis'>" + kp.map(function (k) { return "<div class='kpi'><b>" + k[0] + "</b><span>" + k[1] + "</span></div>"; }).join("") + "</div>" +
      "<svg class='chart' viewBox='0 0 " + W + " " + H + "' role='img' aria-label='Growth of 100 invested, mimic portfolio versus S&P 500'>" + grid +
      "<text x='" + L + "' y='" + (H - 6) + "'>" + esc(st.start) + "</text><text x='" + (W - R) + "' y='" + (H - 6) + "' text-anchor='end'>" + esc(st.end) + "</text>" +
      "<path class='l2' d='" + line(2) + "'/><path class='l1' d='" + line(1) + "'/></svg>" +
      "<div class='legend'><span><i></i>Mimic portfolio</span><span><i class='b'></i>S&P 500 (" + esc(TRACK.benchmark) + ")</span><span>Growth of 100</span></div>" +
      "<p class='note'>What copying would have done: buy the top " + TRACK.params.top + " holdings (max " + Math.round(TRACK.params.cap * 100) + "% each) on each filing date, then rebalance at the next filing. That includes the reporting delay. Price return only: no dividends, fees, tax or slippage. " +
      "Average price coverage of the copied positions: " + pct(st.coverage, 0) + ". Past results do not predict future ones. Data to " + esc(TRACK.asof) + ".</p>";
  }

  // ---------- compare ----------
  function renderOverlap() {
    var el = $("#tab-overlap");
    var others = investors.filter(function (i) { return i.id !== state.id; });
    if (!state.other || state.other === state.id) state.other = others[0] && others[0].id;
    el.innerHTML = "<div class='controls'><div><label for='o-sel'>Compare with</label><select id='o-sel'>" +
      others.map(function (i) { return "<option value='" + i.id + "'" + (i.id === state.other ? " selected" : "") + ">" + esc(i.name) + " · " + esc(i.fund) + "</option>"; }).join("") +
      "</select></div></div><div id='o-out'></div>";
    $("#o-sel").onchange = function (e) { state.other = e.target.value; drawOverlap(); };
    drawOverlap();
  }
  function drawOverlap() {
    var a = snap().positions, b = byId[state.other].snapshots[0].positions, bm = {};
    b.forEach(function (p) { bm[key(p)] = p; });
    var shared = [], score = 0;
    a.forEach(function (p) { var o = bm[key(p)]; if (o) { shared.push({ p: p, o: o }); score += Math.min(p.weight, o.weight); } });
    shared.sort(function (x, y) { return Math.min(y.p.weight, y.o.weight) - Math.min(x.p.weight, x.o.weight); });
    var other = investors.filter(function (i) { return i.id === state.other; })[0];
    $("#o-out").innerHTML = "<div class='kpis'><div class='kpi'><b>" + pct(score) + "</b><span>Portfolio overlap (sum of the smaller weights)</span></div>" +
      "<div class='kpi'><b>" + shared.length + "</b><span>Shared holdings</span></div></div>" +
      (shared.length ? "<table><thead><tr><th>Holding</th><th>This investor</th><th>" + esc(other.name) + "</th></tr></thead><tbody>" +
        shared.map(function (r) { return "<tr><td class='name'>" + label(r.p) + "</td><td>" + pct(r.p.weight) + "</td><td>" + pct(r.o.weight) + "</td></tr>"; }).join("") + "</tbody></table>"
        : "<p class='empty'>No shared holdings in the latest filings.</p>") +
      "<p class='note'>Compares this investor's selected quarter with the other investor's latest filing.</p>";
  }

  // ---------- follow + alerts ----------
  function toggleFollow(id) {
    var i = follows.indexOf(id);
    if (i >= 0) { follows.splice(i, 1); delete seen[id]; }
    else { follows.push(id); seen[id] = latestPeriod(id); }
    store.set("follow", follows); store.set("seen", seen);
    if (state.tag === "Following" && !follows.length) state.tag = "All";
    renderChips(); renderGallery(); renderAlerts();
    if (state.id) renderDetail();
  }
  function renderAlerts() {
    var el = $("#alerts"), fresh = follows.filter(hasNew);
    if (!fresh.length) { el.hidden = true; el.innerHTML = ""; return; }
    var names = fresh.map(function (id) { return investors.filter(function (i) { return i.id === id; })[0].name; });
    var canNotify = "Notification" in window && Notification.permission === "default";
    el.hidden = false;
    el.innerHTML = "<div class='box'><span><strong>New 13F filing:</strong> " + names.map(esc).join(", ") + ".</span><span>" +
      (canNotify ? "<button class='btn alt' id='al-notify'>Notify me</button>" : "") +
      "<button class='btn alt' id='al-dismiss'>Mark as seen</button></span></div>";
    var d = $("#al-dismiss");
    if (d) d.onclick = function () { fresh.forEach(function (id) { seen[id] = latestPeriod(id); }); store.set("seen", seen); renderGallery(); renderAlerts(); };
    var n = $("#al-notify");
    if (n) n.onclick = function () { Notification.requestPermission().then(function () { renderAlerts(); pushNotifications(); }); };
  }
  function pushNotifications() {
    if (!("Notification" in window) || Notification.permission !== "granted") return;
    follows.filter(hasNew).forEach(function (id) {
      var k = id + ":" + latestPeriod(id);
      if (notified[k]) return;
      notified[k] = 1; store.set("notified", notified);
      var inv = investors.filter(function (i) { return i.id === id; })[0];
      try { new Notification("New 13F: " + inv.name, { body: "Filing for the period ending " + latestPeriod(id) + "." }); } catch (e) { /* unsupported */ }
    });
  }

  // ---------- add investor ----------
  var dlg = $("#add-dialog");
  $("#add-open").addEventListener("click", function () { $("#add-msg").textContent = ""; $("#add-name").value = ""; if (dlg.showModal) dlg.showModal(); else dlg.setAttribute("open", ""); });
  $("#add-go").addEventListener("click", function () {
    var name = $("#add-name").value.trim(), msg = $("#add-msg");
    if (name.length < 2) { msg.textContent = "Enter a fund name or CIK."; return; }
    var q = name.toLowerCase();
    var hit = investors.filter(function (i) { return i.name.toLowerCase().indexOf(q) >= 0 || i.fund.toLowerCase().indexOf(q) >= 0 || i.cik.replace(/^0+/, "") === q.replace(/^0+/, ""); })[0];
    if (hit) { msg.textContent = hit.name + " (" + hit.fund + ") is already tracked."; return; }
    var url = "https://github.com/" + REPO + "/issues/new?template=add-investor.yml&title=" + encodeURIComponent("Add investor: " + name) + "&fund=" + encodeURIComponent(name);
    window.open(url, "_blank", "noopener");
    msg.textContent = "Opened on GitHub. Submit the request there and it will be added automatically.";
  });

  // ---------- events ----------
  $("#chips").addEventListener("click", function (e) {
    var t = e.target.closest("[data-tag]"); if (!t) return;
    state.tag = t.dataset.tag; renderChips(); renderGallery();
  });
  $("#gallery").addEventListener("click", function (e) {
    var st = e.target.closest("[data-star]");
    if (st) { toggleFollow(st.dataset.star); return; }
    var c = e.target.closest("[data-open]"); if (!c) return;
    state.id = c.dataset.open; state.q = 0; state.other = null;
    renderGallery(); renderDetail(); renderAlerts();
    $("#detail").scrollIntoView({ behavior: "smooth", block: "start" });
  });
  $("#d-follow").addEventListener("click", function () { if (state.id) toggleFollow(state.id); });
  $("#d-quarter").addEventListener("change", function (e) { state.q = +e.target.value; renderKpis(); renderTab(); });
  document.querySelector(".tabs").addEventListener("click", function (e) {
    var b = e.target.closest("[data-tab]"); if (!b) return;
    state.tab = b.dataset.tab; renderTab();
  });

  renderChips();
  renderGallery();
  renderAlerts();
  pushNotifications();
  var startHash = location.hash.replace("#", "");
  if (startHash && byId[startHash]) { state.id = startHash; state.q = 0; renderGallery(); renderDetail(); }
})();
