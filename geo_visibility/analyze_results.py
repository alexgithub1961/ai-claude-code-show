"""
Results Analysis Tool
Analyzes JSON results from browser assessments and generates insights
"""
import json
import sys
from pathlib import Path
from collections import defaultdict
import glob


def load_results(filename):
    """Load results from JSON file."""
    with open(filename, 'r') as f:
        return json.load(f)


def compare_api_vs_browser_results(api_file, browser_file):
    """Compare API-based vs Browser-based assessment results."""

    print("\n" + "="*80)
    print("API vs BROWSER COMPARISON ANALYSIS")
    print("="*80 + "\n")

    api_data = load_results(api_file)
    browser_data = load_results(browser_file)

    # Extract metrics
    api_ai_rate = api_data.get("ai_overview_rate", 0) * 100
    browser_ai_rate = browser_data.get("ai_overview_rate", 0) * 100

    api_queries = api_data.get("total_queries", 0)
    browser_queries = browser_data.get("total_queries", 0)

    # Display comparison
    print(f"{'Metric':<30} {'API':<20} {'Browser':<20} {'Diff':<15}")
    print("="*85)

    print(f"{'Total Queries':<30} {api_queries:<20} {browser_queries:<20} "
          f"{browser_queries - api_queries:<15}")

    print(f"{'AI Overview Rate':<30} {api_ai_rate:<20.1f}% {browser_ai_rate:<20.1f}% "
          f"{browser_ai_rate - api_ai_rate:+.1f}%")

    # Company mentions
    api_companies = len(api_data.get("rankings", []))
    browser_companies = len(browser_data.get("rankings", []))

    print(f"{'Companies Mentioned':<30} {api_companies:<20} {browser_companies:<20} "
          f"{browser_companies - api_companies:+}")

    # Analysis
    print(f"\n{'='*80}")
    print("📊 ANALYSIS")
    print(f"{'='*80}\n")

    diff = browser_ai_rate - api_ai_rate

    if diff > 20:
        print("🔴 MAJOR DIFFERENCE - Browser shows significantly more AI Overview")
        print(f"\nKey Finding:")
        print(f"  • Browser AI Overview rate is {diff:.1f}% higher than API")
        print(f"  • SearchAPI is NOT representative of user experience")
        print(f"  • Real users see much more GEO content")
        print(f"\n💡 Recommendation:")
        print(f"  • GEO visibility is VIABLE")
        print(f"  • Invest in GEO optimization strategy")
        print(f"  • Previous API-based assessment underestimated opportunity")

    elif diff > 10:
        print("🟡 MODERATE DIFFERENCE - Browser shows more AI Overview")
        print(f"\nKey Finding:")
        print(f"  • Browser AI Overview rate is {diff:.1f}% higher")
        print(f"  • SearchAPI captures some but not all AI Overview")
        print(f"  • User experience includes more GEO content")
        print(f"\n💡 Recommendation:")
        print(f"  • Selective GEO optimization worthwhile")
        print(f"  • Focus on queries with high AI Overview rate")
        print(f"  • Monitor browser results for strategy")

    elif diff < -10:
        print("⚠️  UNEXPECTED - API showed more AI Overview than browser")
        print(f"\nThis is unusual and may indicate:")
        print(f"  • Different query sets tested")
        print(f"  • Timing differences (Google A/B testing)")
        print(f"  • Location/personalization effects")

    else:
        print("🟢 MINIMAL DIFFERENCE - API and browser results align")
        print(f"\nKey Finding:")
        print(f"  • Difference is only {abs(diff):.1f}%")
        print(f"  • SearchAPI provides representative results")
        print(f"  • Original API assessment was accurate")
        print(f"\n💡 Recommendation:")
        print(f"  • Stick with original assessment conclusions")
        print(f"  • GEO visibility remains low")
        print(f"  • Focus resources on other channels")

    # Company-specific analysis
    print(f"\n{'='*80}")
    print("🏢 COMPANY VISIBILITY COMPARISON")
    print(f"{'='*80}\n")

    api_rankings = {r["company"]: r for r in api_data.get("rankings", [])}
    browser_rankings = {r["company"]: r for r in browser_data.get("rankings", [])}

    all_companies = set(api_rankings.keys()) | set(browser_rankings.keys())

    print(f"{'Company':<25} {'API Mentions':<15} {'Browser Mentions':<18} {'Change':<10}")
    print("="*80)

    for company in sorted(all_companies):
        api_mentions = api_rankings.get(company, {}).get("total_mentions", 0)
        browser_mentions = browser_rankings.get(company, {}).get("total_mentions", 0)
        change = browser_mentions - api_mentions

        marker = " ⭐" if company == "First Line Software" else ""
        print(f"{company + marker:<25} {api_mentions:<15} {browser_mentions:<18} {change:+}")

    # First Line Software specific
    print(f"\n{'='*80}")
    print("⭐ FIRST LINE SOFTWARE ANALYSIS")
    print(f"{'='*80}\n")

    fls_api = api_rankings.get("First Line Software")
    fls_browser = browser_rankings.get("First Line Software")

    if fls_browser and not fls_api:
        print("✅ BREAKTHROUGH: First Line Software appears in BROWSER but not API!")
        print(f"   • Browser mentions: {fls_browser['total_mentions']}")
        print(f"   • AI Overview mentions: {fls_browser.get('ai_overview_mentions', 0)}")
        print(f"   • This confirms SearchAPI underestimated visibility")

    elif fls_browser and fls_api:
        print("📈 IMPROVED VISIBILITY: More mentions in browser vs API")
        print(f"   • API mentions: {fls_api.get('total_mentions', 0)}")
        print(f"   • Browser mentions: {fls_browser['total_mentions']}")
        print(f"   • Increase: {fls_browser['total_mentions'] - fls_api.get('total_mentions', 0)}")

    elif fls_api and not fls_browser:
        print("⚠️  INCONSISTENT: Appeared in API but not browser")
        print("    (This is unusual - may indicate query differences)")

    else:
        print("❌ NO VISIBILITY: Not mentioned in either API or browser results")
        print("    • GEO visibility remains zero across methodologies")


def analyze_single_assessment(filename):
    """Analyze a single assessment file."""

    print("\n" + "="*80)
    print("SINGLE ASSESSMENT ANALYSIS")
    print("="*80 + "\n")

    data = load_results(filename)

    # Basic stats
    print(f"Assessment Type: {filename}")
    print(f"Timestamp: {data.get('timestamp', 'unknown')}")
    print(f"Total Queries: {data.get('total_queries', 0)}")
    print(f"AI Overview Count: {data.get('ai_overview_count', 0)}")
    print(f"AI Overview Rate: {data.get('ai_overview_rate', 0)*100:.1f}%")

    # Company rankings
    rankings = data.get("rankings", [])
    print(f"\nCompanies with visibility: {len(rankings)}")

    if rankings:
        print(f"\n{'RANK':<6} {'COMPANY':<25} {'AI OVERVIEW':<12} {'ORGANIC':<10} {'SCORE':<8}")
        print("="*70)

        for i, rank in enumerate(rankings, 1):
            print(f"{i:<6} {rank['company']:<25} {rank['ai_overview_mentions']:<12} "
                  f"{rank['organic_mentions']:<10} {rank['visibility_score']:<8}")

    # Category performance (if available)
    if "category_performance" in data:
        print(f"\n{'='*80}")
        print("CATEGORY PERFORMANCE")
        print(f"{'='*80}\n")

        print(f"{'Category':<30} {'AI Overview':<20} {'Rate':<10}")
        print("-"*60)

        for category, stats in data["category_performance"].items():
            rate = stats["ai_overview"] / stats["total"] * 100 if stats["total"] > 0 else 0
            print(f"{category:<30} {stats['ai_overview']}/{stats['total']:<17} {rate:.0f}%")


def find_latest_results():
    """Find the most recent assessment results."""
    files = glob.glob("*_assessment_*.json")

    if not files:
        return None, None

    files.sort(key=lambda x: Path(x).stat().st_mtime, reverse=True)

    api_files = [f for f in files if "api" in f.lower()]
    browser_files = [f for f in files if "full" in f or "critical" in f]

    return api_files[0] if api_files else None, browser_files[0] if browser_files else None


def main():
    """Main analysis entry point."""

    if len(sys.argv) > 2:
        # Compare two files
        api_file = sys.argv[1]
        browser_file = sys.argv[2]
        compare_api_vs_browser_results(api_file, browser_file)

    elif len(sys.argv) > 1:
        # Analyze single file
        filename = sys.argv[1]
        analyze_single_assessment(filename)

    else:
        # Auto-detect latest results
        print("No files specified, searching for latest results...")
        api_file, browser_file = find_latest_results()

        if browser_file:
            print(f"Found browser results: {browser_file}")
            analyze_single_assessment(browser_file)

            if api_file:
                print(f"\nAlso found API results: {api_file}")
                response = input("\nCompare with API results? (y/n): ")
                if response.lower() == 'y':
                    compare_api_vs_browser_results(api_file, browser_file)
        else:
            print("\n❌ No assessment results found")
            print("\nRun an assessment first:")
            print("  • python browser_assessment_critical.py  (5 queries, quick)")
            print("  • python browser_assessment_full.py      (20 queries, comprehensive)")


if __name__ == "__main__":
    main()
