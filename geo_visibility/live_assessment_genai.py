"""
Live GEO Visibility Assessment - Generative AI & LLM Focus
Queries based on how potential customers search for AI consultancy services.
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


# Customer-focused queries for GenAI/LLM consultancy
TEST_QUERIES = {
    "LLM Implementation & Integration": [
        "how to implement large language models in enterprise",
        "companies that integrate ChatGPT into business applications",
        "consultants for LLM implementation",
        "building custom LLM applications for business",
        "enterprise LLM integration services",
        "who can help integrate OpenAI API into our product",
        "best companies for GPT-4 enterprise integration",
        "LLM consulting firms for startups",
    ],

    "RAG Solutions": [
        "what is RAG retrieval augmented generation",
        "companies that build RAG solutions",
        "how to implement RAG for enterprise knowledge base",
        "RAG architecture consulting services",
        "building AI that searches company documents",
        "consultants for semantic search implementation",
        "RAG vs fine-tuning for business applications",
        "who can build custom RAG system",
    ],

    "AI Chatbots & Assistants": [
        "building custom AI chatbot for customer service",
        "companies that develop AI assistants",
        "enterprise chatbot development services",
        "how to build intelligent virtual assistant",
        "AI chatbot consulting for e-commerce",
        "custom GPT chatbot development",
        "conversational AI implementation services",
        "firms that build AI customer support agents",
    ],

    "AI Search & Discovery": [
        "implementing AI-powered search for website",
        "semantic search development services",
        "building intelligent search with AI",
        "companies that do vector search implementation",
        "AI search engine consulting",
        "embedding-based search for enterprise",
        "neural search implementation firms",
        "intelligent document retrieval systems",
    ],

    "Generative AI Strategy & Consulting": [
        "generative AI consulting for enterprises",
        "how to start with generative AI in business",
        "GenAI strategy consulting firms",
        "companies that advise on AI implementation",
        "generative AI readiness assessment",
        "AI transformation consulting services",
        "which generative AI use cases for my industry",
        "AI strategy consultants for financial services",
    ],

    "Prompt Engineering & LLM Optimization": [
        "prompt engineering services for enterprises",
        "companies that optimize LLM performance",
        "how to improve LLM accuracy for business use",
        "consultants for prompt optimization",
        "LLM fine-tuning services",
        "improving AI model outputs for production",
        "firms that specialize in LLM customization",
        "GPT model optimization consulting",
    ],

    "AI Infrastructure & MLOps": [
        "MLOps for generative AI applications",
        "infrastructure for running LLMs in production",
        "companies that build AI pipelines",
        "LLMOps consulting services",
        "deploying large language models at scale",
        "AI infrastructure consulting firms",
        "production-ready LLM deployment",
        "who can help with AI model monitoring",
    ],

    "Industry-Specific AI Solutions": [
        "generative AI for financial services companies",
        "AI solutions for healthcare documentation",
        "LLM applications for legal industry",
        "AI for customer service automation",
        "generative AI in manufacturing",
        "AI consulting for retail personalization",
        "insurance companies using generative AI",
        "AI implementation in pharmaceutical research",
    ],

    "Vendor Selection & Comparison": [
        "best AI consulting companies 2024",
        "top generative AI development firms",
        "AI consultants vs in-house development",
        "comparing AI consulting firms",
        "most experienced LLM integration companies",
        "AI development agencies for startups",
        "offshore vs nearshore AI development",
        "Eastern European AI consulting firms",
    ],

    "Problem-Based Queries": [
        "how to reduce LLM hallucinations in production",
        "making AI responses more accurate for business",
        "controlling costs of OpenAI API usage",
        "ensuring AI safety and compliance",
        "preventing data leaks with AI applications",
        "improving AI response quality",
        "handling sensitive data with LLMs",
        "making AI outputs consistent and reliable",
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
        scored = []
        for company, data in self.mentions.items():
            if data["count"] > 0:
                avg_position = sum(data["positions"]) / len(data["positions"])
                position_score = 1 - min(avg_position / 1000, 1)
                visibility_score = (data["count"] * 0.7) + (position_score * data["count"] * 0.3)

                scored.append((company, {
                    **data,
                    "visibility_score": visibility_score,
                    "avg_position": avg_position,
                }))

        scored.sort(key=lambda x: x[1]["visibility_score"], reverse=True)
        return scored


async def run_live_assessment(api_key: str):
    """Run live GEO visibility assessment with SearchAPI."""

    print("\n" + "="*80)
    print("LIVE GEO VISIBILITY ASSESSMENT - GENERATIVE AI & LLM FOCUS")
    print("="*80 + "\n")

    print(f"Target Company: First Line Software")
    print(f"Competitors: {', '.join(COMPETITORS)}")
    total_queries_count = sum(len(queries) for queries in TEST_QUERIES.values())
    print(f"Total Queries: {total_queries_count}\n")
    print("Focus: Customer search patterns for GenAI/LLM consultancy services\n")

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
            print(f"[{total_queries}/{total_queries_count}] {query}")

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

                # Rate limiting - be nice to the API
                await asyncio.sleep(2)

            except Exception as e:
                print(f"     ✗ Exception: {str(e)[:60]}...")
                await asyncio.sleep(1)

    # Generate rankings
    print("\n\n" + "="*80)
    print("📊 GEO VISIBILITY RANKINGS - GENERATIVE AI QUERIES")
    print("="*80 + "\n")

    rankings = tracker.get_rankings()

    print(f"Query Statistics:")
    print(f"  Total queries executed: {total_queries}")
    print(f"  Successful responses: {successful_queries}")
    print(f"  With AI Overview: {queries_with_ai_overview}")
    print(f"  Queries with company mentions: {queries_with_mentions}")
    if successful_queries > 0:
        print(f"  AI Overview rate: {queries_with_ai_overview/successful_queries*100:.1f}%")
        print(f"  Mention rate: {queries_with_mentions/successful_queries*100:.1f}%\n")

    if not rankings:
        print("⚠️  No target companies were mentioned in any responses\n")
        print("Analysis:")
        print("  • GenAI/LLM queries also don't trigger vendor mentions")
        print("  • Google AI Overview focuses on technical explanations")
        print("  • Even emerging tech queries avoid company recommendations")
        print("\nFinding: GEO visibility challenge extends to cutting-edge tech queries.")
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
    print("📋 DETAILED BREAKDOWN BY QUERY CATEGORY")
    print("="*80)

    for rank, (company, data) in enumerate(rankings, 1):
        print(f"\n{rank}. {company}")
        print("-" * 70)
        print(f"   Total Mentions: {data['count']}")
        print(f"   Visibility Score: {data['visibility_score']:.2f}")
        print(f"   Average Position: {data['avg_position']:.0f} chars")

        # Group by business area
        areas = {}
        for area in data['business_areas']:
            areas[area] = areas.get(area, 0) + 1

        print(f"\n   Mentions by category:")
        for area, count in sorted(areas.items(), key=lambda x: x[1], reverse=True):
            print(f"     • {area}: {count} mention(s)")

        print(f"\n   Sample queries where mentioned:")
        unique_queries = list(set(data['queries']))[:5]
        for query in unique_queries:
            print(f"     • {query}")

        if data['contexts']:
            print(f"\n   Example context:")
            context = data['contexts'][0].replace('\n', ' ')[:250]
            print(f'     "{context}..."')

    # Summary
    print("\n\n" + "="*80)
    print("📈 SUMMARY - GENERATIVE AI SEARCH PATTERNS")
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
        print(f"\n  Strong categories:")
        areas = {}
        for area in fls_data['business_areas']:
            areas[area] = areas.get(area, 0) + 1
        for area, count in sorted(areas.items(), key=lambda x: x[1], reverse=True)[:3]:
            print(f"    • {area}: {count} mentions")
    else:
        print(f"First Line Software:")
        print(f"  ✗ NOT MENTIONED in any responses")
        print(f"  ✗ GenAI-specific queries show same GEO visibility gap")

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
    print("║  GEO Visibility - Generative AI & LLM Customer Queries      ║")
    print("║  How potential customers search for AI consultancy services  ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")

    try:
        rankings = await run_live_assessment(api_key)

        print("\n✅ Assessment completed!")

        if rankings:
            print("\n💡 Key Insights:")
            print("  • Identified query patterns that trigger company mentions")
            print("  • Found categories where First Line Software has visibility")
            print("  • Discovered competitive positioning opportunities")
            print("  • Can optimize content strategy for high-performing query types")
        else:
            print("\n💡 Key Finding:")
            print("  • Even GenAI-specific queries don't trigger vendor mentions")
            print("  • Google focuses on technical education, not recommendations")
            print("  • Confirms GEO visibility challenge is systematic, not company-specific")
            print("\n💡 Recommendations:")
            print("  • Create comprehensive GenAI/LLM educational content")
            print("  • Target \"how-to\" queries rather than \"who can help\" queries")
            print("  • Build authority through case studies and technical deep-dives")
            print("  • Focus on problem-solving content that builds trust")

    except Exception as e:
        print(f"\n✗ Assessment failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
