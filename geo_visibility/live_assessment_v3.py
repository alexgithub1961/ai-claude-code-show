"""
Live GEO Visibility Assessment using SearchAPI - Version 3
More targeted queries designed to trigger AI Overview with company mentions.
Focus on specific, informational queries that typically generate AI Overview.
"""
import asyncio
import os
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple

from src.engines import SearchAPIEngine
from src.config import CompanyConfig


# Known competitors
COMPETITORS = [
    "DataArt",
    "Endava",
    "Projectus",
    "EPAM",
    "Luxsoft",
]

# Additional variations to catch
COMPETITOR_VARIATIONS = {
    "DataArt": ["DataArt", "Data Art"],
    "Endava": ["Endava"],
    "Projectus": ["Projectus", "Protectus"],
    "EPAM": ["EPAM", "EPAM Systems"],
    "Luxsoft": ["Luxsoft", "Luxoft"],
}


# More specific queries designed to trigger AI Overview
TEST_QUERIES = {
    "AI Services Questions": [
        "what are managed AI services",
        "how to choose AI consulting company",
        "what is generative AI implementation",
        "benefits of AI outsourcing for enterprises",
        "how much does AI development cost",
    ],
    "Digital Publishing Questions": [
        "what is digital experience platform",
        "how to modernize publishing infrastructure",
        "what are headless CMS benefits",
        "digital publishing trends 2024",
        "content management system comparison",
    ],
    "Comparison and Selection": [
        "EPAM vs other IT outsourcing companies",
        "best alternatives to Endava",
        "Ukrainian IT outsourcing companies comparison",
        "top software development companies Eastern Europe",
        "DataArt competitors and alternatives",
    ],
    "Technology Deep Dive": [
        "companies specializing in AI ML solutions",
        "enterprise AI implementation services",
        "digital transformation consulting firms",
        "cloud native development companies",
        "AI powered digital publishing platforms",
    ],
    "Industry and Location Specific": [
        "Ukraine software development industry leaders",
        "Eastern European IT services companies",
        "offshore software development Ukraine vs Poland",
        "top tech companies in Kyiv Ukraine",
        "IT outsourcing industry Ukraine",
    ],
}


class CompetitorTracker:
    """Track mentions of First Line Software and competitors."""

    def __init__(self):
        self.mentions = defaultdict(lambda: {
            "count": 0,
            "queries": [],
            "positions": [],
            "contexts": [],
            "business_areas": [],
        })
        self.query_results = []
        self.company_config = CompanyConfig()

    def analyze_response(self, query: str, response_text: str, business_area: str):
        """Analyze a response for company mentions."""
        if not response_text:
            return

        found_companies = []

        # Check First Line Software
        fls_names = [self.company_config.name] + self.company_config.aliases
        for name in fls_names:
            if name.lower() in response_text.lower():
                self.mentions["First Line Software"]["count"] += 1
                self.mentions["First Line Software"]["queries"].append(query)
                self.mentions["First Line Software"]["business_areas"].append(business_area)
                self.mentions["First Line Software"]["contexts"].append(
                    response_text[:300] + "..."
                )
                position = response_text.lower().find(name.lower())
                self.mentions["First Line Software"]["positions"].append(position)
                found_companies.append("First Line Software")
                break

        # Check competitors
        for competitor in COMPETITORS:
            variations = COMPETITOR_VARIATIONS.get(competitor, [competitor])
            for variation in variations:
                if variation.lower() in response_text.lower():
                    self.mentions[competitor]["count"] += 1
                    self.mentions[competitor]["queries"].append(query)
                    self.mentions[competitor]["business_areas"].append(business_area)
                    self.mentions[competitor]["contexts"].append(
                        response_text[:300] + "..."
                    )
                    position = response_text.lower().find(variation.lower())
                    self.mentions[competitor]["positions"].append(position)
                    found_companies.append(competitor)
                    break

        self.query_results.append({
            "query": query,
            "business_area": business_area,
            "companies_found": found_companies,
            "response_length": len(response_text),
        })

    def get_rankings(self) -> List[Tuple[str, Dict]]:
        """Get companies ranked by visibility."""
        # Calculate visibility score for each company
        scored = []
        for company, data in self.mentions.items():
            if data["count"] > 0:
                # Score based on: mention count + average position (earlier is better)
                avg_position = sum(data["positions"]) / len(data["positions"])
                # Normalize position (0-1, where 0 is best)
                position_score = 1 - min(avg_position / 1000, 1)

                # Final score: 70% mention frequency, 30% position
                visibility_score = (data["count"] * 0.7) + (position_score * data["count"] * 0.3)

                scored.append((company, {
                    **data,
                    "visibility_score": visibility_score,
                    "avg_position": avg_position,
                }))

        # Sort by visibility score (descending)
        scored.sort(key=lambda x: x[1]["visibility_score"], reverse=True)
        return scored


async def run_live_assessment(api_key: str):
    """Run live GEO visibility assessment with SearchAPI."""

    print("\n" + "="*80)
    print("LIVE GEO VISIBILITY ASSESSMENT - SEARCHAPI v3")
    print("="*80 + "\n")

    print(f"Target Company: First Line Software")
    print(f"Competitors: {', '.join(COMPETITORS)}")
    print(f"Total Queries: {sum(len(queries) for queries in TEST_QUERIES.values())}\n")

    # Initialize
    engine = SearchAPIEngine(api_key=api_key)
    tracker = CompetitorTracker()

    # Run queries
    total_queries = 0
    successful_queries = 0
    queries_with_ai_overview = 0
    queries_with_mentions = 0

    for business_area, queries in TEST_QUERIES.items():
        print(f"\n{'='*80}")
        print(f"Category: {business_area}")
        print(f"{'='*80}\n")

        for i, query in enumerate(queries, 1):
            total_queries += 1
            print(f"[{total_queries}] {query}")

            try:
                response = await engine.query(query)

                if response.error:
                    print(f"     ✗ Error: {response.error[:60]}...")
                    await asyncio.sleep(1)
                    continue

                successful_queries += 1

                # Check if we got AI Overview
                has_overview = response.metadata.get("has_ai_overview", False)
                if has_overview:
                    queries_with_ai_overview += 1
                    print(f"     ✓ Google AI Overview")
                else:
                    print(f"     ℹ Organic results")

                print(f"     Length: {len(response.response_text)} chars")

                # Analyze for company mentions
                tracker.analyze_response(query, response.response_text, business_area)

                # Check what was mentioned in this response
                mentioned = []
                if "First Line" in response.response_text or "FLS" in response.response_text:
                    mentioned.append("FLS")
                for comp in COMPETITORS:
                    for var in COMPETITOR_VARIATIONS.get(comp, [comp]):
                        if var.lower() in response.response_text.lower():
                            mentioned.append(comp)
                            break

                if mentioned:
                    queries_with_mentions += 1
                    print(f"     → Mentioned: {', '.join(mentioned)}")

                # Rate limiting
                await asyncio.sleep(2)

            except Exception as e:
                print(f"     ✗ Exception: {str(e)[:60]}...")
                await asyncio.sleep(1)

    # Generate rankings
    print("\n\n" + "="*80)
    print("📊 GEO VISIBILITY RANKINGS")
    print("="*80 + "\n")

    rankings = tracker.get_rankings()

    print(f"Query Statistics:")
    print(f"  Total queries executed: {total_queries}")
    print(f"  Successful responses: {successful_queries}")
    print(f"  With AI Overview: {queries_with_ai_overview}")
    print(f"  Queries with company mentions: {queries_with_mentions}\n")

    if not rankings:
        print("⚠️  No target companies were mentioned in any responses\n")
        print("Analysis:")
        print("  • These queries may not typically mention specific vendor names")
        print("  • Google AI Overview may be more generic for these topics")
        print("  • SearchAPI may not have returned AI Overview for many queries")
        print("\nThis indicates limited GEO visibility for these query types.")
        return None

    # Create ranking table
    print(f"\n{'RANK':<6} {'COMPANY':<30} {'MENTIONS':<10} {'AVG POS':<12} {'SCORE':<8}")
    print("="*80)

    for rank, (company, data) in enumerate(rankings, 1):
        is_fls = company == "First Line Software"
        marker = " ⭐" if is_fls else ""
        company_display = company + marker

        print(f"{rank:<6} {company_display:<30} {data['count']:<10} "
              f"{data['avg_position']:<12.0f} {data['visibility_score']:<8.2f}")

    # Detailed breakdown
    print("\n\n" + "="*80)
    print("📋 DETAILED BREAKDOWN")
    print("="*80)

    for rank, (company, data) in enumerate(rankings, 1):
        print(f"\n{rank}. {company}")
        print("-" * 70)
        print(f"   Total Mentions: {data['count']}")
        print(f"   Visibility Score: {data['visibility_score']:.2f}")
        print(f"   Average Position: {data['avg_position']:.0f} chars")
        print(f"   Mentioned in queries:")
        unique_queries = list(set(data['queries']))[:5]
        for query in unique_queries:
            print(f"     • {query}")

        if data['contexts']:
            print(f"\n   Example context:")
            context = data['contexts'][0].replace('\n', ' ')[:250]
            print(f'     "{context}..."')

    # Summary
    print("\n\n" + "="*80)
    print("📈 SUMMARY")
    print("="*80 + "\n")

    # First Line Software specific
    fls_data = next((data for comp, data in rankings if comp == "First Line Software"), None)
    if fls_data:
        fls_rank = next(i for i, (c, _) in enumerate(rankings, 1) if c == "First Line Software")
        print(f"First Line Software:")
        print(f"  ✓ Rank: #{fls_rank} of {len(rankings)}")
        print(f"  ✓ Mentions: {fls_data['count']}")
        print(f"  ✓ Visibility Score: {fls_data['visibility_score']:.2f}")
        print(f"  ✓ Mention Rate: {fls_data['count']/successful_queries*100:.1f}%")
    else:
        print(f"First Line Software:")
        print(f"  ✗ NOT MENTIONED in any responses")
        print(f"  ✗ Current GEO visibility: Very Low")

    # Competitor comparison
    print(f"\nCompetitors:")
    for competitor in COMPETITORS:
        comp_data = next((data for comp, data in rankings if comp == competitor), None)
        if comp_data:
            rank = next(i for i, (c, _) in enumerate(rankings, 1) if c == competitor)
            print(f"  {competitor:12} → Rank #{rank:2}, {comp_data['count']:2} mentions, Score: {comp_data['visibility_score']:.2f}")
        else:
            print(f"  {competitor:12} → Not mentioned")

    print("\n" + "="*80)
    return rankings


async def main():
    """Main entry point."""
    api_key = "dUngVqvqnKPAr1p1BKqKENJW"

    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║     Live GEO Visibility Assessment with SearchAPI v3        ║")
    print("║     First Line Software vs. Major Competitors                ║")
    print("║     Improved query targeting for AI Overview                 ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")

    try:
        rankings = await run_live_assessment(api_key)

        print("\n✅ Assessment completed!")

        if rankings:
            print("\n💡 Key Insights:")
            print("  • Companies with higher visibility are mentioned more frequently")
            print("  • Check which types of queries trigger company mentions")
            print("  • Analyze competitors' content strategy for GEO optimization")
            print("  • Focus on creating content that answers common questions")
        else:
            print("\n💡 Key Finding:")
            print("  • Current queries don't trigger company mentions in AI Overview")
            print("  • Google AI Overview may not include vendor names for these topics")
            print("  • Consider branded content marketing and thought leadership")
            print("  • Focus on specific use cases and success stories")

    except Exception as e:
        print(f"\n✗ Assessment failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
