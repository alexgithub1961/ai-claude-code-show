"""
Debug HTML Fetch
Save actual HTML from Google to understand parsing issues.
"""
import asyncio
import httpx
from datetime import datetime

# Enable DoH
try:
    from doh_resolver import enable_doh
    enable_doh()
    print("✓ DNS-over-HTTPS enabled")
except Exception as e:
    print(f"⚠️  Could not enable DoH: {e}")


async def fetch_and_save_html(query: str):
    """Fetch Google search HTML and save to file."""

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

    url = "https://www.google.com/search"
    params = {'q': query, 'hl': 'en', 'gl': 'us'}

    print(f"\n🔍 Fetching: {query}")

    try:
        async with httpx.AsyncClient(headers=headers, timeout=15.0, follow_redirects=True) as client:
            response = await client.get(url, params=params)

            print(f"   Status: {response.status_code}")
            print(f"   Content-Length: {len(response.text)} bytes")

            # Save HTML
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"google_search_{timestamp}.html"

            with open(filename, 'w', encoding='utf-8') as f:
                f.write(response.text)

            print(f"   ✓ Saved to: {filename}")

            # Quick analysis
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            h3_count = len(soup.find_all('h3'))
            a_count = len(soup.find_all('a'))
            div_count = len(soup.find_all('div'))

            print(f"\n   HTML Structure:")
            print(f"      <h3> tags: {h3_count}")
            print(f"      <a> tags: {a_count}")
            print(f"      <div> tags: {div_count}")

            # Check for specific patterns
            if 'Our systems have detected unusual traffic' in response.text:
                print(f"   ⚠️  Google detected bot traffic!")
            elif response.status_code == 429:
                print(f"   ⚠️  Rate limited!")
            elif h3_count < 5:
                print(f"   ⚠️  Very few <h3> tags - may be blocked or limited")
            else:
                print(f"   ✓ HTML looks normal")

            return filename

    except Exception as e:
        print(f"   ✗ Error: {e}")
        return None


async def main():
    """Test queries."""
    test_queries = [
        "EPAM software company",
        "generative AI consulting firms",
    ]

    print("\n" + "="*80)
    print("DEBUG: Fetch and Save Google Search HTML")
    print("="*80)

    for query in test_queries:
        await fetch_and_save_html(query)
        await asyncio.sleep(3)

    print("\n✅ HTML files saved. Check them to see what Google returns.\n")


if __name__ == "__main__":
    asyncio.run(main())
