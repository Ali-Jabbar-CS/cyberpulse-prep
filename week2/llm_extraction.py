import asyncio
import sys
import json
import os
from crawl4ai import AsyncWebCrawler, LLMConfig, CrawlerRunConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Article(BaseModel):
    title: str
    url: str
    summary: str
    category: str

async def extract_with_llm():
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
        - summary: a brief description of the article
        - category: one of [Vulnerability, Ransomware, APT, Data Breach, Other]
        Return only real articles, not navigation links or ads.
        """
    )

    config = CrawlerRunConfig(extraction_strategy=strategy)

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://thehackernews.com",
            config=config
        )

        # Debug info
        print(f"Success: {result.success}")
        print(f"Error message: {result.error_message}")
        print(f"Extracted content type: {type(result.extracted_content)}")
        print(f"Extracted content preview: {str(result.extracted_content)[:200]}")

        if result.extracted_content:
            try:
                articles = json.loads(result.extracted_content)
                print(f"\nExtracted {len(articles)} articles\n")
                for article in articles[:3]:
                    print(f"Title:    {article.get('title')}")
                    print(f"URL:      {article.get('url')}")
                    print(f"Category: {article.get('category')}")
                    print(f"Summary:  {article.get('summary', '')[:100]}...")
                    print()
            except json.JSONDecodeError as e:
                print(f"JSON parse error: {e}")
                print(f"Raw content: {result.extracted_content[:500]}")
        else:
            print("\nNo extracted content — LLM call may have failed")
            print("Check your API key is set correctly:")
            print(f"API key loaded: {'Yes' if os.getenv("ANTHROPIC_API_KEY") else 'NO - KEY NOT FOUND'}")

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

asyncio.run(extract_with_llm())