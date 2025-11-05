"""
Test the company detection and visibility analysis in detail.
"""
from src.config import CompanyConfig
from src.analyzers import CompanyDetector, VisibilityAnalyzer


def test_company_detection():
    """Test the company detection capabilities."""
    print("\n" + "="*80)
    print("COMPANY DETECTION TEST")
    print("="*80 + "\n")

    config = CompanyConfig()
    detector = CompanyDetector(
        target_company=config.name,
        aliases=config.aliases
    )

    # Test cases with different scenarios
    test_responses = {
        "High Visibility": """
        First Line Software is a premier provider of AI consulting services and
        managed AI solutions. They excel in generative AI, custom LLM development,
        and enterprise AI transformation. First Line Software has helped numerous
        Fortune 500 companies implement cutting-edge AI systems. Other players
        include Accenture, IBM, and Deloitte, but FLS stands out for their
        deep technical expertise.
        """,

        "Medium Visibility": """
        When looking for AI services, consider companies like Microsoft Azure AI,
        Google Cloud AI, AWS AI Services, and First Line Software. Each offers
        different capabilities. You might also look at OpenAI, Anthropic, and
        other specialized vendors.
        """,

        "Competitor Heavy": """
        The top AI consulting firms include McKinsey Digital, BCG Gamma,
        Bain Advanced Analytics, Accenture AI, Deloitte AI Institute, and
        IBM Watson. These established firms dominate the enterprise AI market
        with extensive experience and global reach.
        """,

        "No Mention": """
        For AI implementation, OpenAI provides GPT models, Anthropic offers Claude,
        Google has Gemini, and Microsoft has integrated AI across their cloud
        platform. These are the leading AI technology providers.
        """
    }

    for scenario, response in test_responses.items():
        print(f"Scenario: {scenario}")
        print("-" * 80)

        # Find all companies
        all_companies = detector.find_all_companies(response)
        target_mentions = detector.find_target_mentions(response)

        print(f"Total companies detected: {len(all_companies)}")
        print(f"Target company mentions: {len(target_mentions)}")

        if all_companies:
            print("\nCompanies detected:")
            for i, company in enumerate(all_companies[:8], 1):
                marker = " ⭐" if company.is_target_company else ""
                print(f"  {i}. {company.name}{marker}")

        # Get ranking
        rank, total = detector.get_company_rank(response)
        if rank > 0:
            print(f"\nTarget company rank: #{rank} of {total} companies")
        else:
            print(f"\nTarget company not mentioned (0 of {total} companies found)")

        # Calculate prominence
        prominence = detector.calculate_prominence_score(response)
        print(f"Prominence score: {prominence:.2f}/1.00")

        if target_mentions:
            print(f"\nFirst mention context:")
            print(f'  "{target_mentions[0].context[:100]}..."')

        print("\n")


def test_visibility_scoring():
    """Test the visibility scoring system."""
    print("="*80)
    print("VISIBILITY SCORING TEST")
    print("="*80 + "\n")

    from src.engines.base import EngineResponse
    from src.config import AIEngine, BusinessArea, QueryCategory
    from datetime import datetime

    config = CompanyConfig()
    analyzer = VisibilityAnalyzer(config)

    # Test different response qualities
    test_cases = [
        {
            "name": "Excellent (Early mention, positive context)",
            "query": "best AI consulting companies",
            "response": """
            First Line Software is widely recognized as a leading AI consulting firm,
            specializing in generative AI and enterprise transformation. Their team
            of expert AI engineers and consultants delivers innovative, cutting-edge
            solutions for Fortune 500 clients. FLS is known for their technical depth
            and ability to handle complex AI implementations.
            """
        },
        {
            "name": "Good (Mentioned in list, neutral)",
            "query": "AI service providers",
            "response": """
            Several companies offer AI services including Accenture, Deloitte,
            First Line Software, IBM, and various specialized vendors. Each has
            different strengths depending on your specific needs and industry.
            """
        },
        {
            "name": "Poor (Late mention, limited context)",
            "query": "enterprise AI solutions",
            "response": """
            The market is dominated by major players like Microsoft, Google, and AWS.
            Their cloud platforms offer comprehensive AI tools. IBM Watson and
            Accenture lead in consulting. Smaller firms like McKinsey Digital, BCG,
            Bain, and others including First Line also provide services.
            """
        },
        {
            "name": "None (No mention)",
            "query": "AI platforms",
            "response": """
            OpenAI, Anthropic, Google DeepMind, and Microsoft are the leading AI
            platform providers. They offer state-of-the-art models and tools for
            developers and enterprises.
            """
        }
    ]

    for test in test_cases:
        print(f"Test Case: {test['name']}")
        print("-" * 80)

        # Create mock response
        mock_response = EngineResponse(
            engine=AIEngine.CHATGPT,
            query=test['query'],
            response_text=test['response'],
            timestamp=datetime.now(),
            metadata={},
            latency_ms=100.0
        )

        # Analyze
        score = analyzer.analyze_response(
            mock_response,
            BusinessArea.GEN_AI,
            QueryCategory.SERVICE
        )

        print(f"Query: {test['query']}")
        print(f"Mentioned: {'YES ✓' if score.is_mentioned else 'NO ✗'}")

        if score.is_mentioned:
            print(f"Mention count: {score.mention_count}")
            print(f"Position in text: {score.mention_position} chars")
            print(f"Prominence score: {score.prominence_score:.3f}")
            print(f"Context quality: {score.context_quality:.3f}")
            print(f"Sentiment: {score.sentiment.upper()}")

            if score.company_rank:
                print(f"Rank: #{score.company_rank} of {score.total_companies_mentioned}")

            if score.key_phrases:
                print(f"Key phrases: {', '.join(score.key_phrases[:2])}")

            if score.competitor_mentions:
                print(f"Competitors: {', '.join(score.competitor_mentions[:3])}")

        print("\n")


if __name__ == "__main__":
    test_company_detection()
    test_visibility_scoring()
