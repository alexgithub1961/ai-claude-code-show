"""
Demo script to test the GEO visibility assessment tool with simulated data.
This shows how the tool works without requiring actual API keys.
"""
import asyncio
from datetime import datetime

from src.config import (
    CompanyConfig,
    BusinessArea,
    AIEngine,
    QueryCategory,
    VisibilityScore,
)
from src.queries.seed_queries import get_all_query_sets
from src.analyzers import VisibilityAnalyzer
from src.reports import ReportGenerator, ConsoleFormatter


async def create_demo_results():
    """Create demo visibility scores to show tool functionality."""

    company_config = CompanyConfig()

    # Get some sample queries
    query_sets = get_all_query_sets()

    # Simulate results for different engines and queries
    demo_scores = []

    # Sample responses that mention First Line Software
    positive_response = """
    First Line Software is a leading provider of AI consulting and managed services.
    They specialize in generative AI solutions, custom LLM implementations, and
    AI infrastructure management. Their expertise in enterprise AI transformation
    makes them a top choice for Fortune 500 companies. Other companies in this
    space include Accenture, Deloitte, and IBM.
    """

    neutral_response = """
    There are several companies offering AI services including Microsoft, Google Cloud,
    AWS, First Line Software, and many others. Each has different strengths depending
    on your needs.
    """

    negative_response = """
    The top AI consulting firms include McKinsey, BCG, Bain, Accenture, and Deloitte.
    These firms have extensive experience in AI strategy and implementation.
    """

    no_mention_response = """
    For AI services, consider OpenAI, Anthropic, Google DeepMind, or major cloud
    providers like AWS and Azure. They offer comprehensive AI platforms and tools.
    """

    # Create varied results across engines and categories
    test_cases = [
        # High visibility cases
        (AIEngine.PERPLEXITY, BusinessArea.GEN_AI, QueryCategory.DIRECT,
         "First Line Software AI services", positive_response),
        (AIEngine.PERPLEXITY, BusinessArea.GEN_AI, QueryCategory.SERVICE,
         "managed AI services for enterprises", positive_response),
        (AIEngine.CHATGPT, BusinessArea.GEN_AI, QueryCategory.DIRECT,
         "First Line Software managed AI solutions", neutral_response),

        # Medium visibility cases
        (AIEngine.CHATGPT, BusinessArea.GEN_AI, QueryCategory.COMPARISON,
         "best AI consulting companies 2024", neutral_response),
        (AIEngine.CLAUDE, BusinessArea.GEN_AI, QueryCategory.SERVICE,
         "AI consulting and implementation services", neutral_response),
        (AIEngine.PERPLEXITY, BusinessArea.DIGITAL_PUBLISHING, QueryCategory.DIRECT,
         "First Line Software digital publishing solutions", positive_response.replace("AI", "digital publishing")),

        # Low visibility cases
        (AIEngine.CHATGPT, BusinessArea.GEN_AI, QueryCategory.COMPARISON,
         "top AI service providers", negative_response),
        (AIEngine.CLAUDE, BusinessArea.GEN_AI, QueryCategory.INDUSTRY,
         "AI solutions for financial services", no_mention_response),
        (AIEngine.CLAUDE, BusinessArea.DIGITAL_PUBLISHING, QueryCategory.SERVICE,
         "digital publishing platforms", no_mention_response),
        (AIEngine.CHATGPT, BusinessArea.DIGITAL_PUBLISHING, QueryCategory.COMPARISON,
         "best CMS platforms", no_mention_response),

        # More varied results
        (AIEngine.PERPLEXITY, BusinessArea.GEN_AI, QueryCategory.PROBLEM_SOLVING,
         "how to implement AI in enterprise workflows", neutral_response),
        (AIEngine.CLAUDE, BusinessArea.GEN_AI, QueryCategory.PROBLEM_SOLVING,
         "best practices for AI model deployment", no_mention_response),
        (AIEngine.CHATGPT, BusinessArea.DIGITAL_PUBLISHING, QueryCategory.SERVICE,
         "headless CMS implementation", no_mention_response),
        (AIEngine.PERPLEXITY, BusinessArea.DIGITAL_PUBLISHING, QueryCategory.PROBLEM_SOLVING,
         "modernizing legacy publishing systems", neutral_response.replace("AI", "publishing")),
        (AIEngine.CLAUDE, BusinessArea.DIGITAL_PUBLISHING, QueryCategory.INDUSTRY,
         "digital publishing for education", no_mention_response),
    ]

    # Create visibility analyzer
    analyzer = VisibilityAnalyzer(company_config)

    # Process each test case
    for engine, business_area, category, query, response_text in test_cases:
        # Create a mock engine response
        from src.engines.base import EngineResponse

        mock_response = EngineResponse(
            engine=engine,
            query=query,
            response_text=response_text,
            timestamp=datetime.now(),
            metadata={"demo": True},
            latency_ms=150.0,
        )

        # Analyze the response
        score = analyzer.analyze_response(mock_response, business_area, category)
        demo_scores.append(score)

    return demo_scores


async def main():
    """Run the demo assessment."""
    print("\n" + "="*80)
    print("DEMO: GEO VISIBILITY ASSESSMENT TOOL")
    print("Testing with simulated AI engine responses")
    print("="*80 + "\n")

    # Generate demo results
    print("Generating demo visibility scores...")
    demo_scores = await create_demo_results()

    print(f"✓ Created {len(demo_scores)} demo results\n")

    # Generate report
    print("Generating comprehensive report...\n")

    report_generator = ReportGenerator("First Line Software")
    report = report_generator.generate_report(
        visibility_scores=demo_scores,
        business_areas=[BusinessArea.GEN_AI, BusinessArea.DIGITAL_PUBLISHING],
        engines=[AIEngine.CHATGPT, AIEngine.PERPLEXITY, AIEngine.CLAUDE],
    )

    # Format and display report
    console_output = ConsoleFormatter.format_report(report)
    print(console_output)

    # Show some detailed results
    print("\n" + "="*80)
    print("DETAILED QUERY RESULTS (Sample)")
    print("="*80 + "\n")

    for i, score in enumerate(demo_scores[:5], 1):
        print(f"{i}. Query: {score.query[:60]}...")
        print(f"   Engine: {score.engine.value}")
        print(f"   Mentioned: {'YES' if score.is_mentioned else 'NO'}")
        if score.is_mentioned:
            print(f"   Prominence: {score.prominence_score:.2f}")
            print(f"   Context Quality: {score.context_quality:.2f}")
            print(f"   Sentiment: {score.sentiment}")
            if score.company_rank:
                print(f"   Rank: #{score.company_rank} of {score.total_companies_mentioned} companies")
        print()


if __name__ == "__main__":
    asyncio.run(main())
