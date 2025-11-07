"""
Traditional SEO Visibility Checker
Analyzes organic search results (not AI Overview) to compare SEO performance.
"""
import asyncio
import os
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple
import httpx

from src.config import CompanyConfig


# Companies to track
COMPANIES = {
    "First Line Software": ["First Line Software", "First Line", "FLS", "firstlinesoftware.com"],
    "DataArt": ["DataArt", "Data Art", "dataart.com"],
    "Endava": ["Endava", "endava.com"],
    "Projectus": ["Projectus", "Protectus", "projectus.com"],
    "EPAM": ["EPAM", "EPAM Systems", "epam.com"],
    "Luxsoft": ["Luxsoft", "Luxoft", "luxoft.com", "luxsofttech.com"],
}


# Key service queries for SEO visibility
SEO_TEST_QUERIES = {
    "GenAI Services": [
        "generative AI consulting services",
        "LLM implementation companies",
        "enterprise AI chatbot development",
        "RAG solution providers",
        "AI integration consulting firms",
    ],

    "Software Development": [
        "custom software development Ukraine",
        "offshore software development Eastern Europe",
        "enterprise software development services",
        "software consulting companies",
        "IT outsourcing Ukraine",
    ],

    "Digital Publishing": [
        "digital publishing platform development",
        "content management system development",
        "headless CMS implementation services",
        "digital experience platform consulting",
        "publishing technology solutions",
    ],

    "AI/ML Services": [
        "machine learning consulting companies",
        "AI implementation services",
        "ML model development services",
        "artificial intelligence consulting firms",
        "enterprise AI solutions",
    ],

    "Technology Consulting": [
        "technology consulting firms",
        "digital transformation consultants",
        "cloud native development services",
        "software architecture consulting",
        "technical consulting companies",
    ],
}


class SEOVisibilityTracker:
    """Track organic search visibility for companies."""

    def __init__(self):
        self.results = []
        self.company_positions = defaultdict(list)
        self.company_appearances = defaultdict(int)

    def analyze_organic_results(self, query: str, organic_results: List[Dict], category: str):
        """Analyze organic search results for company mentions."""
        query_result = {
            "query": query,
            "category": category,
            "companies_found": {},
        }

        for position, result in enumerate(organic_results, start=1):
            title = result.get("title", "").lower()
            snippet = result.get("snippet", "").lower()
            link = result.get("link", "").lower()
            domain = result.get("domain", "").lower()

            for company, variations in COMPANIES.items():
                found = False
                match_type = None

                # Check domain match (strongest signal)
                for variation in variations:
                    if ".com" in variation or ".net" in variation:
                        if variation.lower() in domain:
                            found = True
                            match_type = "domain"
                            break

                # Check title match
                if not found:
                    for variation in variations:
                        if ".com" not in variation and variation.lower() in title:
                            found = True
                            match_type = "title"
                            break

                # Check snippet match
                if not found:
                    for variation in variations:
                        if ".com" not in variation and variation.lower() in snippet:
                            found = True
                            match_type = "snippet"
                            break

                # Check URL match
                if not found:
                    for variation in variations:
                        if ".com" not in variation and variation.lower() in link:
                            found = True
                            match_type = "url"
                            break

                if found:
                    if company not in query_result["companies_found"]:
                        query_result["companies_found"][company] = []

                    query_result["companies_found"][company].append({
                        "position": position,
                        "match_type": match_type,
                        "title": result.get("title", ""),
                        "link": result.get("link", ""),
                    })

                    self.company_positions[company].append({
                        "query": query,
                        "category": category,
                        "position": position,
                        "match_type": match_type,
                    })

                    self.company_appearances[company] += 1

        self.results.append(query_result)

    def get_rankings(self) -> List[Tuple[str, Dict]]:
        """Get companies ranked by SEO visibility."""
        company_scores = []

        for company in COMPANIES.keys():
            if company not in self.company_appearances or self.company_appearances[company] == 0:
                continue

            positions = self.company_positions[company]
            total_appearances = len(positions)

            # Calculate average position (lower is better)
            avg_position = sum(p["position"] for p in positions) / total_appearances

            # Calculate position score (top 3 is best)
            top3_count = sum(1 for p in positions if p["position"] <= 3)
            top10_count = sum(1 for p in positions if p["position"] <= 10)

            # Domain matches are strongest signal
            domain_matches = sum(1 for p in positions if p["match_type"] == "domain")

            # Visibility score: weighted combination
            visibility_score = (
                (top3_count * 10) +      # Top 3 positions are gold
                (top10_count * 5) +      # Top 10 is good
                (domain_matches * 15) +  # Domain matches are best
                (total_appearances * 2)  # More appearances = better
            ) / avg_position             # Penalize lower average position

            company_scores.append((company, {
                "total_appearances": total_appearances,
                "avg_position": avg_position,
                "top3_count": top3_count,
                "top10_count": top10_count,
                "domain_matches": domain_matches,
                "visibility_score": visibility_score,
                "positions": positions,
            }))

        # Sort by visibility score
        company_scores.sort(key=lambda x: x[1]["visibility_score"], reverse=True)
        return company_scores


async def run_seo_visibility_check(api_key: str):
    """Run SEO visibility check using SearchAPI."""

    print("\n" + "="*80)
    print("TRADITIONAL SEO VISIBILITY CHECK")
    print("Organic Search Results Analysis (Not AI Overview)")
    print("="*80 + "\n")

    print(f"Companies Tracked: {len(COMPANIES)}")
    print(f"  - First Line Software")
    for comp in COMPANIES.keys():
        if comp != "First Line Software":
            print(f"  - {comp}")

    total_queries_count = sum(len(queries) for queries in SEO_TEST_QUERIES.values())
    print(f"\nTotal Queries: {total_queries_count}\n")

    tracker = SEOVisibilityTracker()
    base_url = "https://www.searchapi.io/api/v1/search"

    total_queries = 0
    successful_queries = 0

    for category, queries in SEO_TEST_QUERIES.items():
        print(f"\n{'='*80}")
        print(f"Category: {category}")
        print(f"{'='*80}\n")

        for query in queries:
            total_queries += 1
            print(f"[{total_queries}/{total_queries_count}] {query}")

            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        base_url,
                        params={
                            "q": query,
                            "api_key": api_key,
                            "engine": "google",
                            "num": 20,  # Get top 20 results
                        },
                        timeout=30.0,
                    )

                    if response.status_code != 200:
                        print(f"     ✗ Error: {response.status_code}")
                        await asyncio.sleep(1)
                        continue

                    data = response.json()
                    organic_results = data.get("organic_results", [])

                    if not organic_results:
                        print(f"     ✗ No organic results")
                        await asyncio.sleep(1)
                        continue

                    successful_queries += 1
                    print(f"     ✓ Got {len(organic_results)} organic results")

                    # Analyze results
                    tracker.analyze_organic_results(query, organic_results, category)

                    # Show what was found
                    found_companies = []
                    result = tracker.results[-1]
                    for company, matches in result["companies_found"].items():
                        positions = [m["position"] for m in matches]
                        best_pos = min(positions)
                        found_companies.append(f"{company}(#{best_pos})")

                    if found_companies:
                        print(f"     → Found: {', '.join(found_companies)}")

                    await asyncio.sleep(2)

            except Exception as e:
                print(f"     ✗ Exception: {str(e)[:60]}...")
                await asyncio.sleep(1)

    # Generate rankings
    print("\n\n" + "="*80)
    print("📊 SEO VISIBILITY RANKINGS - ORGANIC SEARCH RESULTS")
    print("="*80 + "\n")

    rankings = tracker.get_rankings()

    print(f"Query Statistics:")
    print(f"  Total queries executed: {total_queries}")
    print(f"  Successful responses: {successful_queries}")
    print(f"  Companies with visibility: {len(rankings)}\n")

    if not rankings:
        print("⚠️  No companies found in organic results\n")
        return None

    # Rankings table
    print(f"\n{'RANK':<6} {'COMPANY':<25} {'APPEAR':<8} {'AVG POS':<10} {'TOP 3':<8} {'TOP 10':<8} {'SCORE':<10}")
    print("="*80)

    for rank, (company, data) in enumerate(rankings, 1):
        is_fls = company == "First Line Software"
        marker = " ⭐" if is_fls else ""
        company_display = company + marker

        print(f"{rank:<6} {company_display:<25} {data['total_appearances']:<8} "
              f"{data['avg_position']:<10.1f} {data['top3_count']:<8} "
              f"{data['top10_count']:<8} {data['visibility_score']:<10.1f}")

    # Detailed analysis
    print("\n\n" + "="*80)
    print("📋 DETAILED SEO ANALYSIS")
    print("="*80)

    for rank, (company, data) in enumerate(rankings, 1):
        print(f"\n{rank}. {company}")
        print("-" * 70)
        print(f"   Total Appearances: {data['total_appearances']}")
        print(f"   Average Position: {data['avg_position']:.1f}")
        print(f"   Top 3 Positions: {data['top3_count']}")
        print(f"   Top 10 Positions: {data['top10_count']}")
        print(f"   Domain Matches: {data['domain_matches']}")
        print(f"   SEO Visibility Score: {data['visibility_score']:.1f}")

        # Group by category
        categories = {}
        for pos in data['positions']:
            cat = pos['category']
            categories[cat] = categories.get(cat, 0) + 1

        print(f"\n   Appearances by category:")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"     • {cat}: {count} appearances")

        # Show best positions
        top_positions = sorted(data['positions'], key=lambda x: x['position'])[:5]
        if top_positions:
            print(f"\n   Top 5 positions:")
            for pos in top_positions:
                print(f"     • #{pos['position']} - {pos['query']} ({pos['match_type']} match)")

    # Summary
    print("\n\n" + "="*80)
    print("📈 SEO VISIBILITY SUMMARY")
    print("="*80 + "\n")

    fls_data = next((data for comp, data in rankings if comp == "First Line Software"), None)
    if fls_data:
        fls_rank = next(i for i, (c, _) in enumerate(rankings, 1) if c == "First Line Software")
        print(f"First Line Software:")
        print(f"  Rank: #{fls_rank} of {len(rankings)}")
        print(f"  Total Appearances: {fls_data['total_appearances']}")
        print(f"  Average Position: {fls_data['avg_position']:.1f}")
        print(f"  Top 3 Positions: {fls_data['top3_count']}")
        print(f"  Top 10 Positions: {fls_data['top10_count']}")
        print(f"  Visibility Score: {fls_data['visibility_score']:.1f}")

        if successful_queries > 0:
            appearance_rate = (fls_data['total_appearances'] / successful_queries) * 100
            print(f"  Appearance Rate: {appearance_rate:.1f}% of queries")
    else:
        print(f"First Line Software:")
        print(f"  ✗ NOT FOUND in any organic search results")
        print(f"  ✗ Zero traditional SEO visibility for tested queries")

    print(f"\nCompetitors:")
    for competitor in COMPANIES.keys():
        if competitor == "First Line Software":
            continue
        comp_data = next((data for comp, data in rankings if comp == competitor), None)
        if comp_data:
            rank = next(i for i, (c, _) in enumerate(rankings, 1) if c == competitor)
            print(f"  {competitor:20} → Rank #{rank}, {comp_data['total_appearances']} appearances, "
                  f"Avg pos {comp_data['avg_position']:.1f}, Score {comp_data['visibility_score']:.1f}")
        else:
            print(f"  {competitor:20} → Not found in organic results")

    print("\n" + "="*80)
    return rankings


async def main():
    """Main entry point."""
    api_key = "dUngVqvqnKPAr1p1BKqKENJW"

    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║           Traditional SEO Visibility Assessment             ║")
    print("║    Organic Search Rankings (Not AI Overview/GEO)            ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")

    print("This assessment checks WHERE companies appear in traditional")
    print("organic search results, not whether they're mentioned in AI Overview.\n")

    try:
        rankings = await run_seo_visibility_check(api_key)

        print("\n✅ SEO Visibility Check completed!")

        if rankings:
            print("\n💡 Key Insights:")
            print("  • Shows traditional SEO performance vs GEO performance")
            print("  • Identifies which query types have visibility")
            print("  • Reveals competitive positioning in organic search")
            print("  • Can guide SEO optimization priorities")
        else:
            print("\n⚠️ No Traditional SEO Visibility:")
            print("  • Companies not appearing in organic results")
            print("  • May need broader SEO strategy")
            print("  • Different query types may be needed")

    except Exception as e:
        print(f"\n✗ Assessment failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
