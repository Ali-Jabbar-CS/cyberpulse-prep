import os
import json
from dotenv import load_dotenv

load_dotenv()
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

from firecrawl import FirecrawlApp

def get_client():
    if not FIRECRAWL_API_KEY:
        print("⚠️  No FIRECRAWL_API_KEY found in .env — running in demo mode")
        return None
    return FirecrawlApp(api_key=FIRECRAWL_API_KEY)


def demo_single_scrape(app):
    print("\n--- DEMO 1: Single Page Scrape ---")

    if app is None:
        print("Demo mode: Firecrawl would return clean markdown like this:")
        print("# The Hacker News\n## Critical OpenSSL Vulnerability...\n[article content]")
        return

    result = app.scrape("https://thehackernews.com", formats=["markdown"])

    markdown = result.markdown or ""
    print(f"Scraped {len(markdown)} chars of clean markdown")
    print(markdown[:500])


def demo_site_crawl(app):
    print("\n--- DEMO 2: Full Site Crawl ---")

    if app is None:
        print("Demo mode: Firecrawl would crawl all pages under a domain")
        print("Returns: list of {url, markdown} for each page found")
        return

    result = app.crawl("https://thehackernews.com", limit=5, scrape_options={"formats": ["markdown"]})

    pages = result.data or []
    print(f"Crawled {len(pages)} pages")
    for page in pages:
        url = page.metadata.url if page.metadata else "unknown"
        content_len = len(page.markdown or "")
        print(f"  {url} — {content_len} chars")


def demo_structured_extraction(app):
    print("\n--- DEMO 3: Structured Data Extraction ---")

    if app is None:
        print("Demo mode: Firecrawl extract would return structured JSON like:")
        mock = {
            "articles": [
                {
                    "title": "Critical RCE in Apache Struts",
                    "threat_level": "Critical",
                    "cve_id": "CVE-2024-53677",
                    "affected_systems": ["Apache Struts 2.0-6.3"]
                }
            ]
        }
        print(json.dumps(mock, indent=2))
        return

    result = app.extract(
        ["https://thehackernews.com"],
        prompt="""Extract cybersecurity articles from this page. 
        For each article return: title, threat_level (Critical/High/Medium/Low), 
        cve_id if mentioned, affected_systems as a list."""
    )

    print(json.dumps(result.data, indent=2))


def demo_comparison():
    print("\n--- DEMO 4: Crawl4AI vs Firecrawl Comparison ---")

    comparison = {
        "task": "Scrape THN and extract article titles",
        "crawl4ai_approach": {
            "code_lines": "~30",
            "runs_on": "Your machine",
            "requires": "AsyncWebCrawler + LLMExtractionStrategy + Anthropic API key",
            "data_leaves_machine": False,
            "cost": "Only Anthropic API tokens"
        },
        "firecrawl_approach": {
            "code_lines": "~10",
            "runs_on": "Firecrawl cloud servers",
            "requires": "FirecrawlApp + Firecrawl API key",
            "data_leaves_machine": True,
            "cost": "Firecrawl credits + optional Anthropic tokens",
            "best_for": "Speed, JS-heavy sites, quick prototypes, startups"
        }
    }

    print(json.dumps(comparison, indent=2))
    print("\n💡 Crawl4AI is the right choice.")
    print("   Defense work = sensitive targets. Data stays local.")

def run_demos():
    app = get_client()

    demo_single_scrape(app)
    demo_site_crawl(app)
    demo_structured_extraction(app)
    demo_comparison()

    print("\n✅ Firecrawl overview complete!")

if __name__ == "__main__":
    run_demos()