# Star Schema Design: Alpha Vantage Stock Data

## Overview

Star schema for competitive stock price analytics targeting the Canon U.S.A. Data Analytics Analyst role.
Tracks daily stock performance for Canon and key imaging/document competitors.

**Business Question:** How does Canon's stock performance compare to competitors, and what drives divergence?

## Data Source

**API:** Alpha Vantage  
**Endpoints:** `TIME_SERIES_DAILY_ADJUSTED`, `OVERVIEW`  
**Companies Tracked:** Canon (CAJ), Sony (SONY), Nikon (NINOY), HP (HPQ), Xerox (XRX)  
**Update Frequency:** Weekdays after US market close via GitHub Actions

## Star Schema

```
                    ┌─────────────────┐
                    │    DIM_DATE     │
                    ├─────────────────┤
                    │ date_key (PK)   │
                    │ full_date       │
                    │ day_of_week     │
                    │ day_name        │
                    │ week_of_year    │
                    │ month           │
                    │ month_name      │
                    │ quarter         │
                    │ year            │
                    │ is_weekend      │
                    │ is_trading_day  │
                    └────────┬────────┘
                             │
                             │
┌──────────────────────────┐ │
│      DIM_COMPANY         │ │
├──────────────────────────┤ │
│ company_key (PK)         │ │
│ ticker                   │ │
│ company_name             │ │
│ sector                   ├─┤──────────────────────────┐
│ industry                 │ │                          │
│ country                  │ │  FACT_STOCK_PRICES       │
│ currency                 │ │  ────────────────────    │
│ exchange                 │ │  date_key (FK)           │
│ market_capitalization    ├─┤  company_key (FK)        │
│ pe_ratio                 │ │  ──────────────          │
│ forward_pe               │ │  open_price              │
│ peg_ratio                │ │  high_price              │
│ book_value               │ │  low_price               │
│ dividend_yield           │ │  close_price             │
│ eps                      │ │  adjusted_close          │
│ revenue_ttm              │ │  volume                  │
│ gross_profit_ttm         │ │  dividend_amount         │
│ ebitda                   │ │  split_coefficient       │
│ week_52_high             │ │  price_change_pct        │
│ week_52_low              │ │  vs_canon_spread         │
│ analyst_target_price     │ └──────────────────────────┘
│ analyst_rating_buy       │
│ analyst_rating_hold      │
│ analyst_rating_sell      │
└──────────────────────────┘
```

## Table Definitions

### FACT_STOCK_PRICES

Daily stock price snapshot — the core analytics table.

| Column | Type | Description |
|--------|------|-------------|
| date_key | INT | FK to DIM_DATE (YYYYMMDD) |
| company_key | INT | FK to DIM_COMPANY |
| open_price | DECIMAL(14,4) | Opening price (USD) |
| high_price | DECIMAL(14,4) | Daily high |
| low_price | DECIMAL(14,4) | Daily low |
| close_price | DECIMAL(14,4) | Closing price |
| volume | BIGINT | Shares traded |

**Grain:** One row per company per trading day

### DIM_COMPANY

Company fundamentals — updated on each extraction run.

| Column | Type | Description |
|--------|------|-------------|
| company_key | INT | Surrogate PK |
| ticker | VARCHAR(10) | Stock ticker symbol |
| company_name | VARCHAR(300) | Full company name |
| sector | VARCHAR(100) | e.g. Technology |
| industry | VARCHAR(200) | e.g. Electronic Equipment |
| country | VARCHAR(50) | Country of headquarters |
| market_capitalization | BIGINT | Market cap (USD) |
| pe_ratio | DECIMAL(12,4) | Price-to-earnings ratio |
| week_52_high | DECIMAL(14,4) | 52-week high price |
| week_52_low | DECIMAL(14,4) | 52-week low price |
| analyst_target_price | DECIMAL(14,4) | Consensus price target |
| analyst_rating_buy | INT | # analyst buy ratings |
| analyst_rating_hold | INT | # analyst hold ratings |
| analyst_rating_sell | INT | # analyst sell ratings |

### DIM_DATE

Standard date dimension.

| Column | Type | Description |
|--------|------|-------------|
| date_key | INT | YYYYMMDD format PK |
| full_date | DATE | Actual date |
| day_of_week | INT | 1 = Monday … 7 = Sunday |
| day_name | VARCHAR(10) | Monday, Tuesday, etc. |
| week_of_year | INT | 1–52 |
| month | INT | 1–12 |
| month_name | VARCHAR(10) | January, February, etc. |
| quarter | INT | 1–4 |
| year | INT | 4-digit year |
| is_weekend | BOOLEAN | Saturday or Sunday |
| is_trading_day | BOOLEAN | NYSE trading day |

## Sample Analytics Queries

### 1. Canon vs. Competitor YTD Returns
```sql
SELECT
    c.ticker,
    c.company_name,
    MIN(f.adjusted_close) AS start_price,
    MAX(CASE WHEN d.full_date = CURRENT_DATE THEN f.adjusted_close END) AS current_price,
    ROUND(
        (MAX(CASE WHEN d.full_date = CURRENT_DATE THEN f.adjusted_close END)
         / MIN(f.adjusted_close) - 1) * 100, 2
    ) AS ytd_return_pct
FROM fact_stock_prices f
JOIN dim_company c ON f.company_key = c.company_key
JOIN dim_date d ON f.date_key = d.date_key
WHERE d.year = YEAR(CURRENT_DATE)
GROUP BY c.ticker, c.company_name
ORDER BY ytd_return_pct DESC;
```

### 2. 30-Day Price Volatility by Company
```sql
SELECT
    c.ticker,
    c.company_name,
    STDDEV(f.adjusted_close) AS price_stddev,
    AVG(f.adjusted_close) AS avg_price,
    STDDEV(f.adjusted_close) / AVG(f.adjusted_close) AS coefficient_of_variation
FROM fact_stock_prices f
JOIN dim_company c ON f.company_key = c.company_key
JOIN dim_date d ON f.date_key = d.date_key
WHERE d.full_date >= CURRENT_DATE - 30
GROUP BY c.ticker, c.company_name
ORDER BY coefficient_of_variation DESC;
```

### 3. Canon Analyst Sentiment vs. Competitors
```sql
SELECT
    ticker,
    company_name,
    analyst_rating_buy,
    analyst_rating_hold,
    analyst_rating_sell,
    ROUND(analyst_rating_buy::FLOAT /
          NULLIF(analyst_rating_buy + analyst_rating_hold + analyst_rating_sell, 0) * 100, 1
    ) AS buy_pct,
    analyst_target_price,
    week_52_high,
    week_52_low
FROM dim_company
ORDER BY buy_pct DESC;
```

## Data Volume Estimates

| Table | Rows (Initial) | Growth Rate |
|-------|----------------|-------------|
| FACT_STOCK_PRICES | ~2,500 (5 cos × 100 days) | ~5/day (weekdays) |
| DIM_COMPANY | 5 | Stable |
| DIM_DATE | 365 | +1/day |

## Relevance to Canon Role

| Job Requirement | How This Schema Addresses It |
|-----------------|------------------------------|
| Strategic pricing support | Competitor price/valuation benchmarking |
| ROI modeling | P/E ratio, analyst targets vs. actuals |
| Revenue analytics | Market cap trends, revenue TTM tracking |
| SQL proficiency | Window functions, aggregations, date math |
| Power BI / Streamlit reporting | Star schema optimized for BI tools |
