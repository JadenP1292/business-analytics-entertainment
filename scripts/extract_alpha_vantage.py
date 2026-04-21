"""
Alpha Vantage Stock Data → Snowflake RAW
Extracts daily adjusted stock prices and company fundamentals for Canon and
key competitors (Sony, Nikon, HP) to support competitive pricing analytics.

Required env vars:
  ALPHA_VANTAGE_API_KEY, SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_PASSWORD,
  SNOWFLAKE_WAREHOUSE, SNOWFLAKE_DATABASE, SNOWFLAKE_SCHEMA (default: RAW)

Free tier: 25 requests/day, 5 requests/minute.
This script uses 10 requests max (5 tickers × price + 5 tickers × overview).
"""

import os
import time
import logging
from datetime import date, datetime

import requests
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
log = logging.getLogger(__name__)

API_KEY = os.environ["ALPHA_VANTAGE_API_KEY"]
BASE_URL = "https://www.alphavantage.co/query"

# Canon competitors in imaging, printing, and document solutions
TICKERS = [
    {"ticker": "SONY",  "name": "Sony Group Corporation"},
    {"ticker": "NINOY", "name": "Nikon Corporation"},
    {"ticker": "HPQ",   "name": "HP Inc."},
    {"ticker": "XRX",   "name": "Xerox Holdings Corporation"},
    {"ticker": "KODK",  "name": "Eastman Kodak Company"},
]

PRICE_DDL = """
CREATE OR REPLACE TABLE STOCK_PRICES_DAILY (
    trade_date          DATE          NOT NULL,
    ticker              VARCHAR(10)   NOT NULL,
    open_price          NUMBER(14,4),
    high_price          NUMBER(14,4),
    low_price           NUMBER(14,4),
    close_price         NUMBER(14,4),
    volume              NUMBER(18),
    extracted_at        TIMESTAMP_NTZ NOT NULL,
    PRIMARY KEY (trade_date, ticker)
);
"""

COMPANY_DDL = """
CREATE TABLE IF NOT EXISTS COMPANY_OVERVIEW (
    ticker                  VARCHAR(10)   NOT NULL PRIMARY KEY,
    company_name            VARCHAR(300),
    sector                  VARCHAR(100),
    industry                VARCHAR(200),
    country                 VARCHAR(50),
    currency                VARCHAR(10),
    exchange                VARCHAR(50),
    market_capitalization   NUMBER(20),
    pe_ratio                NUMBER(12,4),
    forward_pe              NUMBER(12,4),
    peg_ratio               NUMBER(12,4),
    book_value              NUMBER(14,4),
    dividend_yield          NUMBER(10,6),
    eps                     NUMBER(14,4),
    revenue_ttm             NUMBER(20),
    gross_profit_ttm        NUMBER(20),
    ebitda                  NUMBER(20),
    week_52_high            NUMBER(14,4),
    week_52_low             NUMBER(14,4),
    analyst_target_price    NUMBER(14,4),
    analyst_rating_buy      NUMBER(10),
    analyst_rating_hold     NUMBER(10),
    analyst_rating_sell     NUMBER(10),
    description             VARCHAR(65535),
    updated_at              TIMESTAMP_NTZ NOT NULL
);
"""

PRICE_MERGE = """
MERGE INTO STOCK_PRICES_DAILY AS tgt
USING (SELECT $1::DATE AS trade_date, $2 AS ticker, $3 AS open_price,
              $4 AS high_price, $5 AS low_price, $6 AS close_price,
              $7 AS volume, $8 AS extracted_at
       FROM VALUES (%s, %s, %s, %s, %s, %s, %s, %s)) AS src
ON tgt.trade_date = src.trade_date AND tgt.ticker = src.ticker
WHEN MATCHED THEN UPDATE SET
    close_price = src.close_price,
    volume = src.volume,
    extracted_at = src.extracted_at
WHEN NOT MATCHED THEN INSERT VALUES (
    src.trade_date, src.ticker, src.open_price, src.high_price,
    src.low_price, src.close_price, src.volume, src.extracted_at
);
"""

COMPANY_MERGE = """
MERGE INTO COMPANY_OVERVIEW AS tgt
USING (SELECT $1 AS ticker, $2 AS company_name, $3 AS sector,
              $4 AS industry, $5 AS country, $6 AS currency, $7 AS exchange,
              $8 AS market_capitalization, $9 AS pe_ratio, $10 AS forward_pe,
              $11 AS peg_ratio, $12 AS book_value, $13 AS dividend_yield,
              $14 AS eps, $15 AS revenue_ttm, $16 AS gross_profit_ttm,
              $17 AS ebitda, $18 AS week_52_high, $19 AS week_52_low,
              $20 AS analyst_target_price, $21 AS analyst_rating_buy,
              $22 AS analyst_rating_hold, $23 AS analyst_rating_sell,
              $24 AS description, $25 AS updated_at
       FROM VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)) AS src
ON tgt.ticker = src.ticker
WHEN MATCHED THEN UPDATE SET
    company_name = src.company_name, sector = src.sector, industry = src.industry,
    market_capitalization = src.market_capitalization, pe_ratio = src.pe_ratio,
    week_52_high = src.week_52_high, week_52_low = src.week_52_low,
    analyst_target_price = src.analyst_target_price,
    analyst_rating_buy = src.analyst_rating_buy,
    analyst_rating_hold = src.analyst_rating_hold,
    analyst_rating_sell = src.analyst_rating_sell,
    updated_at = src.updated_at
WHEN NOT MATCHED THEN INSERT VALUES (
    src.ticker, src.company_name, src.sector, src.industry, src.country,
    src.currency, src.exchange, src.market_capitalization, src.pe_ratio,
    src.forward_pe, src.peg_ratio, src.book_value, src.dividend_yield,
    src.eps, src.revenue_ttm, src.gross_profit_ttm, src.ebitda,
    src.week_52_high, src.week_52_low, src.analyst_target_price,
    src.analyst_rating_buy, src.analyst_rating_hold, src.analyst_rating_sell,
    src.description, src.updated_at
);
"""


def av_get(params: dict, pause: float = 12.0) -> dict | None:
    """Call Alpha Vantage with rate-limit pause (5 req/min free tier)."""
    params["apikey"] = API_KEY
    try:
        resp = requests.get(BASE_URL, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if "Note" in data:
            log.warning("Rate limit hit: %s", data["Note"])
            return None
        if "Error Message" in data:
            log.warning("API error: %s", data["Error Message"])
            return None
        return data
    except requests.RequestException as e:
        log.warning("Request failed: %s", e)
        return None
    finally:
        time.sleep(pause)


def fetch_daily_prices(ticker: str) -> list[tuple]:
    log.info("Fetching daily prices: %s", ticker)
    data = av_get({
        "function": "TIME_SERIES_DAILY",
        "symbol": ticker,
        "outputsize": "compact",  # last 100 trading days
    })
    if not data:
        return []

    series = data.get("Time Series (Daily)", {})
    now = datetime.utcnow()
    rows = []
    for trade_date_str, vals in series.items():
        rows.append((
            trade_date_str,
            ticker,
            float(vals.get("1. open", 0) or 0),
            float(vals.get("2. high", 0) or 0),
            float(vals.get("3. low", 0) or 0),
            float(vals.get("4. close", 0) or 0),
            int(float(vals.get("5. volume", 0) or 0)),
            now,
        ))
    log.info("  %d price rows for %s", len(rows), ticker)
    return rows


def fetch_company_overview(ticker: str) -> tuple | None:
    log.info("Fetching company overview: %s", ticker)
    data = av_get({"function": "OVERVIEW", "symbol": ticker})
    if not data or not data.get("Symbol"):
        return None

    def num(key):
        val = data.get(key)
        try:
            return float(val) if val and val != "None" else None
        except (ValueError, TypeError):
            return None

    return (
        ticker,
        data.get("Name"),
        data.get("Sector"),
        data.get("Industry"),
        data.get("Country"),
        data.get("Currency"),
        data.get("Exchange"),
        num("MarketCapitalization"),
        num("PERatio"),
        num("ForwardPE"),
        num("PEGRatio"),
        num("BookValue"),
        num("DividendYield"),
        num("EPS"),
        num("RevenueTTM"),
        num("GrossProfitTTM"),
        num("EBITDA"),
        num("52WeekHigh"),
        num("52WeekLow"),
        num("AnalystTargetPrice"),
        num("AnalystRatingBuy"),
        num("AnalystRatingHold"),
        num("AnalystRatingSell"),
        data.get("Description", "")[:65000],
        datetime.utcnow(),
    )


def get_snowflake_conn():
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        schema=os.environ.get("SNOWFLAKE_SCHEMA", "RAW"),
    )


def main():
    log.info("Starting Alpha Vantage extraction for %s", date.today())

    all_price_rows = []
    all_company_rows = []

    for company in TICKERS:
        ticker = company["ticker"]
        price_rows = fetch_daily_prices(ticker)
        all_price_rows.extend(price_rows)

        overview = fetch_company_overview(ticker)
        if overview:
            all_company_rows.append(overview)

    log.info("Total price rows: %d | Company rows: %d", len(all_price_rows), len(all_company_rows))

    with get_snowflake_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(PRICE_DDL)
            cur.execute(COMPANY_DDL)
            log.info("Tables ensured in Snowflake RAW.")

            for row in all_price_rows:
                cur.execute(PRICE_MERGE, row)
            log.info("Loaded %d price rows → STOCK_PRICES_DAILY", len(all_price_rows))

            for row in all_company_rows:
                cur.execute(COMPANY_MERGE, row)
            log.info("Loaded %d company rows → COMPANY_OVERVIEW", len(all_company_rows))

    log.info("Done.")


if __name__ == "__main__":
    main()
