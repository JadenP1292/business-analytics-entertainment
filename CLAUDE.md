# CLAUDE.md

## Project Overview

Portfolio project for ISBA 4715 (Analytics Engineering) demonstrating end-to-end data pipeline and analytics skills. The project targets a Data Analytics Analyst role at Canon U.S.A., focusing on SQL, Python, data pipelines, and dashboard development.

## Target Role

**Position:** Data Analytics Analyst
**Company:** Canon U.S.A., Inc.
**Location:** Melville, NY
**Key Skills:** SQL, Python, Power BI, data pipelines, revenue/pricing analytics

## Tech Stack

- **Data Warehouse:** Snowflake
- **Transformation:** dbt
- **Orchestration:** GitHub Actions
- **Dashboard:** Streamlit (deployed to Streamlit Community Cloud)
- **Knowledge Base:** Claude Code (scrape, summarize, query)

## Project Structure

```
├── docs/
│   ├── job-posting.pdf      # Target job posting
│   └── proposal.md          # Project proposal
├── dbt/                     # dbt project (Milestone 01)
├── extract/                 # Python extraction scripts
├── streamlit/               # Dashboard app (Milestone 02)
├── knowledge/               # Knowledge base (Milestone 02)
│   ├── raw/                 # Scraped source documents
│   └── wiki/                # Synthesized wiki pages
└── .github/workflows/       # GitHub Actions pipelines
```

## Milestones

1. **Proposal (Apr 13):** Job posting + reflection + repo setup
2. **Milestone 01 (Apr 27):** API source extraction, dbt models, GitHub Actions pipeline
3. **Milestone 02 (May 4):** Web scrape source, Streamlit dashboard, knowledge base
4. **Final (May 11):** Updated resume, final interview

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run API extraction (Alpha Vantage → Snowflake RAW)
python extract/extract_alpha_vantage.py

# Run web scrape (Canon News → Snowflake RAW + knowledge/raw/)
python extract/scrape_canon_news.py
```

## Milestone 01 Status

### Verified Complete
- Proposal (`docs/proposal.md` + `docs/job-posting.pdf`)
- Repo structure, `.gitignore`, `CLAUDE.md`
- Star schema design (`docs/api-star-schema.md`) — Alpha Vantage stock data
- `requirements.txt` with all dependencies
- `.env.example` documenting all required secrets
- Source 1: `extract/extract_alpha_vantage.py` — Alpha Vantage API → Snowflake `RAW.STOCK_PRICES_DAILY` + `RAW.COMPANY_OVERVIEW`
  - Tracks: Canon (CAJ), Sony (SONY), Nikon (NINOY), HP (HPQ), Xerox (XRX)
- Source 2: `extract/scrape_canon_news.py` — Canon USA Newsroom → Snowflake `RAW.CANON_NEWS` + `knowledge/raw/`
- GitHub Actions: `.github/workflows/extract_alpha_vantage.yml` (weekdays 21:00 UTC)
- GitHub Actions: `.github/workflows/scrape_canon_news.yml` (daily 9:00 UTC)
- Data pipeline diagram in `README.md` (Mermaid flowchart)

### Remaining Before Submission (Apr 27)
- Get Alpha Vantage API key at alphavantage.co/support/#api-key (free, any email)
- Configure GitHub repository secrets (ALPHA_VANTAGE_API_KEY, SNOWFLAKE_*)
- Run scripts end-to-end with real credentials to verify Snowflake loads
- Commit all new files and push to GitHub
- Verify GitHub Actions trigger via workflow_dispatch

### Next Recommended Action
Get Alpha Vantage API key, populate `.env`, then run `python extract/extract_alpha_vantage.py` locally to confirm end-to-end connectivity.
