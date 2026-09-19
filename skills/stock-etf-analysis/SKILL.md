---
name: stock-etf-analysis
description: "Analyse a stock or ETF like a CFA: fair-value forecast, under/overvalued read, brand-lens BBS score, portfolio view, pre-mortem, as a visual scorecard, dashboard or Excel model. Education only."
license: Apache-2.0
compatibility: "Works best with web search or market-data tools enabled. The Excel model needs Python 3 with openpyxl."
metadata:
  author: Jay Nair
  version: "1.0.1"
  category: investing
  repository: https://github.com/jay-nair-builds/foundry
---

# Stock and ETF Analysis: the Brand-to-Balance-Sheet (BBS) method

Analyse a stock (or ETF) the way a CFA charterholder would, then present it so a **non-financial reader can follow it in 60 seconds**. What makes this method distinctive: it links **brand and marketing strength to the balance sheet**, values the company **story-first** (in the tradition of Aswath Damodaran), shows the **portfolio of businesses** behind the number, tests the **P/E against the market and the industry**, reads the **macro backdrop that matters for that specific company**, and forces a **pre-mortem** on how the thesis fails.

Educational analysis only. Never personalised investment advice.

**Wording rule:** never label sections or captions with phrases such as "in plain English", "in simple terms" or "simply put". Write the sentence itself clearly, and put definitions in the ? glossary popovers (see Step 8).

**Credit stamp (fixed):** every output carries this exact line: **Brand-to-Balance-Sheet (BBS) method by Jay Nair · github.com/jay-nair-builds/foundry**. It appears in the scorecard masthead and page footer, on the README sheet and Summary sheet of the Excel model, and as the last line of a text brief. Keep the wording as written. It is part of the terms of use of this skill (Apache-2.0, see the NOTICE file), so do not remove, shorten or reword it.

## Step 0: Set up

1. **Pull current data.** Price, 52-week range, shares, financial statements (ten years where available), latest results, segment data, guidance, consensus estimates, net debt, P/E and other multiples. Search the web or use connected market tools. **State the as-of date and source for every figure.** Never quote memory as current.
2. **Choose the output format.** If the user has not said, ask once: (a) Visual scorecard, (b) Interactive dashboard, (c) Excel model, (d) Quick text brief, or a combination. Default to (a) plus (c).
3. **Assumptions.** State base currency, horizon (default 10 years: 5 explicit, 5 fade), discount rate and terminal growth. Ask at most one question, only if essential.
4. **Snapshot first.** Always open with one line on what it is, plus ticker, exchange, currency, price and as-of date.

## Step 1: Forecast (story first, then numbers)

For each of **Bear / Base / Bull**, write a **two-sentence story**, then convert it into numbers:

- Year-1 revenue (anchor to company guidance and consensus; say where you deviate and why).
- Revenue growth for years 2-5, then a straight-line fade to the long-run rate in years 6-10.
- Operating margin path (year 1 to year 5, held after).
- Tax rate, and **cash conversion** (free cash flow to firm as a share of after-tax operating profit), or a sales-to-capital ratio if the data supports it.
- Share count trend (buybacks or dilution).

Label every forecast as an **estimate**.

## Step 2: Valuation (is it under- or overvalued?)

1. **Cost of capital build-up**: use the **current 10-year government bond yield as the risk-free rate** (cite the date and source; never leave a stale or illustrative rate once a macro section shows the live one), an equity risk premium, beta (Blume-adjust the raw beta: 0.67 x raw + 0.33), cost of equity, cost of debt (risk-free plus a spread), market-value weights, WACC. If a floor or cap is applied, say so and show the unadjusted figure. Flag any assumption that is not sourced.
2. **DCF** for each scenario: discount FCFF, add a terminal value, add cash, deduct debt, divide by shares. Show **fair value per share** for Bear, Base, Bull.
3. **Sanity checks**: terminal value as a share of enterprise value, and implied terminal return on capital (terminal growth divided by terminal reinvestment rate).
4. **P/E test against benchmarks**: show trailing and forward P/E for the company, the **broad market** (S&P 500 forward and trailing, with the 10-year average) and the **industry** (a sector or industry fund or index, chosen to match what the company does). Add PEG, EV/EBITDA, and the **P/E implied by the Base fair value** (Base value divided by consensus forward EPS, and by trailing EPS). Show the premium or discount to each benchmark. Note that providers use different methods, that index and fund P/Es are not exactly comparable, and when an industry fund mixes in unlike businesses (for example telecom inside a communication-services fund). Compare consensus forward EPS with the model's year-1 EPS.
5. **Reverse DCF**: scale the Base growth rates until value equals price. Report the **growth the price already assumes** versus the Base case. This is the most useful number for non-specialists.
6. **Sensitivity table**: fair value across discount rate and terminal growth.
7. **Read-out** relative to Base fair value, with a +/-15% band: **Undervalued**, **Roughly fair**, or **Overvalued (under these assumptions)**. Always show the margin of safety as a percentage and how the read flips if assumptions change.

## Step 3: The BBS Score (0-100)

Score five pillars from 1 to 10, each with one line of evidence and its source. Equal weights (20 points each) unless the user sets weights.

| Pillar | What it measures |
|---|---|
| **Brand Power** | Pricing power (gross margin trend, price vs volume growth), customer loyalty and retention, share of voice or mind, reputation and regulatory exposure |
| **Growth Engine** | Revenue growth, market size, and quality of growth drivers |
| **Profit Quality** | Operating margin, ROIC, cash conversion |
| **Balance-Sheet Strength** | Net debt, interest cover, capex burden relative to free cash flow |
| **Valuation Gap** | Formula: clamp(round(6 + 10 x margin of safety), 1, 10). 6 = fairly priced |

Also give the **marketing lens** in two or three lines: how efficiently the company converts marketing or ad spend into growth, its exposure to the advertising cycle or customer concentration, and any brand-related risk.

Bands: 80+ Exceptional, 65-79 Strong, 50-64 Mixed, below 50 Weak. Always spell out the name in full (Brand-to-Balance-Sheet Score) in the masthead, with a ? popover.

## Step 4: Financial track record and outlook

Show **ten years of reported results** (or as many as exist) and **five forecast periods** tied to the Base scenario: revenue, growth, gross margin, operating margin, net margin, diluted EPS, free cash flow. Adjust per-share history for stock splits. **Reconcile every historical year** (gross profit less operating costs equals reported operating income; pre-tax income less tax equals reported net income) before using it, and note one-offs (acquisition break fees, legal accruals, restructuring, unusual tax rates). Forecast periods are 12-month windows from the valuation date (NTM, then years 2-5); say so next to the fiscal-year history.

## Step 5: Portfolio view (what is inside the number)

Break the company into the parts that earn, or lose, the money. Show revenue mix, growth, and profit or margin by part, and what each part means for the valuation:

- **Technology and platform groups**: segments or market platforms (e.g. data center vs other; family of apps vs reality labs), concentration in the largest line, and profit absorbed by loss-making bets.
- **Consumer goods groups (e.g. Procter & Gamble, Unilever)**: categories, power brands versus the tail, regions and emerging markets, and price versus volume versus mix growth. Note where a sum-of-the-parts view would change the answer.
- **ETFs and funds**: holdings, sectors, regions and overlap.

Only report segment figures that a source discloses. Say plainly when segment profit is not disclosed.

## Step 6: Macro backdrop, chosen for the company

Pick indicators by **how the company earns money**, not from a fixed list. Give each a latest reading with its date and source, a **tag (tailwind, headwind, mixed, low relevance)**, one line on why it matters, and a one-line **net read** per company. Show a **relevance matrix** (High, Med, Low) so the reader sees why each set was chosen. Always include the live risk-free rate and policy rate because they feed the discount rate.

| Company type | Lead indicators |
|---|---|
| Advertising and consumer platforms | Consumer sentiment, inflation (headline and core), real disposable income and spending, saving rate, retail and ad-market growth, AI or data-centre input costs |
| Semiconductors and AI hardware | Customer capital spending (hyperscaler capex), global chip sales, rates, energy and power costs, export and trade policy, supply-chain capacity |
| Consumer goods (e.g. Procter & Gamble, Unilever) | Raw-material and packaging costs (resin, pulp, palm oil, oil), consumer sentiment, real disposable income, inflation and price elasticity, currency and emerging-market growth, retailer inventory |
| Banks and insurers | Yield curve, credit spreads and defaults, unemployment, loan growth, regulation |
| Energy and materials | Commodity prices, inventories, demand growth, capex cycle, currency |

Only report readings a source supports; cite the source. Label the tag as the analyst's judgement.

## Step 7: Bull / Bear and pre-mortem

**Bull / Bear:** three short bullets each, argued fairly.

**Pre-mortem:** imagine it is three years later and the stock is **down 40%**. Write the **three most likely reasons**, each with the **early-warning indicator**, a **suggested kill-switch threshold** (a measurable trigger, labelled as the analyst's suggestion), and the **evidence that would prove the thesis wrong**. Also list the strongest bear argument the analyst would most like to ignore.

## Step 8: Present it for a non-financial reader

Every section opens with a one-line lead that states the takeaway. **Every technical term gets a small ? button** that opens a short popover with two parts: **what it is** and **how it is calculated** (for example BBS Score, each pillar, DCF, FCFF, WACC, beta, risk-free rate, equity risk premium, terminal growth, fair value, gap to price, reverse DCF, CAGR, 52-week range, P/E trailing and forward, PEG, EV/EBITDA, benchmarks, margins, EPS, free cash flow, sensitivity, pre-mortem, and each macro indicator). Popovers open on click or tap, close on outside click or Escape, work with the keyboard, and stay inside the viewport. Use the dataviz skill for charts and the artifact-design skill for pages.

### Page structure (visual scorecard)

The page tells a story in this order: answer first, then the evidence from the brand outwards, then the price, then what could break the answer. Companies sit side by side inside every chapter.

1. **Masthead**: eyebrow with the full framework name, the conclusion as the headline, a one-sentence dek, a byline with the credit stamp, then a four-cell **approach and parameters strip** (method, scenarios, discount rate, score), each with a ? popover, and the price date.
2. **Verdict at a glance**: one **identical card per company**, so every element sits in the same place. Order inside each card: name, ticker and market cap with a verdict chip; three large figures (price, Base value, gap to price); a **fair-value range bar** (Bear to Bull band, Base marker, dashed price line, every marker directly labelled with its value); a **52-week range bar**; a **BBS gauge** with the four bands; a strip of forward P/E, S&P 500 forward P/E and PEG. Follow the cards with a bottom-line paragraph.
3. **The valuation model in brief**: four short steps (forecast, turn profit into cash, discount to today, value per share), then one card per company with Bear, Base and Bull fair values and the assumptions behind them, the discount rate and long-run growth, the gap to price, the Excel download button and links to the detail below.
4. **The story behind the verdict**: a chapter strip with links, each chapter phrased as the question it answers. Every chapter heading carries a "Chapter N of 7" label and its question.
5. **Chapter 1, the brand**: the marketing lens. **Chapter 2, the business**: portfolio view of segments, brands or categories. **Chapter 3, the track record**: ten years of results and five forecast periods (revenue bar chart with forecast lighter and dashed, gross and operating margin line chart, summary table with forecast columns tinted). **Chapter 4, the economy around it**: macro backdrop (four headline tiles, relevance matrix, one panel per company). **Chapter 5, the score**: BBS pillar table with 10-segment meters and evidence.
6. **Chapter 6, the price**: what today's price already assumes (reverse-DCF bars, Base versus priced-in growth), then P/E against the market and the industry (trailing and forward bar panels with company bars in series colours, benchmarks in grey and Base-implied P/E as outlined bars, a multiples table with premium or discount, and a method note).
7. **Chapter 7, what could break it**: sensitivity heat tables, then the pre-mortem.
8. **Download panel** for the Excel model, then **method, assumptions, what changed since the last version, and sources**, then a page footer with the credit stamp and the education-only disclaimer.

### Visual identity (institutional research, not template-looking)

- **White page**, deep-green identity: a dark-green gradient masthead, hairline rules, thin section rules in deep green. A serif for headings and large titles (Source Serif 4) and a neutral grotesque for everything else (Public Sans), tabular figures, small letter-spaced caps for labels. No emoji, no pill-shaped buttons, no decorative gradients beyond the masthead, no icon-in-a-circle cards.
- Take the restraint of large asset-manager research pages as a reference, but **never copy or imitate any real firm's name, logo or branding**.
- **Layout discipline:** two-column card grids with identical internals; consistent blocks (title row, chart, label row); no dense multi-column table rows of mini charts; every chart element directly labelled (no unlabelled axes or legends that need decoding); generous spacing.
- Build simple bars, ranges and gauges in **HTML and CSS** (they stay legible at any width). Use **width-aware SVG** (drawn at the container's real pixel width and redrawn on resize) for time-series charts, with tooltips on hover.
- Series colours must pass the dataviz validator on the white surface (for example green #0A7D55 and gold #B5820F); benchmarks in neutral greys. Status colours (tailwind green, headwind rust, mixed grey) always come with an icon and a text label. The white page is a deliberate single-theme design.
- Check the layout at 1200px and 400px with no horizontal page scroll; only tables scroll inside their own container.

### Format (a): Visual scorecard
A single self-contained HTML page (publish with the Artifact tool). Add the `downloads` capability so the page can offer the Excel model.

### Format (b): Interactive dashboard
An HTML page where the user can **switch scenario and change discount rate, terminal growth and margin** with sliders and see fair value and the verdict update live. Include a sortable comparison table.

### Format (c): Excel model (Damodaran-style)
Use the xlsx skill. **One engine, two outputs:** compute the numbers in one script and use the same inputs to write the workbook and the page, then recalculate the workbook and reconcile every value per share, forecast line and history check against the script before delivery.

- **README**: the credit stamp as the first line under the title, then method, colour code, sheet list, sources, limits, and how to open it in Google Sheets (upload to Drive, open with Google Sheets).
- **Summary**: both companies side by side, linked to the company sheets, including multiples and the P/E implied by the Base value, with the credit stamp under the title.
- **One valuation sheet per company**: market data; cost-of-capital build-up; **story-to-numbers scenario table** with a narrative per scenario (Bear, Base, Bull, Market-implied); ten-year FCFF projection per scenario; valuation bridge; live sensitivity grid.
- **One P&L sheet per company**: ten years of reported history, a latest-twelve-months column and five forecast periods. Rows: revenue, growth, cost of revenue, gross profit and margin, R&D, SG&A, other operating items, total operating expenses, operating income and margin, interest and other income, pre-tax income, tax and effective rate, net income and margin, diluted shares, EPS and growth, free cash flow and margin, capex and capex as a share of revenue. Forecast revenue, operating margin and free cash flow **link to the Base scenario**; gross margin, R&D share, other income and share change are blue inputs. Add **integrity checks** (calculated versus reported operating income and net income, differences shown as zero) and a growth and margin summary (3, 5, 9-year CAGRs, average margin). Comments explain one-offs, split adjustments and definitions.
- **PE_Benchmarks**: company multiples, S&P 500 and industry benchmarks with sources and dates, premium or discount, P/E implied by the Base value, and the model's year-1 EPS against consensus.
- **Macro**: relevance matrix and the selected indicators per company with reading, period, direction, why it matters and source.
- **BBS_Score**: editable pillar scores and weights; Valuation Gap driven by formula from the DCF.
- Blue inputs, black formulas, green cross-sheet links, yellow fill for key assumptions. Live formulas throughout, a comment citing the source for each hardcoded input, zero formula errors.
- Deliver the file with SendUserFile, and offer it inside the page through the `downloads` capability.

### Format (d): Quick text brief
One screen in chat: snapshot, fair-value range and read-out, P/E versus market and industry, BBS score, top three pre-mortem risks, bottom line on the trade-offs, then the credit stamp as the last line.

## ETFs

For an ETF, replace Steps 1-2 with: index and method, TER, spread, tracking difference, domicile, accumulating or distributing, fund size, currency and hedging, top holdings and concentration, look-through weighted P/E and overlap with other holdings. Keep the BBS scorecard where meaningful (Brand Power becomes provider and index quality), and the portfolio view, macro backdrop and pre-mortem always apply. If the user gives investor context (e.g. Switzerland, CHF), prefer UCITS-eligible, EU-domiciled ETFs and add a short note on currency exposure and withholding-tax domicile.

## Guardrails

- **No personalised advice.** Never say buy, sell or hold. Present the valuation read as a model output under stated assumptions, and note you are not a licensed advisor.
- **Show sources, dates and assumptions.** Flag anything unverified, anything from a single source, and label estimates as estimates. Say where the Base case sits versus analyst consensus.
- **Show uncertainty**: ranges, scenarios and sensitivity, never a single false-precision number.
- **Separate fact from opinion.** Macro tags and BBS pillar scores are analyst judgement; say so. Past performance and backtests do not predict returns.
- When a live input (such as the risk-free rate) changes a result versus an earlier version, say what changed and by how much.
- Never place trades or orders.

## Style

Concise, high-signal, bold and business-connected. Lead with the answer (verdict, score, fair-value range), then the evidence.

## Bundled files

- `scripts/engine.py`: the Python valuation engine (scenarios, reverse DCF, sensitivity).
- `scripts/fin.py`: historical and forward P&L data for the worked example. Run `python scripts/fin.py` to check that reported operating and net income reconcile.
- `assets/example/`: a finished scorecard page and Excel model (Nvidia against Meta) to match in structure and quality.
- `assets/screens/`: screenshots of the scorecard.

## Licence and credit

Licensed under Apache-2.0. Copyright 2026 Jay Nair. The Brand-to-Balance-Sheet method and the BBS Score name originate with Jay Nair. Copies and adaptations must keep the NOTICE file and the credit stamp described above. Source: github.com/jay-nair-builds/foundry
