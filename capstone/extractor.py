import json
import os
import re
import anthropic
from dotenv import load_dotenv
import textwrap

load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def extract_cve_ids(text):
    """Extract CVE IDs from text using regex - No API needed."""
    pattern = r'CVE-\d{4}-\d{4,7}'
    matches = re.findall(pattern, text, re.IGNORECASE)
    # Deduplicate while preserving order
    seen = set()
    unique = []
    for cve in matches:
        if cve.upper() not in seen:
            seen.add(cve.upper())
            unique.append(cve.upper())
    return unique


def extract_severity_hint(text):
    """Scan text for severity keywords - returns highest found."""
    text_lower = text.lower()
    if any(word in text_lower for word in ["critical", "zero-day", "0-day", "actively exploited"]):
        return "Critical"
    elif any(word in text_lower for word in ["high severity", "remote code execution", "rce"]):
        return "High"
    elif any(word in text_lower for word in ["medium", "moderate"]):
        return "Medium"
    return "Unknown"


def enrich_article(article):
    """Use claude to extract security-specific fields from the article."""

    title = article.get("title", "")
    summary = article.get("summary", "")
    category = article.get("category", "")

    # First run cheap regex extraction
    cve_ids = extract_cve_ids(f"{title} {summary}")
    severity_hint = extract_severity_hint(f"{title} {summary}")

    prompt = f"""You are an expert cybersecurity analyst. Analyze this cybersecurity article and extract structured security intelligence.

Article Title: {title}
Article Summary: {summary}
Article Category: {category}
CVEs already detected: {cve_ids if cve_ids else "None Found"}
Severity hint from keywords: {severity_hint}

Return ONLY a JSON object with exactly these fields:
{{
"affected_software": ["list", "of", "software", "or", "systems"],
    "attack_type": "one of: RCE, SQLi, XSS, Phishing, Ransomware, Supply Chain, DDoS, Privilege Escalation, Other",
    "threat_actor": "threat actor or group name, or 'Unknown'",
    "patch_available": true or false,
    "defense_relevance": "one of: Critical, High, Medium, Low",
    "keywords": ["3", "to", "5", "key", "terms"]
}}

No explanations, no extra text. Just the JSON object."""

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )

        raw = response.content[0].text.strip()
        # Strip markdown fences if Claude adds them
        raw = raw.replace("```json", "").replace("```", "").strip()
        enriched_fields = json.loads(raw)

    except Exception as e:
        print(f"  ⚠️  Enrichment failed for '{title[:40]}': {e}")
        enriched_fields = {
            "affected_software": [],
            "attack_type": "Other",
            "threat_actor": "Unknown",
            "patch_available": False,
            "defense_relevance": severity_hint,
            "keywords": []
        }

    # Merge everything into one enriched article
    return {
        **article,
        "cve_ids": cve_ids,
        "severity_hint": severity_hint,
        **enriched_fields
    }


def enrich_all_articles(articles, limit=10):
    """Enrich a batch of articles. Limit controls API spend during testing."""

    print(
        f"🔬 Enriching {min(limit, len(articles))} of {len(articles)} articles...")

    enriched = []
    for i, article in enumerate(articles[:limit]):
        title_preview = article.get("title", "No title")[:50]
        print(f"  [{i+1}/{min(limit, len(articles))}] {title_preview}...")
        enriched_article = enrich_article(article)
        enriched.append(enriched_article)

    print(f"\n✅ Enrichment complete — {len(enriched)} articles processed")
    return enriched


def main():
    input_path = os.path.join(os.path.dirname(
        __file__), "crawled_articles.json")

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            articles = json.load(f)
    except FileNotFoundError:
        print("❌ crawled_articles.json not found — run crawler.py first")
        return []

    print(f"📂 Loaded {len(articles)} articles from crawler\n")

    enriched = enrich_all_articles(articles, limit=10)

    # Truncate summary to 150 chars so JSON stays readable
    for article in enriched:
        if "summary" in article and article["summary"]:
            article["summary"] = article["summary"][:175].rstrip() + "..."

    output_path = os.path.join(os.path.dirname(
        __file__), "enriched_articles.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(enriched, f, indent=2, ensure_ascii=False)

    print(f"💾 Saved to capstone/enriched_articles.json")
    return enriched


if __name__ == "__main__":
    main()
