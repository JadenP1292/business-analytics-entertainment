"""
Canon USA Newsroom Scraper → Snowflake RAW
Scrapes press releases and news articles from Canon USA's newsroom.
Feeds both the Snowflake raw layer and the knowledge base (knowledge/raw/).

Required env vars:
  SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_PASSWORD,
  SNOWFLAKE_WAREHOUSE, SNOWFLAKE_DATABASE, SNOWFLAKE_SCHEMA (default: RAW)
"""

import os
import re
import sys
import logging
import hashlib
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
log = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

SOURCES = [
    {
        "name": "Canon USA Newsroom",
        "url": "https://www.usa.canon.com/newsroom",
        "base_url": "https://www.usa.canon.com",
    },
    {
        "name": "Canon Global News",
        "url": "https://global.canon/en/news/index.html",
        "base_url": "https://global.canon",
    },
]

# Save raw scraped files to knowledge base
KNOWLEDGE_RAW_DIR = Path(__file__).parent.parent / "knowledge" / "raw"

DDL = """
CREATE TABLE IF NOT EXISTS CANON_NEWS (
    article_id       VARCHAR(64)       NOT NULL PRIMARY KEY,
    scraped_date     DATE              NOT NULL,
    scraped_at       TIMESTAMP_NTZ     NOT NULL,
    source_name      VARCHAR(200),
    source_url       VARCHAR(1000),
    article_url      VARCHAR(1000),
    headline         VARCHAR(1000),
    publish_date     DATE,
    body_text        VARCHAR(65535),
    article_type     VARCHAR(100),
    word_count       NUMBER(10)
);
"""

MERGE_SQL = """
MERGE INTO CANON_NEWS AS tgt
USING (SELECT $1 AS article_id, $2 AS scraped_date, $3 AS scraped_at,
              $4 AS source_name, $5 AS source_url, $6 AS article_url,
              $7 AS headline, $8 AS publish_date, $9 AS body_text,
              $10 AS article_type, $11 AS word_count
       FROM VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)) AS src
ON tgt.article_id = src.article_id
WHEN MATCHED THEN UPDATE SET
    scraped_date = src.scraped_date,
    scraped_at   = src.scraped_at,
    body_text    = src.body_text,
    word_count   = src.word_count
WHEN NOT MATCHED THEN INSERT VALUES (
    src.article_id, src.scraped_date, src.scraped_at, src.source_name,
    src.source_url, src.article_url, src.headline, src.publish_date,
    src.body_text, src.article_type, src.word_count
);
"""


def make_article_id(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()[:16]


def fetch_page(url: str, timeout: int = 30) -> BeautifulSoup | None:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "lxml")
    except requests.RequestException as e:
        log.warning("Failed to fetch %s: %s", url, e)
        return None


def scrape_canon_usa_newsroom(source: dict) -> list[dict]:
    """Scrape article links and content from Canon USA newsroom."""
    articles = []
    soup = fetch_page(source["url"])
    if not soup:
        return articles

    # Find article links — Canon USA uses anchor tags with /newsroom/ paths
    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/newsroom/" in href and href != source["url"]:
            full_url = urljoin(source["base_url"], href)
            links.add(full_url)

    log.info("Found %d article links on %s", len(links), source["url"])

    for article_url in list(links)[:50]:  # cap at 50 per run
        article = scrape_article(article_url, source)
        if article:
            articles.append(article)

    return articles


def scrape_canon_global_news(source: dict) -> list[dict]:
    """Scrape article links from Canon Global news index."""
    articles = []
    soup = fetch_page(source["url"])
    if not soup:
        return articles

    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/news/" in href and href.endswith(".html") and "index" not in href:
            full_url = urljoin(source["base_url"], href)
            links.add(full_url)

    log.info("Found %d article links on %s", len(links), source["url"])

    for article_url in list(links)[:50]:
        article = scrape_article(article_url, source)
        if article:
            articles.append(article)

    return articles


def scrape_article(url: str, source: dict) -> dict | None:
    soup = fetch_page(url)
    if not soup:
        return None

    # Extract headline
    headline = None
    for tag in ["h1", "h2"]:
        el = soup.find(tag)
        if el and el.get_text(strip=True):
            headline = el.get_text(strip=True)
            break

    if not headline:
        return None

    # Extract body text — remove nav/footer/script noise
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    body_text = soup.get_text(separator=" ", strip=True)
    body_text = re.sub(r"\s{2,}", " ", body_text)[:65000]
    word_count = len(body_text.split())

    # Try to extract a publish date
    publish_date = None
    date_el = soup.find("time")
    if date_el:
        dt_str = date_el.get("datetime", "") or date_el.get_text(strip=True)
        try:
            publish_date = datetime.strptime(dt_str[:10], "%Y-%m-%d").date()
        except ValueError:
            pass

    # Detect article type from URL
    article_type = "news"
    if "press" in url.lower():
        article_type = "press-release"
    elif "product" in url.lower():
        article_type = "product-announcement"

    return {
        "article_id": make_article_id(url),
        "scraped_date": date.today(),
        "scraped_at": datetime.utcnow(),
        "source_name": source["name"],
        "source_url": source["url"],
        "article_url": url,
        "headline": headline[:1000],
        "publish_date": publish_date,
        "body_text": body_text,
        "article_type": article_type,
        "word_count": word_count,
    }


def save_to_knowledge_base(articles: list[dict]):
    """Save raw scraped content to knowledge/raw/ for knowledge base use."""
    KNOWLEDGE_RAW_DIR.mkdir(parents=True, exist_ok=True)
    for article in articles:
        filename = f"canon_news_{article['article_id']}.md"
        filepath = KNOWLEDGE_RAW_DIR / filename
        if filepath.exists():
            continue  # Don't overwrite existing raw files
        content = (
            f"# {article['headline']}\n\n"
            f"**Source:** {article['source_name']}\n"
            f"**URL:** {article['article_url']}\n"
            f"**Date:** {article.get('publish_date', 'Unknown')}\n"
            f"**Type:** {article['article_type']}\n"
            f"**Scraped:** {article['scraped_date']}\n\n"
            f"---\n\n"
            f"{article['body_text']}\n"
        )
        filepath.write_text(content, encoding="utf-8")
    log.info("Saved %d articles to %s", len(articles), KNOWLEDGE_RAW_DIR)


def get_snowflake_conn():
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        schema=os.environ.get("SNOWFLAKE_SCHEMA", "RAW"),
    )


def load_to_snowflake(articles: list[dict]) -> int:
    if not articles:
        log.warning("No articles to load.")
        return 0

    with get_snowflake_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(DDL)
            log.info("Table CANON_NEWS ensured.")
            for a in articles:
                row = (
                    a["article_id"], a["scraped_date"], a["scraped_at"],
                    a["source_name"], a["source_url"], a["article_url"],
                    a["headline"], a["publish_date"], a["body_text"],
                    a["article_type"], a["word_count"],
                )
                cur.execute(MERGE_SQL, row)
            log.info("Loaded %d articles into CANON_NEWS.", len(articles))
            return len(articles)


def main():
    log.info("Starting Canon news scrape for %s", date.today())

    all_articles = []
    seen_ids = set()

    scrapers = [
        (SOURCES[0], scrape_canon_usa_newsroom),
        (SOURCES[1], scrape_canon_global_news),
    ]

    for source, scraper_fn in scrapers:
        articles = scraper_fn(source)
        for a in articles:
            if a["article_id"] not in seen_ids:
                seen_ids.add(a["article_id"])
                all_articles.append(a)

    log.info("Total unique articles scraped: %d", len(all_articles))

    save_to_knowledge_base(all_articles)
    loaded = load_to_snowflake(all_articles)

    log.info("Done. %d articles loaded to Snowflake RAW.CANON_NEWS", loaded)


if __name__ == "__main__":
    main()
