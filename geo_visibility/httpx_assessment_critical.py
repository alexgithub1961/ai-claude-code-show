"""
Critical HTTPX Assessment - 5 Key Queries
Tests user's hypothesis: Does direct HTML fetch show different AI Overview than SearchAPI?
Uses httpx instead of Playwright (works in restricted environments)
"""
import asyncio
import os
from datetime import datetime
from httpx_search_engine import HttpxSearchEngine, compare_api_vs_httpx


# 5 most critical queries to test the hypothesis
CRITICAL_QUERIES = [
    "EPAM software company",
    "First Line Software AI services",
    "top AI consulting companies 2024",
    "who can build custom RAG systems",
    "generative AI consulting firms",
]


async def run_critical_assessment(searchapi_key: str):
    """Run critical assessment with 5 key queries using HTTPX."""

    print("\n" + "="*80)
    print("CRITICAL HTTPX ASSESSMENT")
    print("Testing hypothesis: HTML fetch shows different AI Overview than API")
    print("="*80 + "\n")

    results = []
    api_ai_overview_count = 0
    httpx_ai_overview_count = 0
    differences_found = 0

    for i, query in enumerate(CRITICAL_QUERIES, 1):
        print(f"\n[{i}/{len(CRITICAL_QUERIES)}] Testing: {query}")
        print("-" * 80)

        try:
            # Compare API vs HTTPX
            comparison = await compare_api_vs_httpx(query, searchapi_key)

            results.append(comparison)

            # Count AI Overview appearances
            if comparison.get("api_has_ai_overview"):
                api_ai_overview_count += 1

            if comparison.get("httpx_has_ai_overview"):
                httpx_ai_overview_count += 1

            if comparison.get("difference"):
                differences_found += 1
                print(f"\n⚠️  DIFFERENCE DETECTED!")
                print(f"   API shows AI Overview: {comparison['api_has_ai_overview']}")
                print(f"   HTTPX shows AI Overview: {comparison['httpx_has_ai_overview']}")

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

    if results:
        api_rate = api_ai_overview_count / len(results) * 100
        httpx_rate = httpx_ai_overview_count / len(results) * 100
        diff = httpx_rate - api_rate

        print(f"\nAI Overview Rates:")
        print(f"  SearchAPI: {api_ai_overview_count}/{len(results)} ({api_rate:.1f}%)")
        print(f"  HTTPX:     {httpx_ai_overview_count}/{len(results)} ({httpx_rate:.1f}%)")
        print(f"  Difference: {diff:+.1f}%")

        print(f"\nDifferences found: {differences_found}/{len(results)}")

    # Show which queries had AI Overview in HTTPX
    if httpx_ai_overview_count > 0:
        print(f"\n✅ AI Overview appeared in HTTPX for:")
        for result in results:
            if result.get("httpx_has_ai_overview"):
                print(f"   • {result['query']}")

                # Show snippet of AI Overview text
                httpx_result = result.get("httpx_result", {})
                if httpx_result.get("ai_overview"):
                    text = httpx_result["ai_overview"].get("text", "")[:150]
                    print(f"     Preview: {text}...")

    # Analysis
    print(f"\n{'='*80}")
    print("📈 ANALYSIS")
    print(f"{'='*80}\n")

    if differences_found == 0:
        print("✅ NO DIFFERENCES: HTTPX and API show same AI Overview behavior")
        print("\nKey Finding:")
        print("  • SearchAPI accurately represents what browsers see")
        print("  • Original API assessment was correct")
        print("  • User's hypothesis not confirmed")
        print("\n💡 Recommendation:")
        if httpx_rate < 20:
            print("  • GEO visibility remains low")
            print("  • Focus on other channels")
        else:
            print("  • Consider GEO optimization")

    elif diff > 20:
        print(f"🔴 MAJOR DIFFERENCE - HTTPX shows {diff:.1f}% more AI Overview")
        print(f"\nKey Finding:")
        print(f"  • HTTPX direct fetch shows significantly more AI Overview")
        print(f"  • SearchAPI underestimates actual visibility")
        print(f"  • Real users see much more GEO content")
        print(f"  • User's hypothesis CONFIRMED")
        print(f"\n💡 Recommendation:")
        print(f"  • GEO visibility is VIABLE")
        print(f"  • Invest in GEO optimization strategy")
        print(f"  • Previous API-based assessment was misleading")

    elif diff > 5:
        print(f"🟡 MODERATE DIFFERENCE - HTTPX shows {diff:.1f}% more AI Overview")
        print(f"\nKey Finding:")
        print(f"  • Some discrepancy between API and direct fetch")
        print(f"  • SearchAPI partially underestimates visibility")
        print(f"  • User's hypothesis partially confirmed")
        print(f"\n💡 Recommendation:")
        print(f"  • Selective GEO optimization worthwhile")
        print(f"  • Focus on queries with high HTTPX AI Overview rate")

    elif diff < -5:
        print(f"🟣 REVERSE DIFFERENCE - API shows {-diff:.1f}% more AI Overview")
        print(f"\nThis suggests:")
        print(f"  • SearchAPI may use different rendering")
        print(f"  • HTML parsing may be missing AI Overview")
        print(f"  • Need to improve HTTPX extraction logic")

    else:
        print(f"🟢 MINIMAL DIFFERENCE ({abs(diff):.1f}%)")
        print(f"\nKey Finding:")
        print(f"  • API and HTTPX results align closely")
        print(f"  • SearchAPI provides representative results")

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"httpx_assessment_{timestamp}.json"

    try:
        import json
        with open(filename, 'w') as f:
            json.dump({
                "timestamp": timestamp,
                "queries": CRITICAL_QUERIES,
                "results": results,
                "api_ai_overview_count": api_ai_overview_count,
                "httpx_ai_overview_count": httpx_ai_overview_count,
                "total_queries": len(results),
                "differences_found": differences_found,
                "api_rate": api_rate if results else 0,
                "httpx_rate": httpx_rate if results else 0,
                "difference_percentage": diff if results else 0,
            }, f, indent=2)
        print(f"\n✓ Results saved to: {filename}")
    except Exception as e:
        print(f"\n⚠️  Could not save results: {e}")

    return results


async def main():
    """Main entry point."""
    searchapi_key = os.getenv("SEARCHAPI_API_KEY", "dUngVqvqnKPAr1p1BKqKENJW")

    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║         Critical HTTPX Assessment - 5 Key Queries           ║")
    print("║   Validates if HTML fetch shows different results than API  ║")
    print("╚══════════════════════════════════════════════════════════════╝")

    print(f"\nThis will:")
    print("  • Test 5 critical queries")
    print("  • Compare SearchAPI vs HTTPX (direct HTML fetch)")
    print("  • Check AI Overview appearance rates")
    print("  • Identify discrepancies")
    print("  • Provide strategic recommendations")
    print(f"\nEstimated time: 1-2 minutes")
    print("\nStarting assessment...")

    results = await run_critical_assessment(searchapi_key)

    print("\n✅ Critical assessment complete!")
    print(f"\nResults saved to: httpx_assessment_<timestamp>.json\n")


if __name__ == "__main__":
    asyncio.run(main())
