import json
import os
from datetime import datetime, timezone


def calculate_stats(articles):
    """Summarize threat levels across all analyzed articles."""

    stats = {
        "total_articles": len(articles),
        "by_threat_level": {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Unknown": 0},
        "by_attack_type": {},
        "by_sector": {},
        "cves_identified": [],
        "patch_available_count": 0,
        "top_priority_articles": []
    }

    for article in articles:
        analysis = article.get("analysis", {})

        # Count threat levels
        level = analysis.get("threat_level", "Unknown")
        stats["by_threat_level"][level] = stats["by_threat_level"].get(
            level, 0) + 1

        # Count attack types
        attack = article.get("attack_type", "Other")
        stats["by_attack_type"][attack] = stats["by_attack_type"].get(
            attack, 0) + 1

        # Count affected sectors
        for sector in analysis.get("affected_sectors", []):
            stats["by_sector"][sector] = stats["by_sector"].get(sector, 0) + 1

        # Collect all CVEs
        for cve in article.get("cve_ids", []):
            if cve not in stats["cves_identified"]:
                stats["cves_identified"].append(cve)

        # Count patches available
        if article.get("patch_available", False):
            stats["patch_available_count"] += 1

    # Top 3 highest priority articles
    sorted_articles = sorted(
        articles,
        key=lambda x: x.get("analysis", {}).get("priority_score", 0),
        reverse=True
    )
    stats["top_priority_articles"] = [
        {
            "title": a.get("title", "")[:80],
            "priority_score": a.get("analysis", {}).get("priority_score", 0),
            "threat_level": a.get("analysis", {}).get("threat_level", "Unknown"),
            "url": a.get("url", "")
        }
        for a in sorted_articles[:3]
    ]

    return stats


def format_text_report(articles, stats):
    """Generate a human-readable threat intelligence report."""

    lines = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M local")

    # Header
    lines.append("=" * 70)
    lines.append("           CYBERPULSE THREAT INTELLIGENCE REPORT")
    lines.append(f"           Generated: {now}")
    lines.append("=" * 70)

    # Executive Summary
    lines.append("\n📊 EXECUTIVE SUMMARY")
    lines.append("-" * 40)
    lines.append(f"  Articles Analyzed:  {stats['total_articles']}")
    lines.append(
        f"  Critical Threats:   {stats['by_threat_level'].get('Critical', 0)}")
    lines.append(
        f"  High Threats:       {stats['by_threat_level'].get('High', 0)}")
    lines.append(
        f"  Medium Threats:     {stats['by_threat_level'].get('Medium', 0)}")
    lines.append(
        f"  Low Threats:        {stats['by_threat_level'].get('Low', 0)}")
    lines.append(f"  CVEs Identified:    {len(stats['cves_identified'])}")
    lines.append(f"  Patches Available:  {stats['patch_available_count']}")

    # CVE List
    if stats["cves_identified"]:
        lines.append(f"\n  CVEs: {', '.join(stats['cves_identified'])}")

    # Top Priority Threats
    lines.append("\n\n🚨 TOP PRIORITY THREATS")
    lines.append("-" * 40)
    for i, article in enumerate(stats["top_priority_articles"]):
        lines.append(
            f"\n  #{i+1} [{article['threat_level']}] Priority {article['priority_score']}/10")
        lines.append(f"  {article['title']}")
        lines.append(f"  {article['url']}")

    # Full Article Breakdown
    lines.append("\n\n📋 FULL THREAT BREAKDOWN")
    lines.append("-" * 40)

    for i, article in enumerate(articles):
        analysis = article.get("analysis", {})

        lines.append(f"\n{'─' * 60}")
        lines.append(f"[{i+1}] {article.get('title', 'No title')}")
        lines.append(f"    Source:     {article.get('source', 'Unknown')}")
        lines.append(f"    URL:        {article.get('url', 'N/A')}")
        lines.append(f"    Threat:     {analysis.get('threat_level', 'Unknown')} "
                     f"(Priority {analysis.get('priority_score', 'N/A')}/10)")
        lines.append(
            f"    Attack:     {article.get('attack_type', 'Unknown')}")

        cves = article.get("cve_ids", [])
        if cves:
            lines.append(f"    CVEs:       {', '.join(cves)}")

        lines.append(
            f"    Systems:    {', '.join(analysis.get('affected_systems', ['Unknown']))}")
        lines.append(
            f"    Sectors:    {', '.join(analysis.get('affected_sectors', ['Unknown']))}")
        lines.append(
            f"\n    SUMMARY:    {analysis.get('threat_summary', 'N/A')}")
        lines.append(
            f"\n    ACTION:     {analysis.get('recommended_action', 'N/A')}")
        lines.append(
            f"\n    DEFENSE:    {analysis.get('relevance_to_defense', 'N/A')}")

    # Footer
    lines.append(f"\n\n{'=' * 70}")
    lines.append("           END OF REPORT — CyberPulse v1.0.0")
    lines.append(f"           {now}")
    lines.append("=" * 70)

    return "\n".join(lines)


def generate_report(articles):
    print(f"📝 Generating threat intelligence report...")

    stats = calculate_stats(articles)

    # Build final JSON report
    report = {
        "report_metadata": {
            "generated_at": datetime.now().isoformat(),  # local time
            "pipeline_version": "1.0.0",
            "total_articles": stats["total_articles"],
            "sources": list(set(a.get("source", "") for a in articles))
        },
        "statistics": stats,
        "articles": articles
    }

    output_dir = os.path.dirname(__file__)

    # Save JSON report with spaces between articles
    json_path = os.path.join(output_dir, "threat_report.json")
    with open(json_path, "w", encoding="utf-8") as f:
        wrapper = {
            "report_metadata": report["report_metadata"],
            "statistics": report["statistics"]
        }
        header = json.dumps(wrapper, indent=2, ensure_ascii=False)
        f.write(header[:-1])
        f.write(',\n  "articles": [')
        for i, article in enumerate(report["articles"]):
            f.write("\n")
            article_json = json.dumps(article, indent=2, ensure_ascii=False)
            indented = "\n".join(
                "    " + line for line in article_json.splitlines())
            f.write(indented)
            if i < len(report["articles"]) - 1:
                f.write(",\n\n\n")
        f.write("\n  ]\n}")

    print(f"💾 JSON report saved to capstone/threat_report.json")

    # Save text report
    text_report = format_text_report(articles, stats)
    txt_path = os.path.join(output_dir, "threat_report.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text_report)
    print(f"📄 Text report saved to capstone/threat_report.txt")

    # Print summary to terminal
    print("\n" + "=" * 70)
    print("  CYBERPULSE REPORT SUMMARY")
    print("=" * 70)
    print(f"  Total Articles:  {stats['total_articles']}")
    print(f"  Critical:        {stats['by_threat_level'].get('Critical', 0)}")
    print(f"  High:            {stats['by_threat_level'].get('High', 0)}")
    print(f"  Medium:          {stats['by_threat_level'].get('Medium', 0)}")
    print(f"  CVEs Found:      {len(stats['cves_identified'])}")
    print(
        f"  Top Threat:      {stats['top_priority_articles'][0]['title'][:60] if stats['top_priority_articles'] else 'None'}...")
    print("=" * 70)

    return report


def main():
    input_path = os.path.join(os.path.dirname(
        __file__), "analyzed_articles.json")

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            articles = json.load(f)
    except FileNotFoundError:
        print("❌ analyzed_articles.json not found — run analyzer.py first")
        return

    print(f"📂 Loaded {len(articles)} analyzed articles\n")
    generate_report(articles)


if __name__ == "__main__":
    main()
