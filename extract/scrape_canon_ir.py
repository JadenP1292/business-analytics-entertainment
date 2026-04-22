"""
Canon Investor Relations Scraper → knowledge/raw/
Scrapes earnings press releases and IR content from Canon's global IR pages.
Saves to knowledge/raw/ as markdown for the knowledge base.
"""

import os
import re
import logging
import hashlib
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
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

KNOWLEDGE_RAW_DIR = Path(__file__).parent.parent / "knowledge" / "raw"

IR_SOURCES = [
    {
        "name": "Canon Global IR News",
        "url": "https://global.canon/en/ir/news/index.html",
        "base_url": "https://global.canon",
        "link_pattern": "/en/ir/news/",
    },
    {
        "name": "Canon Global Financial Results",
        "url": "https://global.canon/en/ir/financial/index.html",
        "base_url": "https://global.canon",
        "link_pattern": "/en/ir/",
    },
]


def make_id(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()[:16]


def fetch_page(url: str) -> BeautifulSoup | None:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "lxml")
    except requests.RequestException as e:
        log.warning("Failed to fetch %s: %s", url, e)
        return None


def scrape_article(url: str, source_name: str) -> dict | None:
    soup = fetch_page(url)
    if not soup:
        return None

    headline = None
    for tag in ["h1", "h2", "h3"]:
        el = soup.find(tag)
        if el and el.get_text(strip=True):
            headline = el.get_text(strip=True)
            break

    if not headline:
        return None

    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    body = re.sub(r"\s{2,}", " ", soup.get_text(separator=" ", strip=True))[:60000]

    publish_date = None
    time_el = soup.find("time")
    if time_el:
        try:
            publish_date = datetime.strptime(
                (time_el.get("datetime", "") or time_el.get_text(strip=True))[:10],
                "%Y-%m-%d"
            ).date()
        except ValueError:
            pass

    return {
        "article_id": make_id(url),
        "headline": headline[:500],
        "url": url,
        "source": source_name,
        "publish_date": str(publish_date) if publish_date else "Unknown",
        "scraped_date": str(date.today()),
        "body": body,
    }


def save_to_knowledge_raw(article: dict):
    KNOWLEDGE_RAW_DIR.mkdir(parents=True, exist_ok=True)
    filepath = KNOWLEDGE_RAW_DIR / f"canon_ir_{article['article_id']}.md"
    if filepath.exists():
        return
    content = (
        f"# {article['headline']}\n\n"
        f"**Source:** {article['source']}\n"
        f"**URL:** {article['url']}\n"
        f"**Date:** {article['publish_date']}\n"
        f"**Scraped:** {article['scraped_date']}\n\n"
        f"---\n\n"
        f"{article['body']}\n"
    )
    filepath.write_text(content, encoding="utf-8")
    log.info("Saved %s", filepath.name)


def main():
    log.info("Starting Canon IR scrape for %s", date.today())
    all_articles = []
    seen_ids = set()

    for source in IR_SOURCES:
        soup = fetch_page(source["url"])
        if not soup:
            continue

        links = set()
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if source["link_pattern"] in href and href != source["url"]:
                links.add(urljoin(source["base_url"], href))

        log.info("Found %d links on %s", len(links), source["url"])

        for url in list(links)[:10]:
            article = scrape_article(url, source["name"])
            if article and article["article_id"] not in seen_ids:
                seen_ids.add(article["article_id"])
                all_articles.append(article)

    for article in all_articles:
        save_to_knowledge_raw(article)

    log.info("Done. Saved %d IR articles to knowledge/raw/", len(all_articles))


if __name__ == "__main__":
    main()
