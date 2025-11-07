"""
Live GEO Visibility Assessment using SearchAPI.
Compares First Line Software against known competitors.
"""
import asyncio
import os
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple

from src.engines import SearchAPIEngine
from src.config import BusinessArea, QueryCategory, CompanyConfig
from src.analyzers import CompanyDetector, VisibilityAnalyzer


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
    "Projectus": ["Projectus", "Protectus"],  # In case of typo
    "EPAM": ["EPAM", "EPAM Systems"],
    "Luxsoft": ["Luxsoft", "Luxoft"],  # Common variation
}


# Test queries focused on our business areas
TEST_QUERIES = {
    "Gen AI / Managed AI Services": [
        "best managed AI services for enterprises",
        "AI consulting companies 2024",
        "generative AI development partners",
        "custom LLM implementation services",
        "enterprise AI transformation consulting",
    ],
    "Digital Publishing / DX": [
        "digital publishing platform development companies",
        "enterprise content management solutions providers",
        "headless CMS development services",
        "digital experience platform developers",
        "publishing technology companies",
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
        })
        self.company_config = CompanyConfig()

    def analyze_response(self, query: str, response_text: str, business_area: str):
        """Analyze a response for company mentions."""
        if not response_text:
            return

        # Check First Line Software
        fls_names = [self.company_config.name] + self.company_config.aliases
        for name in fls_names:
            if name.lower() in response_text.lower():
                self.mentions["First Line Software"]["count"] += 1
                self.mentions["First Line Software"]["queries"].append(query)
                self.mentions["First Line Software"]["contexts"].append(
                    response_text[:200] + "..."
                )
                position = response_text.lower().find(name.lower())
                self.mentions["First Line Software"]["positions"].append(position)
                break

        # Check competitors
        for competitor in COMPETITORS:
            variations = COMPETITOR_VARIATIONS.get(competitor, [competitor])
            for variation in variations:
                if variation.lower() in response_text.lower():
                    self.mentions[competitor]["count"] += 1
                    self.mentions[competitor]["queries"].append(query)
                    self.mentions[competitor]["contexts"].append(
                        response_text[:200] + "..."
                    )
                    position = response_text.lower().find(variation.lower())
                    self.mentions[competitor]["positions"].append(position)
                    break

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
    print("LIVE GEO VISIBILITY ASSESSMENT")
    print("Using SearchAPI for Real Google AI Overview Results")
    print("="*80 + "\n")

    print(f"Target Company: First Line Software")
    print(f"Competitors: {', '.join(COMPETITORS)}")
    print(f"Total Queries: {sum(len(queries) for queries in TEST_QUERIES.values())}\n")

    # Initialize
    engine = SearchAPIEngine(api_key=api_key)
    tracker = CompetitorTracker()

    # Track all responses
    all_results = []

    # Run queries
    for business_area, queries in TEST_QUERIES.items():
        print(f"\n{'='*80}")
        print(f"Business Area: {business_area}")
        print(f"{'='*80}\n")

        for i, query in enumerate(queries, 1):
            print(f"Query {i}/{len(queries)}: {query}")

            try:
                response = await engine.query(query)

                if response.error:
                    print(f"  ✗ Error: {response.error}")
                    continue

                # Check if we got AI Overview
                has_overview = response.metadata.get("has_ai_overview", False)
                if has_overview:
                    print(f"  ✓ Google AI Overview retrieved")
                else:
                    print(f"  ℹ Using organic results (no AI Overview)")

                print(f"  Response length: {len(response.response_text)} chars")

                # Analyze for company mentions
                tracker.analyze_response(query, response.response_text, business_area)

                # Check what was mentioned in this response
                mentioned = []
                if "First Line" in response.response_text or "FLS" in response.response_text:
                    mentioned.append("First Line Software")
                for comp in COMPETITORS:
                    for var in COMPETITOR_VARIATIONS.get(comp, [comp]):
                        if var.lower() in response.response_text.lower():
                            mentioned.append(comp)
                            break

                if mentioned:
                    print(f"  Companies mentioned: {', '.join(mentioned)}")
                else:
                    print(f"  No target companies mentioned")

                all_results.append({
                    "query": query,
                    "business_area": business_area,
                    "response": response.response_text,
                    "has_overview": has_overview,
                    "mentioned": mentioned,
                })

                # Rate limiting
                await asyncio.sleep(1)

            except Exception as e:
                print(f"  ✗ Exception: {e}")

    # Generate rankings
    print("\n\n" + "="*80)
    print("GEO VISIBILITY RANKINGS")
    print("="*80 + "\n")

    rankings = tracker.get_rankings()

    if not rankings:
        print("⚠️  No companies were mentioned in any responses")
        print("\nThis could mean:")
        print("  • Queries are too generic")
        print("  • Google AI doesn't mention specific vendors")
        print("  • Companies don't have strong SEO for these queries")
        return

    # Create ranking table
    print(f"{'Rank':<6} {'Company':<25} {'Mentions':<10} {'Avg Position':<15} {'Visibility Score':<20}")
    print("-" * 80)

    for rank, (company, data) in enumerate(rankings, 1):
        is_fls = company == "First Line Software"
        marker = " ⭐" if is_fls else ""

        print(f"{rank:<6} {company:<25}{marker} {data['count']:<10} "
              f"{data['avg_position']:<15.0f} {data['visibility_score']:<20.2f}")

    # Detailed breakdown
    print("\n\n" + "="*80)
    print("DETAILED BREAKDOWN")
    print("="*80 + "\n")

    for rank, (company, data) in enumerate(rankings, 1):
        print(f"\n{rank}. {company}")
        print("-" * 80)
        print(f"Total Mentions: {data['count']}")
        print(f"Visibility Score: {data['visibility_score']:.2f}")
        print(f"Average Position: {data['avg_position']:.0f} characters into response")
        print(f"\nMentioned in queries:")
        for query in set(data['queries']):
            print(f"  • {query}")

        if data['contexts']:
            print(f"\nFirst mention context:")
            print(f'  "{data["contexts"][0]}"')

    # Summary statistics
    print("\n\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80 + "\n")

    total_queries = sum(len(queries) for queries in TEST_QUERIES.values())
    total_with_mentions = sum(1 for r in all_results if r['mentioned'])

    print(f"Total Queries Executed: {total_queries}")
    print(f"Queries with Company Mentions: {total_with_mentions} ({total_with_mentions/total_queries*100:.1f}%)")
    print(f"Unique Companies Mentioned: {len(rankings)}")
    print(f"Total Company Mentions: {sum(data['count'] for _, data in rankings)}")

    # First Line Software specific
    fls_data = next((data for comp, data in rankings if comp == "First Line Software"), None)
    if fls_data:
        print(f"\nFirst Line Software:")
        print(f"  Rank: #{next(i for i, (c, _) in enumerate(rankings, 1) if c == 'First Line Software')}")
        print(f"  Mentions: {fls_data['count']}")
        print(f"  Mention Rate: {fls_data['count']/total_queries*100:.1f}%")
        print(f"  Visibility Score: {fls_data['visibility_score']:.2f}")
    else:
        print(f"\n⚠️  First Line Software: NOT MENTIONED in any responses")
        print(f"  This indicates low GEO visibility for these query types")

    # Competitor comparison
    print(f"\nCompetitors:")
    for competitor in COMPETITORS:
        comp_data = next((data for comp, data in rankings if comp == competitor), None)
        if comp_data:
            rank = next(i for i, (c, _) in enumerate(rankings, 1) if c == competitor)
            print(f"  {competitor}: Rank #{rank}, {comp_data['count']} mentions")
        else:
            print(f"  {competitor}: Not mentioned")

    print("\n" + "="*80)
    print("ASSESSMENT COMPLETE")
    print("="*80 + "\n")

    return rankings, all_results


async def main():
    """Main entry point."""
    api_key = "dUngVqvqnKPAr1p1BKqKENJW"

    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║     Live GEO Visibility Assessment with SearchAPI           ║")
    print("║     First Line Software vs. Competitors                      ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")

    print("Starting live assessment...")
    print("This will query Google AI Overview for real visibility data\n")

    try:
        rankings, results = await run_live_assessment(api_key)

        print("\n✅ Assessment completed successfully!")
        print("\nNext steps:")
        print("  1. Review the rankings above")
        print("  2. Analyze which queries mention competitors but not FLS")
        print("  3. Optimize content strategy based on findings")
        print("  4. Re-run assessment after implementing changes\n")

    except Exception as e:
        print(f"\n✗ Assessment failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
