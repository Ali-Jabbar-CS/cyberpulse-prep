import json
import os
import anthropic
from dotenv import load_dotenv

load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def analyze_article(article):
    """Run threat analysis on a single enriched article."""

    title = article.get("title", "")
    summary = article.get("summary", "")
    category = article.get("category", "other")
    cve_ids = article.get("cve_ids", [])
    affected_software = article.get("affected_software", [])
    attack_type = article.get("attack_type", [])
    severity_hint = article.get("severity_hint", "Unknown")
    defense_relevance = article.get("defense_relevance", "Unknown")

    prompt = f"""You are a senior threat intelligence analyst at a defense contractor supporting US Navy and DOD cybersecurity operations.

    Analyze this cybersecurity article and produce a structured threat assessment.

    ARTICLE_DATA:
    Title: {title}
    Summary: {summary}
    Category: {category}
    CVE IDs: {cve_ids if cve_ids else "None identified"}
    Affected Software/Systems: {affected_software if affected_software else "Unknown"}
    Attack Type: {attack_type}
    Initial Severity: {severity_hint}
    Defense Relevance: {defense_relevance}


Produce a JSON threat assessment with exactly these fields:
{{
    "threat_level": "one of: Critical, High, Medium, Low",
    "threat_summary": "2 sentence max — what is the threat and why it matters",
    "affected_systems": ["specific", "systems", "or", "software"],
    "attack_vector": "how the attack is carried out in one sentence",
    "affected_sectors": ["list", "of", "sectors", "e.g. Defense, Finance, Healthcare"],
    "recommended_action": "one concrete action a defense contractor IT team should take",
    "relevance_to_defense": "one sentence on why this matters specifically to defense contractors or DOD",
    "priority_score": a number from 1-10 where 10 is most urgent
}}

No explanations. JSON only."""

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}]
        )

        raw = response.content[0].text.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        analysis = json.loads(raw)

    except Exception as e:
        print(f"  ⚠️  Analysis failed for '{title[:40]}': {e}")
        analysis = {
            "threat_level": severity_hint,
            "threat_summary": summary[:150] if summary else "No summary available",
            "affected_systems": affected_software,
            "attack_vector": attack_type,
            "affected_sectors": ["Unknown"],
            "recommended_action": "Monitor vendor advisories and apply patches when available",
            "relevance_to_defense": "Requires manual review",
            "priority_score": 5
        }

    return {**article, "analysis": analysis}


def analyze_all_articles(articles):
    print(f"🧠 Analyzing {len(articles)} enriched articles...")

    analyzed = []
    for i, article in enumerate(articles):
        title_preview = article.get("title", "No title")[:50]
        print(f"  [{i+1}/{len(articles)}] {title_preview}...")
        analyzed_article = analyze_article(article)
        analyzed.append(analyzed_article)

    # Sort by priority score descending so highest threats are first
    analyzed.sort(
        key=lambda x: x.get("analysis", {}).get("priority_score", 0),
        reverse=True
    )

    print(f"\n✅ Analysis complete — {len(analyzed)} articles analyzed")
    return analyzed


def main():
    input_path = os.path.join(os.path.dirname(
        __file__), "enriched_articles.json")

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            articles = json.load(f)
    except FileNotFoundError:
        print("❌ enriched_articles.json not found — run extractor.py first")
        return []

    print(f"📂 Loaded {len(articles)} enriched articles\n")

    analyzed = analyze_all_articles(articles)

    # Only truncate raw summary — analysis fields stay full length
    for article in analyzed:
        if "summary" in article and article["summary"]:
            article["summary"] = article["summary"][:150].rstrip() + "..."

    output_path = os.path.join(os.path.dirname(
        __file__), "analyzed_articles.json")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("[\n\n")
        for i, article in enumerate(analyzed):
            f.write(json.dumps(article, indent=2, ensure_ascii=False))
            if i < len(analyzed) - 1:
                f.write(",\n\n\n")
        f.write("\n\n\n]")

    print(f"💾 Saved to capstone/analyzed_articles.json")
    return analyzed


if __name__ == "__main__":
    main()
