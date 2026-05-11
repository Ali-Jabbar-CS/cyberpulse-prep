from bs4 import BeautifulSoup

# This is what requests.get() gives you back — raw HTML
raw_html = """
<html>
  <body>
    <div class="article">
      <h2 class="title">Ransomware group targets US Navy contractors</h2>
      <span class="severity">Critical</span>
      <p class="summary">A known APT group has been observed targeting defense supply chains...</p>
      <a href="/articles/navy-ransomware-2024">Read more</a>
    </div>
    <div class="article">
      <h2 class="title">CISA issues advisory on ICS vulnerabilities</h2>
      <span class="severity">High</span>
      <p class="summary">Industrial control systems used in energy infrastructure are affected...</p>
      <a href="/articles/cisa-ics-2024">Read more</a>
    </div>
  </body>
</html>
"""

soup = BeautifulSoup(raw_html, "html.parser")

# Find one element
first_title = soup.find("h2", class_="title")
print("First title:", first_title.text)

# Find all elements of a type
all_articles = soup.find_all("div", class_="article")
print(f"Found {len(all_articles)} articles")

# Loop through and extract fields
for article in all_articles:
    title = article.find("h2", class_="title").text
    severity = article.find("span", class_="severity").text
    link = article.find("a")["href"]
    print(f"\n{severity} — {title}")
    print(f"  Link: {link}")







import requests
from bs4 import BeautifulSoup

def scrape_headlines(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # h3 tags contain article headlines on Hacker News
    headlines = soup.find_all("h3")

    print(f"Found {len(headlines)} h3 tags\n")
    for i, tag in enumerate(headlines[:5], 1):
        print(f"{i}. {tag.text.strip()}")

scrape_headlines("https://thehackernews.com")










from bs4 import BeautifulSoup

html_v1 = """
<div class="article-card">
  <h2 class="article-title">Zero-day found in Apache server</h2>
</div>
"""

html_v2 = """
<div class="post-wrapper">
    <h2 class="post-heading">Zero-day found in Apache server</h2>
</div>
"""

def extract_title(html):
    soup = BeautifulSoup(html, "html.parser")
    result = soup.find("div", class_="article-card")
    if result:
        return result.find("h2", class_="article-title").text
    return None

print("v1 result:", extract_title(html_v1))
print("v2 result:", extract_title(html_v2))
