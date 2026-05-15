import asyncio
import sys
import os
from datetime import datetime

# Import all four pipeline modules
from crawler import crawl_all_sources
from extractor import enrich_all_articles
from analyzer import analyze_all_articles
from reporter import generate_report


async def run_pipeline(limit=10):
    start_time = datetime.now()

    print("=" * 70)
    print("  CYBERPULSE — AI-Powered Threat Intelligence Pipeline")
    print("  ObjectSecurity Internship Project — Ali Jabbar")
    print(f"  Started: {start_time.strftime('%Y-%m-%d %H:%M local')}")
    print("=" * 70)

    # Stage 1 — Crawl
    print("\n[1/4] 🔍 CRAWLING SOURCES...")
    articles = await crawl_all_sources()
    if not articles:
        print("❌ No articles crawled. Exiting.")
        return

    # Stage 2 — Enrich
    print("\n[2/4] 🔬 ENRICHING ARTICLES...")
    enriched = enrich_all_articles(articles, limit=limit)
    if not enriched:
        print("❌ Enrichment failed. Exiting.")
        return

    # Truncate summaries for clean JSON
    for article in enriched:
        if "summary" in article and article["summary"]:
            article["summary"] = article["summary"][:150].rstrip() + "..."

    # Stage 3 — Analyze
    print("\n[3/4] 🧠 ANALYZING THREATS...")
    analyzed = analyze_all_articles(enriched)
    if not analyzed:
        print("❌ Analysis failed. Exiting.")
        return

    # Stage 4 — Report
    print("\n[4/4] 📝 GENERATING REPORT...")
    generate_report(analyzed)

    # Pipeline complete
    end_time = datetime.now()
    duration = (end_time - start_time).seconds

    print(f"\n{'=' * 70}")
    print(f"  ✅ CYBERPULSE COMPLETE")
    print(f"  Duration:  {duration} seconds")
    print(
        f"  Articles:  {len(articles)} crawled → {len(enriched)} enriched → {len(analyzed)} analyzed")
    print(f"  Outputs:   capstone/threat_report.json")
    print(f"             capstone/threat_report.txt")
    print(f"{'=' * 70}\n")


if __name__ == "__main__":
    # Optional: pass limit as command line argument
    # python main.py 20  ← analyzes 20 articles
    # python main.py     ← defaults to 10
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 10

    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(run_pipeline(limit=limit))
