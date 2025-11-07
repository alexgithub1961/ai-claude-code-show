"""
Browser-based search engine using Playwright
Emulates real browser to get actual search results users see.

This may show different results than SearchAPI because:
- JavaScript-rendered content
- User-agent differences
- Google's API vs browser serving logic
- AI Overview may appear more frequently
"""
import asyncio
from datetime import datetime
from typing import Optional, List, Dict
import time
from playwright.async_api import async_playwright, Browser, Page

# Import DNS-over-HTTPS resolver to bypass UDP DNS blocking
try:
    from doh_resolver import enable_doh
    # Enable DoH at module load to fix DNS in restricted environments
    enable_doh()
    print("✓ DNS-over-HTTPS enabled (bypasses UDP port 53 blocking)")
except Exception as e:
    print(f"⚠️  Could not enable DoH: {e}")


class BrowserSearchEngine:
    """
    Real browser-based search using Playwright.
    Gets the same results actual users see.
    """

    def __init__(self, headless: bool = True, slow_mo: int = 100):
        """
        Initialize browser search engine.

        Args:
            headless: Run browser in headless mode
            slow_mo: Slow down operations (ms) for stability
        """
        self.headless = headless
        self.slow_mo = slow_mo
        self.browser: Optional[Browser] = None
        self.playwright = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def start(self):
        """Start browser instance."""
        self.playwright = await async_playwright().start()

        # Launch Chromium (most common browser)
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            slow_mo=self.slow_mo,
        )

    async def close(self):
        """Close browser instance."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def search_google(self, query: str) -> Dict:
        """
        Perform Google search in real browser.

        Args:
            query: Search query

        Returns:
            Dict with search results, AI Overview, organic results, etc.
        """
        if not self.browser:
            await self.start()

        # Create new page
        page = await self.browser.new_page()

        try:
            # Navigate to Google
            await page.goto("https://www.google.com", wait_until="networkidle")

            # Handle cookie consent if present
            try:
                consent_button = page.locator("button:has-text('Accept all'), button:has-text('I agree')")
                if await consent_button.count() > 0:
                    await consent_button.first.click()
                    await page.wait_for_timeout(500)
            except:
                pass  # No consent dialog

            # Find search box and enter query
            search_box = page.locator("textarea[name='q'], input[name='q']")
            await search_box.fill(query)
            await search_box.press("Enter")

            # Wait for results to load
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(2000)  # Extra wait for dynamic content

            # Take screenshot for debugging
            screenshot_path = f"screenshots/search_{query.replace(' ', '_')[:50]}.png"
            try:
                await page.screenshot(path=screenshot_path, full_page=True)
            except:
                pass  # Screenshot directory may not exist

            # Extract AI Overview if present
            ai_overview = await self._extract_ai_overview(page)

            # Extract organic results
            organic_results = await self._extract_organic_results(page)

            # Extract knowledge panel
            knowledge_panel = await self._extract_knowledge_panel(page)

            # Extract featured snippet
            featured_snippet = await self._extract_featured_snippet(page)

            return {
                "query": query,
                "url": page.url,
                "has_ai_overview": bool(ai_overview),
                "ai_overview": ai_overview,
                "organic_results": organic_results,
                "knowledge_panel": knowledge_panel,
                "featured_snippet": featured_snippet,
                "timestamp": datetime.now().isoformat(),
            }

        finally:
            await page.close()

    async def _extract_ai_overview(self, page: Page) -> Optional[Dict]:
        """Extract Google AI Overview content."""

        # Try multiple selectors for AI Overview
        selectors = [
            "[data-attrid*='SGE']",  # Search Generative Experience
            "[data-attrid*='AIOverview']",
            ".AIOverview",
            "[jsname*='SGE']",
            "div[data-content-feature='1']",
            # Look for text patterns
            "text=/AI-generated/i",
            "text=/AI Overview/i",
        ]

        for selector in selectors:
            try:
                element = page.locator(selector).first
                if await element.count() > 0:
                    text = await element.text_content()
                    html = await element.inner_html()

                    # Extract sources if present
                    sources = await self._extract_ai_sources(element)

                    return {
                        "text": text.strip() if text else "",
                        "html": html[:1000],  # Limit HTML size
                        "sources": sources,
                        "selector_matched": selector,
                    }
            except:
                continue

        return None

    async def _extract_ai_sources(self, element) -> List[Dict]:
        """Extract source citations from AI Overview."""
        sources = []

        # Look for numbered citations or links within AI Overview
        try:
            links = await element.locator("a[href]").all()
            for i, link in enumerate(links[:5], 1):  # Max 5 sources
                href = await link.get_attribute("href")
                text = await link.text_content()
                sources.append({
                    "number": i,
                    "text": text.strip() if text else "",
                    "url": href,
                })
        except:
            pass

        return sources

    async def _extract_organic_results(self, page: Page) -> List[Dict]:
        """Extract organic search results."""
        results = []

        # Main search results container
        try:
            # Try different result selectors
            result_selectors = [
                "div.g",  # Standard Google result
                "[data-sokoban-container]",
                ".tF2Cxc",
            ]

            for selector in result_selectors:
                result_elements = page.locator(selector)
                count = await result_elements.count()

                if count > 0:
                    for i in range(min(count, 20)):  # Max 20 results
                        try:
                            result = result_elements.nth(i)

                            # Extract title
                            title_elem = result.locator("h3").first
                            title = await title_elem.text_content() if await title_elem.count() > 0 else ""

                            # Extract link
                            link_elem = result.locator("a[href]").first
                            link = await link_elem.get_attribute("href") if await link_elem.count() > 0 else ""

                            # Extract snippet
                            snippet_selectors = [".VwiC3b", "[data-sncf='1']", ".IsZvec"]
                            snippet = ""
                            for snip_sel in snippet_selectors:
                                snip_elem = result.locator(snip_sel).first
                                if await snip_elem.count() > 0:
                                    snippet = await snip_elem.text_content()
                                    break

                            if title and link:
                                results.append({
                                    "position": len(results) + 1,
                                    "title": title.strip(),
                                    "link": link,
                                    "snippet": snippet.strip() if snippet else "",
                                })
                        except:
                            continue

                    if results:
                        break  # Found results with this selector

        except Exception as e:
            print(f"Error extracting organic results: {e}")

        return results

    async def _extract_knowledge_panel(self, page: Page) -> Optional[Dict]:
        """Extract knowledge panel (right side info box)."""
        try:
            # Knowledge panel selectors
            kp = page.locator("[data-attrid='kc:/common:'] , .kp-blk").first

            if await kp.count() > 0:
                title = ""
                description = ""

                # Extract title
                title_elem = kp.locator("h2, h3").first
                if await title_elem.count() > 0:
                    title = await title_elem.text_content()

                # Extract description
                desc_elem = kp.locator("[data-attrid*='description']").first
                if await desc_elem.count() > 0:
                    description = await desc_elem.text_content()

                return {
                    "title": title.strip() if title else "",
                    "description": description.strip() if description else "",
                }
        except:
            pass

        return None

    async def _extract_featured_snippet(self, page: Page) -> Optional[Dict]:
        """Extract featured snippet (position 0)."""
        try:
            snippet = page.locator("[data-attrid='FeaturedSnippet']").first

            if await snippet.count() > 0:
                text = await snippet.text_content()

                # Extract source link
                link_elem = snippet.locator("a[href]").first
                link = ""
                if await link_elem.count() > 0:
                    link = await link_elem.get_attribute("href")

                return {
                    "text": text.strip() if text else "",
                    "source_url": link,
                }
        except:
            pass

        return None


async def compare_api_vs_browser(query: str, searchapi_key: str):
    """
    Compare SearchAPI results vs real browser results.

    Args:
        query: Search query
        searchapi_key: SearchAPI key for comparison
    """
    import httpx

    print(f"\n{'='*80}")
    print(f"COMPARING: API vs BROWSER")
    print(f"Query: {query}")
    print(f"{'='*80}\n")

    # 1. Get SearchAPI results
    print("1️⃣  Fetching SearchAPI results...")
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

            if response.status_code == 200:
                api_data = response.json()
                api_has_overview = "ai_overview" in api_data and isinstance(api_data.get("ai_overview"), dict)
                api_organic_count = len(api_data.get("organic_results", []))

                print(f"   ✓ Status: {response.status_code}")
                print(f"   AI Overview: {api_has_overview}")
                if api_has_overview:
                    overview = api_data["ai_overview"]
                    if "error" in overview:
                        print(f"   AI Overview Error: {overview['error']}")
                    else:
                        print(f"   AI Overview Text: {overview.get('text', '')[:100]}...")
                print(f"   Organic Results: {api_organic_count}")
            else:
                print(f"   ✗ Error: {response.status_code}")
                api_has_overview = False
                api_organic_count = 0
    except Exception as e:
        print(f"   ✗ Exception: {e}")
        api_has_overview = False
        api_organic_count = 0

    print()

    # 2. Get real browser results
    print("2️⃣  Fetching Real Browser results...")
    try:
        async with BrowserSearchEngine(headless=True) as browser:
            browser_data = await browser.search_google(query)

            print(f"   ✓ Search completed")
            print(f"   URL: {browser_data['url']}")
            print(f"   AI Overview: {browser_data['has_ai_overview']}")
            if browser_data['ai_overview']:
                print(f"   AI Overview Text: {browser_data['ai_overview']['text'][:100]}...")
                print(f"   AI Overview Sources: {len(browser_data['ai_overview'].get('sources', []))}")
            print(f"   Organic Results: {len(browser_data['organic_results'])}")
            print(f"   Knowledge Panel: {bool(browser_data['knowledge_panel'])}")
            print(f"   Featured Snippet: {bool(browser_data['featured_snippet'])}")
    except Exception as e:
        print(f"   ✗ Exception: {e}")
        browser_data = None

    print()

    # 3. Compare
    print("3️⃣  COMPARISON")
    print(f"{'='*80}")

    if browser_data:
        print(f"\n{'Metric':<30} {'SearchAPI':<25} {'Real Browser':<25}")
        print(f"{'-'*80}")
        print(f"{'AI Overview Present':<30} {str(api_has_overview):<25} {str(browser_data['has_ai_overview']):<25}")
        print(f"{'Organic Results Count':<30} {str(api_organic_count):<25} {str(len(browser_data['organic_results'])):<25}")

        # Show difference
        if api_has_overview != browser_data['has_ai_overview']:
            print(f"\n⚠️  DIFFERENT: AI Overview availability differs!")
            if browser_data['has_ai_overview'] and not api_has_overview:
                print(f"   → Browser shows AI Overview, but API doesn't")
                print(f"   → This means SearchAPI is not returning what users see!")
        else:
            print(f"\n✓ SAME: AI Overview availability matches")

        # Show organic results comparison
        if abs(api_organic_count - len(browser_data['organic_results'])) > 2:
            print(f"\n⚠️  DIFFERENT: Organic result counts differ significantly")

        return browser_data
    else:
        print("Browser search failed, cannot compare")
        return None


async def main():
    """Test browser-based search."""
    import os

    searchapi_key = os.getenv("SEARCHAPI_API_KEY", "dUngVqvqnKPAr1p1BKqKENJW")

    # Test queries - mix of types
    test_queries = [
        "EPAM software company",
        "generative AI consulting services",
        "LLM implementation companies",
        "First Line Software Ukraine",
        "companies that build custom AI solutions",
    ]

    print("\n" + "="*80)
    print("BROWSER-BASED SEARCH ENGINE TEST")
    print("Testing if real browser sees different results than SearchAPI")
    print("="*80)

    for query in test_queries:
        await compare_api_vs_browser(query, searchapi_key)
        print("\n")
        await asyncio.sleep(3)  # Be nice to Google


if __name__ == "__main__":
    asyncio.run(main())
