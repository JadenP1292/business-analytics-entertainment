# Canon Competitive Intelligence

This project tracks daily stock performance and analyst sentiment for Canon's key imaging and document competitors — Sony, Nikon, HP, and Xerox — to demonstrate end-to-end analytics engineering skills relevant to the Data Analytics Analyst role at Canon U.S.A., Inc.

The pipeline extracts data via the Alpha Vantage API and Canon newsroom scraper, loads it into Snowflake, transforms it through dbt staging and mart layers, and surfaces competitive insights through a deployed Streamlit dashboard. A Claude Code-curated knowledge base synthesizes Canon IR and newsroom sources for qualitative context.

## Job Posting

**Role:** Data Analytics Analyst
**Company:** Canon U.S.A., Inc.

This project directly demonstrates the posting's core requirements: SQL for analytics (dbt models + mart queries), Python data pipelines (Alpha Vantage API + web scrapers), automated orchestration (GitHub Actions), and dashboard development (Streamlit) — applied to Canon's own competitive landscape.

## Tech Stack

| Layer | Tool |
|-------|------|
| Source 1 | Alpha Vantage REST API (stock prices + fundamentals) |
| Source 2 | Canon USA / Global newsroom + IR web scrape |
| Data Warehouse | Snowflake |
| Transformation | dbt |
| Orchestration | GitHub Actions (scheduled) |
| Dashboard | Streamlit (Streamlit Community Cloud) |
| Knowledge Base | Claude Code (scrape → summarize → query) |

## Pipeline Diagram

```mermaid
flowchart TD
    subgraph Sources
        A1["Alpha Vantage API\nSONY · NINOY · HPQ · XRX\nDaily prices + fundamentals"]
        A2["Canon Newsroom + IR\nPress releases · Earnings\nusa.canon.com · global.canon"]
    end

    subgraph "GitHub Actions"
        G1["extract_alpha_vantage.yml\nWeekdays 21:00 UTC"]
        G2["scrape_canon_news.yml\nDaily 09:00 UTC"]
    end

    subgraph "Snowflake RAW"
        R1["STOCK_PRICES_DAILY\nCOMPANY_OVERVIEW"]
        R2["CANON_NEWS"]
    end

    subgraph "Snowflake STAGING"
        S1["stg_stock_prices\nstg_company_overview"]
    end

    subgraph "Snowflake MART"
        M1["fact_stock_prices\nfact_company_snapshot"]
        M2["dim_company\ndim_date"]
    end

    subgraph Outputs
        D["Streamlit Dashboard\n(deployed)"]
        K["knowledge/wiki/\n(Claude Code queryable)"]
    end

    A1 --> G1 --> R1 --> S1 --> M1 & M2 --> D
    A2 --> G2 --> R2
    A2 --> K
```

## ERD (Star Schema)

```mermaid
erDiagram
    dim_company {
        int company_key PK
        varchar ticker
        varchar company_name
        varchar sector
        varchar industry
        varchar country
        varchar exchange
    }

    dim_date {
        int date_key PK
        date full_date
        int day_of_week
        varchar day_name
        int week_of_year
        int month
        varchar month_name
        int quarter
        int year
        boolean is_weekend
    }

    fact_stock_prices {
        int company_key FK
        date trade_date
        varchar ticker
        float open_price
        float high_price
        float low_price
        float close_price
        bigint volume
        timestamp extracted_at
    }

    fact_company_snapshot {
        int company_key FK
        varchar ticker
        date snapshot_date
        bigint market_capitalization
        float pe_ratio
        float week_52_high
        float week_52_low
        float analyst_target_price
        int analyst_rating_buy
        int analyst_rating_hold
        int analyst_rating_sell
    }

    dim_company ||--o{ fact_stock_prices : "company_key"
    dim_company ||--o{ fact_company_snapshot : "company_key"
    dim_date ||--o{ fact_stock_prices : "date_key"
```

## Dashboard Preview

![Canon Competitive Intelligence Dashboard](docs/dashboard-screenshot.png)

## Key Insights

**Descriptive (what happened?):** Review the Overview page after deployment — the normalized price chart shows relative performance across Sony, Nikon, HP, and Xerox over the selected period.

**Diagnostic (why did it happen?):** The Volatility page identifies which competitors showed the highest price swings and correlates with market events visible in the Canon newsroom knowledge base.

**Recommendation:** Canon should establish a quarterly competitor pricing monitor tracking XRX and HPQ discount patterns — early signals of enterprise printing price pressure before it reaches Canon's dealer channel.

## Live Dashboard

URL: https://canon-competitive-intelligence.streamlit.app/

## Knowledge Base

A Claude Code-curated wiki built from 21 scraped sources. Wiki pages live in `knowledge/wiki/`, raw sources in `knowledge/raw/`. Browse `knowledge/index.md` to see all pages.

Query it — open Claude Code in this repo and ask:
- "What are Canon's main business segments?"
- "How does Canon compete with Sony in cameras?"
- "What is Canon's strategic direction according to IR sources?"

Claude Code reads wiki pages first and falls back to raw sources. See `CLAUDE.md` for query conventions.

## Setup & Reproduction

**Requirements:** Python 3.12+, Snowflake trial account, Alpha Vantage API key (free at alphavantage.co)

```bash
git clone https://github.com/JadenP1292/business-analytics-entertainment
cd business-analytics-entertainment
pip install -r requirements.txt
cp .env.example .env   # fill in your credentials
```

Fill in `.env`:
```
SNOWFLAKE_ACCOUNT=hyc09383.us-east-1
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_DATABASE=BASKET_CRAFT
SNOWFLAKE_SCHEMA=RAW
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
ALPHA_VANTAGE_API_KEY=your_key
```

**Run pipelines:**
```bash
python extract/extract_alpha_vantage.py
python extract/scrape_canon_news.py
python extract/scrape_canon_ir.py
cd dbt && dbt run --profiles-dir . && dbt test --profiles-dir .
cd ../streamlit && streamlit run app.py
```

## Repository Structure

```
.
├── .github/workflows/    # GitHub Actions pipelines
├── extract/              # Extraction scripts (API + scrapers)
├── dbt/                  # dbt project (staging + mart models)
├── streamlit/            # Streamlit dashboard app
├── knowledge/            # Knowledge base (raw sources + wiki pages)
├── docs/                 # Proposal, job posting, slides
├── .env.example          # Required environment variables
├── .gitignore
├── CLAUDE.md             # Project context + knowledge base query conventions
└── README.md
```
