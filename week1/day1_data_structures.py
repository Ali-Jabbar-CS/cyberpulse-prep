# Day 1 - Core data structures for security data pipelines
import json

# --- SETS: deduplication ---
urls = [
    "https://bleepingcomputer.com/article-1",
    "https://bleepingcomputer.com/article-2",
    "https://bleepingcomputer.com/article-1",
    "https://thehackernews.com/post-1",
    "https://bleepingcomputer.com/article-2",
]
unique_urls = set(urls)
print(f"Found {len(urls)} URLs, {len(unique_urls)} unique")

# --- JSON I/O: saving and loading scraped data ---
articles = [
    {"title": "New ransomware targets healthcare", "severity": "Critical"},
    {"title": "Patch Tuesday: 42 vulnerabilities fixed", "severity": "High"},
]
with open("articles.json", "w") as f:
    json.dump(articles, f, indent=2)

with open("articles.json", "r") as f:
    loaded = json.load(f)
print(loaded[0]["title"])

# --- LIST COMPREHENSIONS: filtering and transforming scraped data ---
articles_full = [
    {"title": "New ransomware hits hospitals", "severity": "Critical"},
    {"title": "Minor CSS update on gov site", "severity": "Low"},
    {"title": "Zero-day found in Windows kernel", "severity": "Critical"},
    {"title": "Company updates privacy policy", "severity": "Low"},
    {"title": "APT group targets defense contractors", "severity": "Critical"},
]

critical = [a for a in articles_full if a["severity"] == "Critical"]
titles = [a["title"] for a in articles_full]
critical_titles = [a["title"].upper() for a in articles_full if a["severity"] == "Critical"]

print(f"All titles: {len(titles)}")
print(f"Critical articles: {len(critical)}")
print(f"Critical titles uppercased: {critical_titles}")