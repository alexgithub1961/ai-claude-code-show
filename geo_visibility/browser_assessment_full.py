"""
Full Browser Assessment - 20 Comprehensive Queries
Complete validation with detailed company visibility analysis
"""
import asyncio
import os
import json
from datetime import datetime
from collections import defaultdict
from browser_search_engine import BrowserSearchEngine


# Comprehensive test queries across categories
FULL_ASSESSMENT_QUERIES = {
    "Direct Company": [
        "EPAM software company",
        "First Line Software Ukraine",
        "DataArt consulting services",
        "Endava technology company",
    ],

    "AI Services": [
        "generative AI consulting firms",
        "LLM implementation companies",
        "enterprise AI chatbot development",
        "RAG solution providers",
    ],

    "Vendor Selection": [
        "top AI consulting companies 2024",
        "best LLM integration services",
        "leading generative AI consultants",
        "who can build custom AI solutions",
    ],

    "Technology Specific": [
        "companies that implement RAG systems",
        "GPT-4 enterprise integration services",
        "ChatGPT business implementation",
        "semantic search development firms",
    ],

    "Comparison": [
        "EPAM competitors",
        "companies like Endava",
        "DataArt alternatives",
        "software development firms Ukraine",
    ],
}


# Companies to track
COMPANIES = {
    "First Line Software": ["First Line Software", "First Line", "FLS"],
    "EPAM": ["EPAM", "EPAM Systems"],
    "DataArt": ["DataArt", "Data Art"],
    "Endava": ["Endava"],
    "Luxsoft": ["Luxsoft", "Luxoft"],
    "Projectus": ["Projectus", "Protectus"],
}


class CompanyVisibilityAnalyzer:
    """Analyze company visibility in browser results."""

    def __init__(self):
        self.company_mentions = defaultdict(lambda: {
            "ai_overview_mentions": 0,
            "organic_mentions": 0,
            "queries": [],
            "contexts": [],
        })
        self.query_results = []

    def analyze_result(self, query: str, category: str, browser_result: dict):
        """Analyze a single query result for company mentions."""
        result_data = {
            "query": query,
            "category": category,
            "has_ai_overview": browser_result.get("has_ai_overview", False),
            "companies_found": [],
        }

        # Check AI Overview for company mentions
        if browser_result.get("has_ai_overview") and browser_result.get("ai_overview"):
            ai_text = browser_result["ai_overview"].get("text", "").lower()

            for company, variations in COMPANIES.items():
                for variation in variations:
                    if variation.lower() in ai_text:
                        self.company_mentions[company]["ai_overview_mentions"] += 1
                        self.company_mentions[company]["queries"].append(query)
                        self.company_mentions[company]["contexts"].append({
                            "query": query,
                            "location": "AI Overview",
                            "text": ai_text[:200],
                        })
                        result_data["companies_found"].append(company)
                        break

        # Check organic results for company mentions
        for organic in browser_result.get("organic_results", []):
            title = organic.get("title", "").lower()
            snippet = organic.get("snippet", "").lower()
            link = organic.get("link", "").lower()

            for company, variations in COMPANIES.items():
                for variation in variations:
                    if (variation.lower() in title or
                        variation.lower() in snippet or
                        variation.lower() in link):

                        self.company_mentions[company]["organic_mentions"] += 1
                        if company not in result_data["companies_found"]:
                            result_data["companies_found"].append(company)
                        break

        self.query_results.append(result_data)

    def get_rankings(self):
        """Get company visibility rankings."""
        rankings = []

        for company, data in self.company_mentions.items():
            total_mentions = data["ai_overview_mentions"] + data["organic_mentions"]
            if total_mentions > 0:
                # Weight AI Overview mentions more heavily
                visibility_score = (
                    data["ai_overview_mentions"] * 10 +
                    data["organic_mentions"] * 1
                )

                rankings.append({
                    "company": company,
                    "ai_overview_mentions": data["ai_overview_mentions"],
                    "organic_mentions": data["organic_mentions"],
                    "total_mentions": total_mentions,
                    "visibility_score": visibility_score,
                    "queries": list(set(data["queries"])),
                })

        rankings.sort(key=lambda x: x["visibility_score"], reverse=True)
        return rankings


async def run_full_assessment():
    """Run comprehensive browser-based assessment."""

    print("\n" + "="*80)
    print("FULL BROWSER ASSESSMENT - 20 QUERIES")
    print("Comprehensive validation with company visibility tracking")
    print("="*80 + "\n")

    total_queries = sum(len(queries) for queries in FULL_ASSESSMENT_QUERIES.values())
    print(f"Total queries: {total_queries}")
    print(f"Estimated time: {total_queries * 0.5:.0f}-{total_queries * 1:.0f} minutes\n")

    analyzer = CompanyVisibilityAnalyzer()
    ai_overview_count = 0
    processed = 0

    async with BrowserSearchEngine(headless=True) as browser:
        for category, queries in FULL_ASSESSMENT_QUERIES.items():
            print(f"\n{'='*80}")
            print(f"Category: {category}")
            print(f"{'='*80}\n")

            for query in queries:
                processed += 1
                print(f"[{processed}/{total_queries}] {query}")

                try:
                    result = await browser.search_google(query)

                    # Show basic result
                    if result["has_ai_overview"]:
                        ai_overview_count += 1
                        print(f"   ✓ AI Overview present")
                    else:
                        print(f"   ℹ No AI Overview")

                    print(f"   Organic results: {len(result['organic_results'])}")

                    # Analyze for company mentions
                    analyzer.analyze_result(query, category, result)

                    # Show companies found
                    result_companies = analyzer.query_results[-1]["companies_found"]
                    if result_companies:
                        print(f"   → Companies: {', '.join(result_companies)}")

                    await asyncio.sleep(3)  # Rate limiting

                except Exception as e:
                    print(f"   ✗ Error: {e}")
                    continue

    # Generate rankings
    print("\n\n" + "="*80)
    print("📊 COMPANY VISIBILITY RANKINGS")
    print("="*80 + "\n")

    rankings = analyzer.get_rankings()

    print(f"AI Overview Rate: {ai_overview_count}/{processed} ({ai_overview_count/processed*100:.1f}%)")
    print(f"Companies with visibility: {len(rankings)}\n")

    if rankings:
        print(f"{'RANK':<6} {'COMPANY':<25} {'AI OVERVIEW':<12} {'ORGANIC':<10} {'SCORE':<8}")
        print("="*80)

        for i, rank in enumerate(rankings, 1):
            is_fls = rank["company"] == "First Line Software"
            marker = " ⭐" if is_fls else ""
            company_display = rank["company"] + marker

            print(f"{i:<6} {company_display:<25} {rank['ai_overview_mentions']:<12} "
                  f"{rank['organic_mentions']:<10} {rank['visibility_score']:<8}")

        # Detailed analysis
        print(f"\n\n{'='*80}")
        print("📋 DETAILED VISIBILITY ANALYSIS")
        print(f"{'='*80}\n")

        for i, rank in enumerate(rankings, 1):
            print(f"\n{i}. {rank['company']}")
            print("-" * 70)
            print(f"   AI Overview Mentions: {rank['ai_overview_mentions']}")
            print(f"   Organic Mentions: {rank['organic_mentions']}")
            print(f"   Visibility Score: {rank['visibility_score']}")

            print(f"\n   Appeared in {len(rank['queries'])} queries:")
            for query in rank['queries'][:5]:  # Show first 5
                print(f"     • {query}")

    else:
        print("⚠️  No companies were mentioned in any results")

    # Strategic analysis
    print(f"\n\n{'='*80}")
    print("📈 STRATEGIC ANALYSIS")
    print(f"{'='*80}\n")

    # First Line Software specific
    fls_data = next((r for r in rankings if r["company"] == "First Line Software"), None)

    if fls_data:
        fls_rank = next(i for i, r in enumerate(rankings, 1) if r["company"] == "First Line Software")
        print(f"First Line Software:")
        print(f"  ✓ Rank: #{fls_rank} of {len(rankings)}")
        print(f"  ✓ AI Overview mentions: {fls_data['ai_overview_mentions']}")
        print(f"  ✓ Organic mentions: {fls_data['organic_mentions']}")
        print(f"  ✓ Visibility score: {fls_data['visibility_score']}")
        print(f"  ✓ Mention rate: {len(fls_data['queries'])/processed*100:.1f}%")

        if fls_data['ai_overview_mentions'] > 0:
            print(f"\n  ✅ APPEARS IN AI OVERVIEW - GEO visibility confirmed!")
        else:
            print(f"\n  ⚠️  Not in AI Overview, but in organic results")

    else:
        print(f"First Line Software:")
        print(f"  ✗ NOT MENTIONED in any results")
        print(f"  ✗ Zero visibility in this assessment")

    # Competitor comparison
    print(f"\nCompetitors:")
    for company in ["EPAM", "DataArt", "Endava", "Luxsoft", "Projectus"]:
        comp_data = next((r for r in rankings if r["company"] == company), None)
        if comp_data:
            rank_num = next(i for i, r in enumerate(rankings, 1) if r["company"] == company)
            print(f"  {company:15} → Rank #{rank_num}, "
                  f"AI Overview: {comp_data['ai_overview_mentions']}, "
                  f"Organic: {comp_data['organic_mentions']}, "
                  f"Score: {comp_data['visibility_score']}")
        else:
            print(f"  {company:15} → Not mentioned")

    # Query category analysis
    print(f"\n\nQuery Category Performance:")
    category_stats = defaultdict(lambda: {"ai_overview": 0, "total": 0})

    for result in analyzer.query_results:
        category_stats[result["category"]]["total"] += 1
        if result["has_ai_overview"]:
            category_stats[result["category"]]["ai_overview"] += 1

    for category, stats in category_stats.items():
        rate = stats["ai_overview"] / stats["total"] * 100 if stats["total"] > 0 else 0
        print(f"  {category:20} → AI Overview: {stats['ai_overview']}/{stats['total']} ({rate:.0f}%)")

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"full_assessment_{timestamp}.json"

    results_data = {
        "timestamp": timestamp,
        "total_queries": processed,
        "ai_overview_count": ai_overview_count,
        "ai_overview_rate": ai_overview_count / processed if processed > 0 else 0,
        "rankings": rankings,
        "query_results": analyzer.query_results,
        "category_performance": dict(category_stats),
    }

    try:
        with open(filename, 'w') as f:
            json.dump(results_data, f, indent=2)
        print(f"\n\n✓ Results saved to: {filename}")
    except Exception as e:
        print(f"\n⚠️  Could not save results: {e}")

    return results_data


async def main():
    """Main entry point."""

    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║     Full Browser Assessment - 20 Comprehensive Queries       ║")
    print("║   Complete validation with company visibility tracking       ║")
    print("╚══════════════════════════════════════════════════════════════╝")

    print("\nThis comprehensive assessment will:")
    print("  • Test 20 queries across 5 categories")
    print("  • Track First Line Software + 5 competitors")
    print("  • Analyze AI Overview vs Organic mentions")
    print("  • Generate company visibility rankings")
    print("  • Provide strategic recommendations")
    print("  • Take screenshots for validation")

    input("\nPress Enter to start...")

    results = await run_full_assessment()

    print("\n" + "="*80)
    print("✅ FULL ASSESSMENT COMPLETE!")
    print("="*80)
    print("\nScreenshots saved to: screenshots/")
    print("Results saved to JSON file")
    print("\nReview screenshots to verify AI Overview presence and accuracy\n")


if __name__ == "__main__":
    asyncio.run(main())
