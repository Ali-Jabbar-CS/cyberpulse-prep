# import asyncio
# import sys
# from crawl4ai import AsyncWebCrawler

# async def first_crawl():
#     print("Starting crawler...")
#     try:
#         async with AsyncWebCrawler(verbose=True) as crawler:
#             result = await crawler.arun(url="https://thehackernews.com")
#             print(f"Success: {result.success}")
#             print(f"Status code: {result.status_code}")
#             print(f"\n--- MARKDOWN PREVIEW (first 500 chars) ---")
#             print(result.markdown[:500])
#     except Exception as e:
#         print(f"Error: {e}")

# if sys.platform == "win32":
#     asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# asyncio.run(first_crawl())



# import asyncio
# import sys
# from crawl4ai import AsyncWebCrawler

# async def explore_result():
#     async with AsyncWebCrawler() as crawler:
#         result = await crawler.arun(url="https://thehackernews.com")

#         # How much content did we get?
#         print(f"Markdown length: {len(result.markdown)} characters")
#         print(f"HTML length: {len(result.html)} characters")

#         # All links found on the page
#         print(f"\nTotal links found: {len(result.links.get('internal', []))} internal")
#         print(f"Total links found: {len(result.links.get('external', []))} external")

#         # Preview first 5 internal links
#         print("\n--- FIRST 5 INTERNAL LINKS ---")
#         for link in result.links.get("internal", [])[:5]:
#             print(f"  {link['href']}")

#         # Preview first 5 external links
#         print("\n--- FIRST 5 EXTERNAL LINKS ---")
#         for link in result.links.get("external", [])[:5]:
#             print(f"  {link['href']}")

#         # Media found on the page
#         print(f"\nImages found: {len(result.media.get('images', []))}")
#         print("\n--- FIRST 3 IMAGES ---")
#         for img in result.media.get("images", [])[:3]:
#             print(f"  {img['src']}")

# if sys.platform == "win32":
#     asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# asyncio.run(explore_result())




import asyncio
import sys
import json
from crawl4ai import AsyncWebCrawler

async def extract_articles():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url="https://thehackernews.com")

        if result.extracted_content is None:
            print("CSS extraction returned nothing — selectors didn't match")
            print("\nHere's the markdown so we can find the real structure:")
            print(result.markdown[:2000])
        else:
            articles = json.loads(result.extracted_content)
            print(f"Extracted {len(articles)} articles")

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

asyncio.run(extract_articles())