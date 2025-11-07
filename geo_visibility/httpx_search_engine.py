"""
HTTPX-based Google Search (No Browser Required)
Fetches Google search results using httpx with browser-like headers.
Works in restricted environments where Playwright can't run.
"""
import asyncio
import httpx
import re
from typing import Dict, List, Optional
from datetime import datetime
from bs4 import BeautifulSoup
import json
import time

# Enable DNS-over-HTTPS
try:
    from doh_resolver import enable_doh
    enable_doh()
    print("✓ DNS-over-HTTPS enabled")
except Exception as e:
    print(f"⚠️  Could not enable DoH: {e}")


class HttpxSearchEngine:
    """
    Google search using httpx with browser-like headers.
    Parses HTML to extract AI Overview and organic results.
    """

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    async def search_google(self, query: str) -> Dict:
        """
        Search Google and extract AI Overview + organic results.

        Args:
            query: Search query

        Returns:
            Dict with:
                - query: str
                - has_ai_overview: bool
                - ai_overview: Dict or None
                - organic_results: List[Dict]
                - timestamp: str
        """
        print(f"\n🔍 Searching: {query}")

        try:
            # Build Google search URL
            url = "https://www.google.com/search"
            params = {
                'q': query,
                'hl': 'en',
                'gl': 'us',
            }

            # Add delay to avoid rate limiting
            await asyncio.sleep(2)

            # Fetch results
            async with httpx.AsyncClient(headers=self.headers, timeout=15.0, follow_redirects=True) as client:
                response = await client.get(url, params=params)

                print(f"   Status: {response.status_code}")

                if response.status_code == 429:
                    print("   ⚠️  Rate limited by Google")
                    return {
                        "query": query,
                        "error": "Rate limited",
                        "has_ai_overview": False,
                        "organic_results": [],
                        "timestamp": datetime.now().isoformat(),
                    }

                if response.status_code != 200:
                    print(f"   ✗ Failed with status {response.status_code}")
                    return {
                        "query": query,
                        "error": f"HTTP {response.status_code}",
                        "has_ai_overview": False,
                        "organic_results": [],
                        "timestamp": datetime.now().isoformat(),
                    }

                # Parse HTML
                html = response.text
                soup = BeautifulSoup(html, 'html.parser')

                # Extract AI Overview
                ai_overview = self._extract_ai_overview(soup)

                # Extract organic results
                organic_results = self._extract_organic_results(soup)

                print(f"   AI Overview: {ai_overview is not None}")
                print(f"   Organic Results: {len(organic_results)}")

                return {
                    "query": query,
                    "has_ai_overview": ai_overview is not None,
                    "ai_overview": ai_overview,
                    "organic_results": organic_results,
                    "timestamp": datetime.now().isoformat(),
                }

        except Exception as e:
            print(f"   ✗ Exception: {e}")
            return {
                "query": query,
                "error": str(e),
                "has_ai_overview": False,
                "organic_results": [],
                "timestamp": datetime.now().isoformat(),
            }

    def _extract_ai_overview(self, soup: BeautifulSoup) -> Optional[Dict]:
        """
        Extract AI Overview from Google search results.

        Google uses various div attributes for AI Overview:
        - data-attrid containing 'SGE' or 'AIOverview'
        - specific CSS classes
        - text containing 'AI-generated' or 'AI Overview'
        """

        # Strategy 1: Look for data-attrid with SGE or AI keywords
        ai_divs = soup.find_all('div', attrs={'data-attrid': re.compile(r'(SGE|AI|Overview)', re.I)})

        if ai_divs:
            for div in ai_divs:
                text = div.get_text(strip=True)
                if len(text) > 50:  # Substantial content
                    return {
                        "text": text[:2000],  # First 2000 chars
                        "method": "data-attrid",
                    }

        # Strategy 2: Look for divs with AI-related text
        for pattern in [r'AI-generated', r'AI Overview', r'Generative AI']:
            ai_text_elements = soup.find_all(text=re.compile(pattern, re.I))
            for element in ai_text_elements:
                parent = element.find_parent(['div', 'section'])
                if parent:
                    text = parent.get_text(strip=True)
                    if len(text) > 100:
                        return {
                            "text": text[:2000],
                            "method": "text-pattern",
                        }

        # Strategy 3: Look for specific CSS classes (Google changes these frequently)
        for class_pattern in ['AIOverview', 'sge', 'ai-overview', 'generative']:
            elements = soup.find_all('div', class_=re.compile(class_pattern, re.I))
            for element in elements:
                text = element.get_text(strip=True)
                if len(text) > 100:
                    return {
                        "text": text[:2000],
                        "method": f"class-{class_pattern}",
                    }

        # Strategy 4: Check for "An AI Overview is not available" message
        not_available = soup.find(text=re.compile(r'An AI Overview is not available', re.I))
        if not_available:
            return {
                "text": "An AI Overview is not available for this search",
                "method": "not-available-message",
                "available": False,
            }

        return None

    def _extract_organic_results(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Extract organic search results from Google SERP.

        Google organic results typically have:
        - <div class="g"> containers (or similar)
        - <h3> for titles
        - <a> for URLs
        - Various div classes for snippets
        """
        results = []

        # Strategy 1: Find all <h3> tags (Google uses these for result titles)
        h3_tags = soup.find_all('h3')

        for h3 in h3_tags[:15]:  # Top 15 to ensure we get at least 10
            try:
                # Title from h3
                title = h3.get_text(strip=True)

                # Find parent link
                link = h3.find_parent('a')
                if not link:
                    # Try finding sibling or nearby link
                    parent = h3.find_parent(['div', 'article'])
                    if parent:
                        link = parent.find('a')

                if not link:
                    continue

                url = link.get('href', '')

                # Clean Google redirect URLs
                if url.startswith('/url?q='):
                    match = re.search(r'/url\?q=([^&]+)', url)
                    if match:
                        url = match.group(1)

                # Skip internal Google links
                if not url or url.startswith('#') or 'google.com' in url:
                    continue

                # Find snippet (search near the link/title)
                snippet = ""
                parent = h3.find_parent(['div', 'article'])
                if parent:
                    # Look for common snippet classes/tags
                    snippet_elem = (
                        parent.find('div', class_=re.compile(r'(VwiC3b|lyLwlc|s3v9rd|IsZvec)')) or
                        parent.find('span', class_=re.compile(r'(st|aCOpRe)')) or
                        parent.find('div', attrs={'data-sncf': '1'}) or
                        parent.find('div', attrs={'data-snf': 'nke7rc'})
                    )
                    if snippet_elem:
                        snippet = snippet_elem.get_text(strip=True)

                if title and url:
                    results.append({
                        "title": title,
                        "url": url,
                        "snippet": snippet,
                        "position": len(results) + 1,
                    })

            except Exception as e:
                continue

        # Strategy 2: Standard div class="g" approach (backup)
        if len(results) < 3:
            result_divs = soup.find_all('div', class_='g')

            for div in result_divs[:10]:
                try:
                    title_elem = div.find('h3')
                    title = title_elem.get_text(strip=True) if title_elem else ""

                    link_elem = div.find('a')
                    url = link_elem.get('href', '') if link_elem else ""

                    snippet_elem = div.find('div', class_=re.compile(r'(VwiC3b|lyLwlc|s3v9rd)'))
                    if not snippet_elem:
                        snippet_elem = div.find('span', class_=re.compile(r'(st|aCOpRe)'))
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""

                    if title and url and url not in [r['url'] for r in results]:
                        results.append({
                            "title": title,
                            "url": url,
                            "snippet": snippet,
                            "position": len(results) + 1,
                        })
                except Exception:
                    continue

        # Strategy 3: Look for any <a> with <h3> children (most reliable)
        if len(results) < 3:
            links_with_h3 = soup.find_all('a', href=True)

            for link in links_with_h3[:20]:
                try:
                    h3 = link.find('h3')
                    if not h3:
                        continue

                    title = h3.get_text(strip=True)
                    url = link.get('href', '')

                    # Clean URL
                    if url.startswith('/url?q='):
                        match = re.search(r'/url\?q=([^&]+)', url)
                        if match:
                            url = match.group(1)

                    # Skip Google internal links
                    if not url or url.startswith('#') or 'google.com' in url or url.startswith('/search'):
                        continue

                    # Avoid duplicates
                    if url in [r['url'] for r in results]:
                        continue

                    results.append({
                        "title": title,
                        "url": url,
                        "snippet": "",
                        "position": len(results) + 1,
                    })

                except Exception:
                    continue

        return results[:10]  # Return top 10


async def compare_api_vs_httpx(query: str, searchapi_key: str) -> Dict:
    """
    Compare SearchAPI vs HTTPX-based search for a query.

    Args:
        query: Search query
        searchapi_key: SearchAPI API key

    Returns:
        Dict with comparison results
    """
    print("=" * 80)
    print(f"COMPARING: API vs HTTPX")
    print(f"Query: {query}")
    print("=" * 80)

    # 1. SearchAPI results
    print("\n1️⃣  Fetching SearchAPI results...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.searchapi.io/api/v1/search",
                params={
                    "q": query,
                    "api_key": searchapi_key,
                    "engine": "google",
                },
                timeout=30.0,
            )

            api_data = response.json()
            api_ai_overview = api_data.get("ai_overview")
            api_organic = api_data.get("organic_results", [])

            print(f"   ✓ Status: {response.status_code}")
            print(f"   AI Overview: {bool(api_ai_overview)}")
            if api_ai_overview and isinstance(api_ai_overview, dict):
                if api_ai_overview.get("error"):
                    print(f"   AI Overview Error: {api_ai_overview.get('error')}")
            print(f"   Organic Results: {len(api_organic)}")
    except Exception as e:
        print(f"   ✗ Exception: {e}")
        api_ai_overview = None
        api_organic = []

    # 2. HTTPX-based search
    print("\n2️⃣  Fetching HTTPX search results...")
    engine = HttpxSearchEngine()
    httpx_result = await engine.search_google(query)

    # 3. Comparison
    print("\n3️⃣  COMPARISON")
    print("=" * 80)

    api_has_ai = bool(api_ai_overview and not (isinstance(api_ai_overview, dict) and api_ai_overview.get("error")))
    httpx_has_ai = httpx_result.get("has_ai_overview", False)

    print(f"AI Overview:")
    print(f"  SearchAPI: {'✓ Yes' if api_has_ai else '✗ No'}")
    print(f"  HTTPX:     {'✓ Yes' if httpx_has_ai else '✗ No'}")

    if httpx_has_ai and httpx_result.get("ai_overview"):
        print(f"\nAI Overview Preview:")
        text = httpx_result["ai_overview"].get("text", "")[:200]
        print(f"  {text}...")

    print(f"\nOrganic Results:")
    print(f"  SearchAPI: {len(api_organic)} results")
    print(f"  HTTPX:     {len(httpx_result.get('organic_results', []))} results")

    return {
        "query": query,
        "api_has_ai_overview": api_has_ai,
        "httpx_has_ai_overview": httpx_has_ai,
        "difference": httpx_has_ai != api_has_ai,
        "httpx_result": httpx_result,
    }


async def test_httpx_search():
    """Test the HTTPX search engine."""
    engine = HttpxSearchEngine()

    test_queries = [
        "EPAM software company",
        "First Line Software AI services",
        "top AI consulting companies 2024",
    ]

    print("\n" + "=" * 80)
    print("HTTPX SEARCH ENGINE TEST")
    print("=" * 80)

    for query in test_queries:
        result = await engine.search_google(query)

        print(f"\n{'='*80}")
        print(f"Query: {query}")
        print(f"AI Overview: {result.get('has_ai_overview')}")
        if result.get('ai_overview'):
            print(f"AI Text: {result['ai_overview'].get('text', '')[:150]}...")
        print(f"Organic Results: {len(result.get('organic_results', []))}")

        await asyncio.sleep(3)  # Rate limiting


if __name__ == "__main__":
    asyncio.run(test_httpx_search())
