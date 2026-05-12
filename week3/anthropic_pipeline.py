import anthropic
import json
import os
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# --- STEP 1: Load the articles we already scraped ---
def load_articles(filepath="all_articles.json"):
    try:
        with open(filepath, "r") as f:
            articles = json.load(f)
        print(f"Loaded {len(articles)} articles from {filepath}")
        return articles
    except FileNotFoundError:
        print(f"No file found at {filepath} — using sample data")
        return [
            {
                "title": "Critical RCE Vulnerability Found in Apache HTTP Server",
                "url": "https://example.com/apache-rce",
                "summary": "A critical remote code execution vulnerability was discovered in Apache HTTP Server versions 2.4.x, allowing unauthenticated attackers to execute arbitrary code.",
                "category": "Vulnerability"
            },
            {
                "title": "BlackCat Ransomware Group Targets Healthcare Sector",
                "url": "https://example.com/blackcat",
                "summary": "The BlackCat ransomware group has been observed targeting hospitals and healthcare providers across the United States, encrypting patient records.",
                "category": "Ransomware"
            }
        ]

# --- STEP 2: Analyze a single article with Claude ---
def analyze_article(article):
    prompt = f"""
You are a senior threat intelligence analyst at a defense contractor.
Analyze this cybersecurity article and return a JSON object with exactly these fields:

{{
    "threat_level": "Critical | High | Medium | Low",
    "affected_systems": ["list", "of", "affected", "systems"],
    "attack_vector": "how the attack works in one sentence",
    "affected_sectors": ["list", "of", "industries", "at risk"],
    "recommended_action": "one concrete action defenders should take",
    "relevance_to_defense": "why this matters for defense/government contractors specifically"
}}

Article title: {article['title']}
Article summary: {article['summary']}
Category: {article['category']}

Return only the JSON object, no other text.
"""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = message.content[0].text.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Sometimes Claude adds markdown fences despite instructions
        clean = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)

# --- STEP 3: Run the full pipeline ---
def run_pipeline(limit=5):
    articles = load_articles()

    # Only process up to limit articles to keep API costs low while testing
    articles_to_process = articles[:limit]
    print(f"Analyzing {len(articles_to_process)} articles...\n")

    enriched = []

    for i, article in enumerate(articles_to_process, 1):
        print(f"[{i}/{len(articles_to_process)}] {article['title'][:60]}...")
        try:
            analysis = analyze_article(article)
            enriched.append({
                "title": article["title"],
                "url": article["url"],
                "category": article["category"],
                "analysis": analysis
            })
            print(f"  Threat level: {analysis.get('threat_level')}")
            print(f"  Action: {analysis.get('recommended_action', '')[:80]}...")
            print()
        except Exception as e:
            print(f"  Failed: {e}\n")

    # Save enriched intelligence report
    with open("threat_report.json", "w") as f:
        json.dump(enriched, f, indent=2)

    print(f"--- PIPELINE COMPLETE ---")
    print(f"Processed: {len(enriched)} articles")
    print(f"Saved to: threat_report.json")

    # Summary by threat level
    levels = {}
    for item in enriched:
        level = item["analysis"].get("threat_level", "Unknown")
        levels[level] = levels.get(level, 0) + 1

    print("\nThreat level breakdown:")
    for level, count in sorted(levels.items()):
        print(f"  {level}: {count}")

if __name__ == "__main__":
    run_pipeline(limit=5)