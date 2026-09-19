# Toolkit

Claude skills, tools and apps for **marketing, media, brand and investing**, built by Jay Nair.

The idea behind everything here: connect what marketers know about **brands and audiences** to the **numbers** that decide whether a business, a campaign or a stock is worth backing.

## What is in here

| Theme | What it covers | Status |
|---|---|---|
| [Investing](investing/) | Stock and ETF analysis, valuation models, scorecards | 1 skill live |
| Marketing | Marketing analytics, campaign and media measurement | Planned |
| Media | Media planning, channel mix, content performance | Planned |
| Brand | Brand insights, brand health, brand-to-financials links | Planned |
| Apps | Full tools and dashboards that combine the above | Planned |

Folders appear as soon as they hold something real.

## Live now

### [Stock and ETF analysis: the Brand-to-Balance-Sheet (BBS) method](investing/stock-etf-analysis/)

A Claude skill that analyses a stock the way an analyst would, then presents it so a non-finance reader can follow it:

- **Fair value** from a ten-year discounted cash flow in the Damodaran tradition, in Bear, Base and Bull scenarios, plus a reverse DCF that shows what the price already assumes
- **BBS Score (0 to 100)**: five pillars that run from brand power to balance-sheet strength
- **P/E against the market and the industry**, a **macro backdrop** chosen for each company, a **portfolio view** of the business mix and a **pre-mortem** on how the thesis fails
- Output as a visual scorecard and a downloadable Excel model with live formulas

Worked example: Nvidia against Meta, September 2026.

## How the repo is organised

```
toolkit/
  <theme>/
    <skill-or-app>/
      SKILL.md or README.md   what it does and how to use it
      examples/               sample output
      model/ or src/          supporting files
```

Every skill or app is self-contained in its own folder, so it can be copied out on its own.

## Disclaimer

Everything here is for education. Nothing is investment, legal or tax advice, and nothing is a recommendation to buy, sell or hold any security. Examples use data as of the date shown and are not updated.
