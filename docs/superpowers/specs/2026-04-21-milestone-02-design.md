# Milestone 02 Design — Canon Competitive Intelligence

**Date:** 2026-04-21
**Due:** 2026-05-04
**Project:** ISBA 4715 Portfolio — Data Analytics Analyst at Canon U.S.A.

---

## Core Story

**Business question:** "How has Canon's competitive landscape shifted?"

Track daily stock performance and company fundamentals for Canon's 4 key competitors — Sony (SONY), Nikon (NINOY), HP (HPQ), Xerox (XRX) — to demonstrate strategic pricing and competitive intelligence skills directly relevant to the Canon Data Analytics Analyst role.

---

## 1. dbt Layer

### Staging Models
Both materialized as views in Snowflake `STAGING` schema.

| Model | Source | Key transformations |
|-------|--------|---------------------|
| `stg_stock_prices` | `RAW.STOCK_PRICES_DAILY` | Cast types, rename columns, filter nulls |
| `stg_company_overview` | `RAW.COMPANY_OVERVIEW` | Normalize numerics, cast strings |

### Mart Models
All materialized as tables in Snowflake `MART` schema.

| Model | Grain | Description |
|-------|-------|-------------|
| `dim_date` | One row per calendar day | Date spine Jan 1 2025 – Dec 31 2026 |
| `dim_company` | One row per ticker | Surrogate key, name, sector, exchange |
| `fact_stock_prices` | One row per trade_date × ticker | OHLCV prices, FK to dim_date + dim_company |
| `fact_company_snapshot` | One row per extraction date × ticker | PE ratio, market cap, analyst ratings, 52-week high/low, target price — snapshot of fundamentals each time the pipeline runs |

### dbt Tests
- `not_null` + `unique` on all primary keys
- `relationships` from fact FKs to dim PKs
- `accepted_values` on ticker (SONY, NINOY, HPQ, XRX)

---

## 2. Streamlit Dashboard

**Layout:** Sidebar navigation, dark theme, deployed to Streamlit Community Cloud.
**Data connection:** `snowflake-connector-python` via `st.secrets` (no credentials in code).

### Pages

**Page 1 — Overview** (descriptive)
- 4 KPI tiles: current price + YTD return per company, color-coded green/red
- Normalized price chart: all companies rebased to 100 at period start
- Date range selector in sidebar
- Key insight callout at bottom

**Page 2 — Price Trends** (descriptive)
- Line chart: raw closing price over time per company
- Multi-select checkbox to show/hide individual companies
- Summary table: high, low, average, latest price

**Page 3 — Volatility & Risk** (diagnostic)
- Bar chart: rolling price standard deviation per company
- Slider: adjust rolling window (7 / 14 / 30 days)
- Answers: "Why did some stocks move more than others?"

**Page 4 — Fundamentals** (diagnostic)
- Stacked bar: analyst Buy / Hold / Sell counts per company
- Metrics table: PE ratio, market cap, 52-week range, analyst target price
- Dropdown: select which metric to highlight

---

## 3. Knowledge Base

### Raw Sources (15+ files from 3 sites)
| Site | Target count | Content |
|------|-------------|---------|
| `usa.canon.com/newsroom` | ~8 articles | Product launches, US press releases |
| `global.canon/en/news` | ~5 articles | Global strategy, financial news |
| `global.canon/en/ir/` | ~5 documents | Earnings releases, annual report highlights |

Raw files saved to `knowledge/raw/` as markdown, named `canon_news_<hash>.md` or `canon_ir_<hash>.md`.

### Wiki Pages (Claude Code-generated)
Saved to `knowledge/wiki/`:
- `overview.md` — who Canon is, products, key markets, revenue scale
- `competitive_landscape.md` — Canon vs. Sony, Nikon, HP, Xerox positioning
- `strategy_and_financials.md` — synthesis from IR: revenue trends, segment performance, priorities

### Index
`knowledge/index.md` — lists all wiki pages with one-line summaries + all raw sources with URL and scrape date.

### CLAUDE.md Query Conventions
Added section: "When answering questions about Canon, read `knowledge/wiki/` pages first, then fall back to `knowledge/raw/`. Cite sources by filename."

---

## 4. Repo Structure

```
├── .github/workflows/        # GitHub Actions pipelines
├── docs/                     # job-posting.pdf, proposal.md, slides.pdf
├── extract/                  # extraction scripts (renamed from scripts/)
├── dbt/                      # dbt project
│   ├── models/
│   │   ├── staging/          # stg_stock_prices.sql, stg_company_overview.sql
│   │   └── mart/             # dim_date.sql, dim_company.sql, fact_stock_prices.sql, fact_company_snapshot.sql
│   ├── tests/
│   └── dbt_project.yml
├── streamlit/                # Dashboard app
│   ├── app.py                # Entry point + sidebar nav
│   └── pages/                # overview.py, price_trends.py, volatility.py, fundamentals.py
├── knowledge/
│   ├── raw/                  # 15+ scraped source files
│   ├── wiki/                 # overview.md, competitive_landscape.md, strategy_and_financials.md
│   └── index.md
├── .env.example
├── .gitignore
├── CLAUDE.md
├── README.md                 # Filled with template: ERD, pipeline diagram, insights, live URL
└── requirements.txt
```

---

## 5. Presentation Slides

Single PDF (`docs/slides.pdf`) submitted to Brightspace. Built in Google Slides or PowerPoint, exported as PDF.

**Slide 1 — Descriptive insight**
- Takeaway title: states the finding (e.g. "Sony outperformed all imaging peers by 5pp YTD")
- Visual: normalized price chart with callout highlighting the divergence point
- 1-sentence supporting evidence below the chart

**Slide 2 — Diagnostic insight**
- Takeaway title: states the root cause (e.g. "Xerox's volatility spiked 3× peers during restructuring announcement")
- Visual: volatility bar chart with callout on the outlier bar
- 1-sentence explanation of what drove it

**Slide 3 — Recommendation**
- Format: [Action] → [Expected outcome]
- Example: "Canon should monitor XRX and HPQ pricing quarterly → early signals of competitor discounting pressure"
- Brief rationale connecting to Canon's strategic pricing role

---

## 6. README + ERD

- **ERD:** Mermaid `erDiagram` block generated from dbt mart models, embedded in README
- **Pipeline diagram:** Existing Mermaid flowchart (already in README), updated to reflect `extract/` rename and dbt schema names
- **Dashboard screenshot:** Added after deployment
- **Key insights:** Takeaway titles for descriptive + diagnostic findings, actionable recommendation

---

## Deliverable Checklist

| # | Deliverable | Pts | Status |
|---|-------------|-----|--------|
| 8 | dbt project (staging + mart + tests) | 15 | Planned |
| 9 | Streamlit dashboard (deployed) | 15 | Planned |
| 10 | Presentation slides PDF | 7 | Planned |
| 11 | Knowledge base (15+ sources, wiki, index) | 8 | Planned |
| 12 | README.md (full template) | 5 | Planned |
| 13 | ERD in README | 3 | Planned |
| 14 | Clean repo structure + commit history | 2 | Planned |
