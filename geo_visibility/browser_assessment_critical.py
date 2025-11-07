"""
Critical Browser Assessment - 5 Key Queries
Quick validation of SearchAPI vs Browser differences
"""
import asyncio
import os
from datetime import datetime
from browser_search_engine import BrowserSearchEngine, compare_api_vs_browser


# 5 most critical queries to test the hypothesis
CRITICAL_QUERIES = [
    "EPAM software company",
    "First Line Software AI services",
    "top AI consulting companies 2024",
    "who can build custom RAG systems",
    "generative AI consulting firms",
]


async def run_critical_assessment(searchapi_key: str):
    """Run critical assessment with 5 key queries."""

    print("\n" + "="*80)
    print("CRITICAL BROWSER ASSESSMENT")
    print("Testing hypothesis: Browser shows more AI Overview than API")
    print("="*80 + "\n")

    results = []
    api_ai_overview_count = 0
    browser_ai_overview_count = 0

    for i, query in enumerate(CRITICAL_QUERIES, 1):
        print(f"\n[{i}/{len(CRITICAL_QUERIES)}] Testing: {query}")
        print("-" * 80)

        try:
            # Use comparison function
            browser_result = await compare_api_vs_browser(query, searchapi_key)

            if browser_result:
                results.append({
                    "query": query,
                    "browser_has_ai_overview": browser_result.get("has_ai_overview", False),
                    "browser_result": browser_result,
                })

                # Count AI Overview appearances
                if browser_result.get("has_ai_overview"):
                    browser_ai_overview_count += 1

            await asyncio.sleep(3)  # Be nice to Google

        except Exception as e:
            print(f"Error: {e}")
            continue

    # Summary
    print("\n\n" + "="*80)
    print("📊 CRITICAL ASSESSMENT SUMMARY")
    print("="*80 + "\n")

    print(f"Queries tested: {len(CRITICAL_QUERIES)}")
    print(f"Successful: {len(results)}")
    print(f"\nBrowser AI Overview rate: {browser_ai_overview_count}/{len(results)} ({browser_ai_overview_count/len(results)*100:.1f}%)") if results else print("No results")

    # Show which queries triggered AI Overview
    if browser_ai_overview_count > 0:
        print(f"\n✅ AI Overview appeared in browser for:")
        for result in results:
            if result["browser_has_ai_overview"]:
                print(f"   • {result['query']}")

                # Show snippet of AI Overview text
                if result["browser_result"].get("ai_overview"):
                    text = result["browser_result"]["ai_overview"]["text"][:150]
                    print(f"     Preview: {text}...")

    # Analysis
    print(f"\n{'='*80}")
    print("📈 ANALYSIS")
    print(f"{'='*80}\n")

    if browser_ai_overview_count == 0:
        print("❌ No AI Overview detected in browser searches")
        print("\nPossible reasons:")
        print("  • These query types don't trigger AI Overview")
        print("  • Google hasn't rolled out AI Overview for these queries")
        print("  • User location/personalization affects availability")
        print("\n💡 Recommendation:")
        print("  • SearchAPI assessment was accurate")
        print("  • GEO visibility remains low")
        print("  • Focus on other channels")

    elif browser_ai_overview_count < len(results) * 0.2:
        print(f"⚠️  Low AI Overview rate ({browser_ai_overview_count}/{len(results)})")
        print("\n💡 Recommendation:")
        print("  • Selective GEO optimization possible")
        print("  • Focus on queries that triggered AI Overview")
        print("  • Monitor for increasing availability")

    else:
        print(f"✅ Significant AI Overview presence ({browser_ai_overview_count}/{len(results)})")
        print("\n💡 Key Finding:")
        print("  • Browser DOES show more AI Overview than expected")
        print("  • SearchAPI underestimated actual visibility")
        print("  • GEO strategy may be viable")
        print("\n📋 Next Steps:")
        print("  • Run full 20-query assessment")
        print("  • Analyze which query types perform best")
        print("  • Check for company mentions in AI Overview")
        print("  • Develop GEO content strategy")

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"critical_assessment_{timestamp}.json"

    try:
        import json
        with open(filename, 'w') as f:
            json.dump({
                "timestamp": timestamp,
                "queries": CRITICAL_QUERIES,
                "results": results,
                "browser_ai_overview_count": browser_ai_overview_count,
                "total_queries": len(results),
            }, f, indent=2)
        print(f"\n✓ Results saved to: {filename}")
    except Exception as e:
        print(f"\n⚠️  Could not save results: {e}")

    return results


async def main():
    """Main entry point."""
    searchapi_key = os.getenv("SEARCHAPI_API_KEY", "dUngVqvqnKPAr1p1BKqKENJW")

    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║         Critical Browser Assessment - 5 Key Queries          ║")
    print("║   Validates if browser sees different results than API       ║")
    print("╚══════════════════════════════════════════════════════════════╝")

    print(f"\nThis will:")
    print("  • Test 5 critical queries")
    print("  • Compare SearchAPI vs Real Browser")
    print("  • Check AI Overview appearance rate")
    print("  • Take screenshots for verification")
    print("  • Provide strategic recommendations")
    print(f"\nEstimated time: 2-3 minutes")

    input("\nPress Enter to start...")

    results = await run_critical_assessment(searchapi_key)

    print("\n✅ Critical assessment complete!")
    print("\nScreenshots saved to: screenshots/")
    print("Review them to verify AI Overview presence\n")


if __name__ == "__main__":
    asyncio.run(main())
