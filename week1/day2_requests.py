# Day 2 - HTTP requests, sessions, query params, retry logic
import requests
import json
import time

# --- BASIC FETCH with exception handling ---
def safe_fetch(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.text[:200]
    except requests.exceptions.Timeout:
        print(f"Timed out: {url}")
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error: {e}")
    except Exception as e:
        print(f"Something else broke: {e}")
    return None

# --- CUSTOM USER-AGENT + saving headers to disk ---
def fetch_and_save(url, output_file, label="page"):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        result = {
            "label": label,
            "url": url,
            "status_code": response.status_code,
            "response_headers": dict(response.headers),
        }
        with open(output_file, "w") as f:
            json.dump(result, f, indent=2)
        print(f"Saved {label} → {output_file}")
        return True
    except Exception as e:
        print(f"Failed on {label}: {e}")
        return False

# --- QUERY PARAMETERS ---
def demo_query_params():
    params = {"topic": "ransomware", "severity": "critical", "limit": 10}
    response = requests.get("https://httpbin.org/get", params=params)
    data = response.json()
    print("URL built:", response.url)
    print("Args received:", data["args"])

# --- SESSIONS: reuse headers across multiple requests ---
def demo_sessions():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
    }
    session = requests.Session()
    session.headers.update(headers)
    urls = [
        "https://httpbin.org/get",
        "https://httpbin.org/headers",
        "https://httpbin.org/user-agent",
    ]
    for url in urls:
        response = session.get(url)
        print(f"Status {response.status_code} → {url.split('/')[-1]}")
    session.close()

# --- REAL CVE SEARCH: NVD government database ---
def search_cves(keyword, results_per_page=5):
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 CyberPulse-Research/1.0"})
    params = {"keywordSearch": keyword, "resultsPerPage": results_per_page}
    try:
        response = session.get(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            params=params,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        cves = []
        for item in data.get("vulnerabilities", []):
            cve = item["cve"]
            cves.append({
                "id": cve["id"],
                "published": cve["published"][:10],
                "description": cve["descriptions"][0]["value"][:120] + "..."
            })
        return cves
    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        session.close()

# --- SMART FETCH: automatic retry on rate limiting ---
def smart_fetch(url, params=None, retries=3):
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 CyberPulse-Research/1.0"})
    for attempt in range(retries):
        try:
            response = session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                print(f"Success on attempt {attempt + 1}")
                return response.json()
            elif response.status_code == 429:
                wait = int(response.headers.get("Retry-After", 5))
                print(f"Rate limited. Waiting {wait}s before retry...")
                time.sleep(wait)
            elif response.status_code == 403:
                print("Blocked — server rejected us")
                return None
            elif response.status_code == 404:
                print(f"Page doesn't exist: {url}")
                return None
        except requests.exceptions.Timeout:
            print(f"Attempt {attempt + 1} timed out, retrying...")
            time.sleep(2)
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            return None
    print("All retries exhausted")
    return None


# --- RUN EVERYTHING ---
if __name__ == "__main__":
    safe_fetch("https://httpbin.org/get")
    fetch_and_save("https://httpbin.org/get", "result.json", label="test_request")
    demo_query_params()
    demo_sessions()

    results = search_cves("ransomware", results_per_page=3)
    for cve in results:
        print(f"\n{cve['id']} ({cve['published']})")
        print(f"  {cve['description']}")

    smart_fetch(
        "https://services.nvd.nist.gov/rest/json/cves/2.0",
        params={"keywordSearch": "supply chain attack", "resultsPerPage": 2}
    )