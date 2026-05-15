import asyncio
import json
import os
import sys
from datetime import datetime, timezone

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Sources to crawl — easy to add more later
SOURCES = [
    "https://thehackernews.com",
    "https://bleepingcomputer.com",
    "https://krebsonsecurity.com",
]


class Article(BaseModel):
    title: str
    url: str
    summary: str
    category: str


async def crawl_source(crawler, url):
    print(f"  Crawling {url}...")

    strategy = LLMExtractionStrategy(
        llm_config=LLMConfig(
            provider="anthropic/claude-haiku-4-5-20251001",
            api_token=ANTHROPIC_API_KEY,
        ),
        schema=Article.model_json_schema(),
        extraction_type="schema",
        instruction=(
            "Extract cybersecurity news articles from this page. "
            "For each article extract: title, url, summary "
            "(2 sentences max), and category "
            "(one of: malware, vulnerability, breach, "
            "ransomware, nation-state, other)."
        ),
    )

    config = CrawlerRunConfig(
        extraction_strategy=strategy
    )

    try:
        result = await crawler.arun(
            url=url,
            config=config,
        )

        if not result.extracted_content:
            print(f"  ⚠️  No content extracted from {url}")
            return []

        articles = json.loads(result.extracted_content)

        # Attach source metadata to each article
        for article in articles:
            article["source"] = url
            article["scraped_at"] = (
                datetime.now(timezone.utc).isoformat()
            )

        print(f"  ✅ {url} — {len(articles)} articles")

        return articles

    except Exception as e:
        print(f"  ❌ Failed to crawl {url}: {e}")
        return []


async def crawl_all_sources():
    print("🔍 Starting CyberPulse crawler...")
    print(f"   Sources: {len(SOURCES)}")
    print(
        f"   Time: "
        f"{datetime.now(timezone.utc).isoformat()}\n"
    )

    all_articles = []

    async with AsyncWebCrawler() as crawler:
        # Crawl all sources simultaneously
        tasks = [
            crawl_source(crawler, url)
            for url in SOURCES
        ]

        results = await asyncio.gather(*tasks)

        for source_articles in results:
            all_articles.extend(source_articles)

    # Deduplicate by URL
    seen_urls = set()
    unique_articles = []

    for article in all_articles:
        url = article.get("url", "")

        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_articles.append(article)

    print(
        f"\n📦 Total articles collected: "
        f"{len(unique_articles)}"
    )

    return unique_articles


async def main():
    articles = await crawl_all_sources()

    # Save to file so extractor.py can load it
    output_path = os.path.join(
        os.path.dirname(__file__),
        "crawled_articles.json",
    )

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            articles,
            f,
            indent=2,
            ensure_ascii=False,
        )

    print("💾 Saved to capstone/crawled_articles.json")

    return articles


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(
            asyncio.WindowsProactorEventLoopPolicy()
        )

    asyncio.run(main())
