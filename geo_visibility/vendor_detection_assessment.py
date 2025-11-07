"""
Vendor Detection Assessment
Tests if vendor names appear in organic search results.
Compares SearchAPI vs HTTPX for vendor mentions.
"""
import asyncio
import os
import httpx
import json
import re
from datetime import datetime
from typing import Dict, List, Set
from httpx_search_engine import HttpxSearchEngine

# Companies to track
COMPANIES = {
    "First Line Software": ["First Line Software", "First Line", "FLS", "firstlinesoftware"],
    "EPAM": ["EPAM", "EPAM Systems"],
    "DataArt": ["DataArt", "Data Art"],
    "Endava": ["Endava"],
    "Projectus": ["Projectus"],
    "Luxsoft": ["Luxsoft", "Luxoft"],
}

# 5 critical queries
CRITICAL_QUERIES = [
    "EPAM software company",
    "First Line Software AI services",
    "top AI consulting companies 2024",
    "who can build custom RAG systems",
    "generative AI consulting firms",
]


def detect_companies_in_text(text: str) -> Set[str]:
    """
    Detect which companies are mentioned in text.

    Args:
        text: Text to search (title, snippet, URL, etc.)

    Returns:
        Set of company names found
    """
    found = set()
    text_lower = text.lower()

    for company, variations in COMPANIES.items():
        for variation in variations:
            if variation.lower() in text_lower:
                found.add(company)
                break  # Found this company, move to next

    return found


def analyze_organic_results(results: List[Dict], method_name: str) -> Dict:
    """
    Analyze organic results for company mentions.

    Args:
        results: List of organic results with title, url, snippet
        method_name: "SearchAPI" or "HTTPX" for logging

    Returns:
        Dict with company mentions and details
    """
    companies_found = {company: [] for company in COMPANIES.keys()}
    total_mentions = 0

    for position, result in enumerate(results, start=1):
        title = result.get("title", "")
        url = result.get("url", "")
        snippet = result.get("snippet", "")

        # Combine all text for searching
        combined_text = f"{title} {url} {snippet}"

        # Detect companies
        found = detect_companies_in_text(combined_text)

        for company in found:
            companies_found[company].append({
                "position": position,
                "title": title,
                "url": url,
                "snippet": snippet[:200],
            })
            total_mentions += 1
            print(f"      [{position}] {company} - {title[:60]}...")

    return {
        "companies_found": companies_found,
        "total_mentions": total_mentions,
        "unique_companies": len([c for c, results in companies_found.items() if results]),
    }


async def compare_vendor_detection(query: str, searchapi_key: str) -> Dict:
    """
    Compare vendor detection between SearchAPI and HTTPX.

    Args:
        query: Search query
        searchapi_key: SearchAPI API key

    Returns:
        Dict with comparison results
    """
    print("\n" + "="*80)
    print(f"VENDOR DETECTION COMPARISON")
    print(f"Query: {query}")
    print("="*80)

    # 1. SearchAPI results
    print("\n1️⃣  SearchAPI Organic Results")
    print("-" * 80)

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
            api_organic = api_data.get("organic_results", [])

            print(f"   Status: {response.status_code}")
            print(f"   Organic results: {len(api_organic)}")

            if api_organic:
                print(f"   Vendors found:")
                api_analysis = analyze_organic_results(api_organic, "SearchAPI")
            else:
                print(f"   No organic results")
                api_analysis = {"companies_found": {company: [] for company in COMPANIES}, "total_mentions": 0, "unique_companies": 0}

    except Exception as e:
        print(f"   ✗ Exception: {e}")
        api_organic = []
        api_analysis = {"companies_found": {company: [] for company in COMPANIES}, "total_mentions": 0, "unique_companies": 0}

    # 2. HTTPX results
    print("\n2️⃣  HTTPX Organic Results (Browser-like)")
    print("-" * 80)

    engine = HttpxSearchEngine()
    httpx_result = await engine.search_google(query)
    httpx_organic = httpx_result.get("organic_results", [])

    print(f"   Status: {'OK' if not httpx_result.get('error') else 'Error'}")
    print(f"   Organic results: {len(httpx_organic)}")

    if httpx_organic:
        print(f"   Vendors found:")
        httpx_analysis = analyze_organic_results(httpx_organic, "HTTPX")
    else:
        print(f"   No organic results (HTML parsing issue)")
        httpx_analysis = {"companies_found": {company: [] for company in COMPANIES}, "total_mentions": 0, "unique_companies": 0}

    # 3. Comparison
    print("\n3️⃣  COMPARISON")
    print("="*80)

    # Count mentions per company
    print("\nVendor Mentions by Method:")
    print(f"{'Company':<25} {'SearchAPI':<15} {'HTTPX':<15} {'Difference'}")
    print("-" * 70)

    differences_found = False
    for company in COMPANIES.keys():
        api_count = len(api_analysis["companies_found"].get(company, []))
        httpx_count = len(httpx_analysis["companies_found"].get(company, []))
        diff = httpx_count - api_count

        diff_str = f"{diff:+d}" if diff != 0 else "="
        if diff != 0:
            differences_found = True
            diff_str = f"⚠️  {diff_str}"

        print(f"{company:<25} {api_count:<15} {httpx_count:<15} {diff_str}")

    print("\n" + "-" * 70)
    print(f"{'TOTAL':<25} {api_analysis['total_mentions']:<15} {httpx_analysis['total_mentions']:<15}")
    print(f"{'Unique Companies':<25} {api_analysis['unique_companies']:<15} {httpx_analysis['unique_companies']:<15}")

    # Show differences
    if differences_found:
        print("\n⚠️  DIFFERENCES DETECTED!")
        print("   Different vendor visibility between SearchAPI and HTTPX")
    else:
        print("\n✅ NO DIFFERENCES - Both methods found same vendors")

    await asyncio.sleep(2)  # Rate limiting

    return {
        "query": query,
        "api_analysis": api_analysis,
        "httpx_analysis": httpx_analysis,
        "differences_found": differences_found,
        "api_organic_count": len(api_organic),
        "httpx_organic_count": len(httpx_organic),
    }


async def run_vendor_assessment(searchapi_key: str):
    """Run vendor detection assessment."""

    print("\n" + "="*80)
    print("VENDOR DETECTION ASSESSMENT")
    print("Testing: Do vendor names appear in organic results?")
    print("="*80 + "\n")

    results = []

    # Track overall stats
    api_total_vendors = 0
    httpx_total_vendors = 0
    queries_with_differences = 0

    for i, query in enumerate(CRITICAL_QUERIES, 1):
        print(f"\n{'='*80}")
        print(f"[{i}/{len(CRITICAL_QUERIES)}] Testing: {query}")
        print(f"{'='*80}")

        try:
            comparison = await compare_vendor_detection(query, searchapi_key)
            results.append(comparison)

            # Update stats
            api_total_vendors += comparison["api_analysis"]["total_mentions"]
            httpx_total_vendors += comparison["httpx_analysis"]["total_mentions"]

            if comparison["differences_found"]:
                queries_with_differences += 1

        except Exception as e:
            print(f"\n✗ Error processing query: {e}")
            continue

    # Summary
    print("\n\n" + "="*80)
    print("📊 VENDOR DETECTION SUMMARY")
    print("="*80 + "\n")

    print(f"Queries tested: {len(CRITICAL_QUERIES)}")
    print(f"Successful: {len(results)}")

    print(f"\nTotal Vendor Mentions:")
    print(f"  SearchAPI:  {api_total_vendors}")
    print(f"  HTTPX:      {httpx_total_vendors}")
    print(f"  Difference: {httpx_total_vendors - api_total_vendors:+d}")

    print(f"\nQueries with differences: {queries_with_differences}/{len(results)}")

    # Per-company summary
    print(f"\n{'='*80}")
    print("📈 VENDOR VISIBILITY BY COMPANY")
    print(f"{'='*80}\n")

    # Aggregate company mentions across all queries
    company_totals_api = {company: 0 for company in COMPANIES}
    company_totals_httpx = {company: 0 for company in COMPANIES}

    for result in results:
        for company in COMPANIES:
            company_totals_api[company] += len(result["api_analysis"]["companies_found"].get(company, []))
            company_totals_httpx[company] += len(result["httpx_analysis"]["companies_found"].get(company, []))

    print(f"{'Company':<25} {'SearchAPI':<15} {'HTTPX':<15} {'Difference'}")
    print("-" * 70)

    for company in sorted(COMPANIES.keys()):
        api_count = company_totals_api[company]
        httpx_count = company_totals_httpx[company]
        diff = httpx_count - api_count

        emoji = "🟢" if httpx_count > 0 else "⚫"
        diff_str = f"{diff:+d}" if diff != 0 else "="

        print(f"{emoji} {company:<23} {api_count:<15} {httpx_count:<15} {diff_str}")

    # Analysis
    print(f"\n{'='*80}")
    print("📈 ANALYSIS")
    print(f"{'='*80}\n")

    if api_total_vendors == 0 and httpx_total_vendors == 0:
        print("❌ NO VENDORS FOUND in organic results (both methods)")
        print("\nKey Finding:")
        print("  • Neither SearchAPI nor HTTPX found vendor names")
        print("  • These query types don't show target vendors in results")
        print("  • Low organic visibility across the board")

    elif httpx_total_vendors > api_total_vendors * 1.5:
        print(f"🔴 HTTPX SHOWS MORE VENDORS (+{httpx_total_vendors - api_total_vendors} mentions)")
        print("\nKey Finding:")
        print("  • HTTPX (browser-like) finds more vendor mentions")
        print("  • SearchAPI may miss some organic results")
        print("  • User's hypothesis CONFIRMED for organic results")
        print("\n💡 Recommendation:")
        print("  • SearchAPI underestimates vendor visibility")
        print("  • Real users see more vendor mentions than API suggests")

    elif api_total_vendors > httpx_total_vendors * 1.5:
        print(f"🟣 SearchAPI SHOWS MORE VENDORS (+{api_total_vendors - httpx_total_vendors} mentions)")
        print("\nKey Finding:")
        print("  • SearchAPI finds more vendors than HTTPX")
        print("  • HTTPX HTML parsing may need improvement")
        print("  • SearchAPI appears more reliable for organic results")

    else:
        print(f"🟢 SIMILAR VENDOR COUNTS (±{abs(httpx_total_vendors - api_total_vendors)} mentions)")
        print("\nKey Finding:")
        print("  • Both methods show similar vendor visibility")
        print("  • Results are consistent across methods")

    # Check if HTTPX parsing is working
    httpx_avg_results = sum(r["httpx_organic_count"] for r in results) / len(results) if results else 0
    if httpx_avg_results < 2:
        print(f"\n⚠️  WARNING: HTTPX found very few organic results (avg: {httpx_avg_results:.1f})")
        print("   • HTML parsing may not be working correctly")
        print("   • Google's HTML structure may have changed")
        print("   • Results may be incomplete")

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"vendor_detection_{timestamp}.json"

    try:
        with open(filename, 'w') as f:
            json.dump({
                "timestamp": timestamp,
                "queries": CRITICAL_QUERIES,
                "results": results,
                "summary": {
                    "api_total_vendors": api_total_vendors,
                    "httpx_total_vendors": httpx_total_vendors,
                    "difference": httpx_total_vendors - api_total_vendors,
                    "queries_with_differences": queries_with_differences,
                    "company_totals_api": company_totals_api,
                    "company_totals_httpx": company_totals_httpx,
                },
            }, f, indent=2, default=str)
        print(f"\n✓ Results saved to: {filename}")
    except Exception as e:
        print(f"\n⚠️  Could not save results: {e}")

    return results


async def main():
    """Main entry point."""
    searchapi_key = os.getenv("SEARCHAPI_API_KEY", "dUngVqvqnKPAr1p1BKqKENJW")

    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║          Vendor Detection Assessment                         ║")
    print("║   Do vendor names appear in organic search results?         ║")
    print("╚══════════════════════════════════════════════════════════════╝")

    print(f"\nTracking {len(COMPANIES)} companies:")
    for company, variations in COMPANIES.items():
        print(f"  • {company}: {', '.join(variations)}")

    print(f"\nTesting {len(CRITICAL_QUERIES)} queries:")
    for i, query in enumerate(CRITICAL_QUERIES, 1):
        print(f"  {i}. {query}")

    print(f"\nEstimated time: 1-2 minutes")
    print("\nStarting assessment...\n")

    results = await run_vendor_assessment(searchapi_key)

    print("\n✅ Vendor detection assessment complete!\n")


if __name__ == "__main__":
    asyncio.run(main())
