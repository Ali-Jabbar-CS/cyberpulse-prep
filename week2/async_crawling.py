import asyncio
import sys
import json
import os
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai import LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Article(BaseModel):
    title: str
    url: str
    summary: str
    category: str

# Multiple security news sources — this is how CyberPulse will work
SOURCES = [
    "https://thehackernews.com",
    "https://www.bleepingcomputer.com",
    "https://krebsonsecurity.com",
]

async def crawl_single(crawler, url, config):
    """Crawl one URL and return extracted articles."""
    print(f"Starting: {url}")
    result = await crawler.arun(url=url, config=config)

    if result.extracted_content:
        try:
            articles = json.loads(result.extracted_content)
            # Filter out any error entries
            valid = [a for a in articles if a.get("title") and a.get("title") != "None"]
            print(f"Done: {url} → {len(valid)} articles")
            return {"source": url, "articles": valid}
        except json.JSONDecodeError:
            print(f"Parse error: {url}")
            return {"source": url, "articles": []}
    else:
        print(f"No content: {url}")
        return {"source": url, "articles": []}


async def crawl_all_sources():
    strategy = LLMExtractionStrategy(
        llm_config=LLMConfig(
            provider="anthropic/claude-haiku-4-5-20251001",
            api_token=os.getenv("ANTHROPIC_API_KEY")
        ),
        schema=Article.model_json_schema(),
        extraction_type="schema",
        instruction="""
        Extract all news articles from this cybersecurity news page.
        For each article find:
        - title: the article headline
        - url: the link to the full article  
        - summary: a brief description
        - category: one of [Vulnerability, Ransomware, APT, Data Breach, Other]
        Return only real articles, not navigation links or ads.
        """
    )

    config = CrawlerRunConfig(extraction_strategy=strategy)

    # One crawler instance shared across all requests
    async with AsyncWebCrawler() as crawler:
        # asyncio.gather runs all three crawls simultaneously
        tasks = [crawl_single(crawler, url, config) for url in SOURCES]
        results = await asyncio.gather(*tasks)

    # Flatten all articles from all sources
    all_articles = []
    for source_result in results:
        all_articles.extend(source_result["articles"])

    print(f"\n--- FINAL RESULTS ---")
    print(f"Sources crawled: {len(SOURCES)}")
    print(f"Total articles: {len(all_articles)}")

    # Show breakdown by category
    categories = {}
    for article in all_articles:
        cat = article.get("category", "Unknown")
        categories[cat] = categories.get(cat, 0) + 1

    print("\nBy category:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: {count}")

    # Save everything to disk
    with open("all_articles.json", "w") as f:
        json.dump(all_articles, f, indent=2)
    print("\nSaved to all_articles.json")

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

asyncio.run(crawl_all_sources())