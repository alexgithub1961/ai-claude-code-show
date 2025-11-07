"""
Test SearchAPI and simulated engine functionality.
"""
import asyncio
from src.engines import SearchAPIEngine, SimulatedAIEngine, EngineFactory
from src.config import AIEngine, EngineCredentials
import os
from dotenv import load_dotenv


async def test_searchapi():
    """Test SearchAPI integration for Chrome AI Summary."""
    print("\n" + "="*80)
    print("SEARCHAPI INTEGRATION TEST")
    print("="*80 + "\n")

    load_dotenv()

    api_key = os.getenv("SEARCHAPI_API_KEY")

    if not api_key:
        print("⚠️  SEARCHAPI_API_KEY not found in .env")
        print("   Get a free key from: https://www.searchapi.io/")
        print("   Skipping SearchAPI test\n")
        return

    engine = SearchAPIEngine(api_key=api_key)

    print(f"Engine configured: {engine.is_configured()}")
    print(f"Engine type: {engine.get_engine_type().value}\n")

    # Test query
    test_query = "best AI consulting companies 2024"
    print(f"Test Query: '{test_query}'\n")
    print("Querying Google AI Overview via SearchAPI...")

    try:
        response = await engine.query(test_query)

        print(f"\n✓ Response received")
        print(f"  Latency: {response.latency_ms:.0f}ms")
        print(f"  Has error: {response.error is not None}")

        if response.error:
            print(f"  Error: {response.error}")
        else:
            print(f"\n  Metadata:")
            for key, value in response.metadata.items():
                print(f"    {key}: {value}")

            print(f"\n  Response preview (first 300 chars):")
            print(f"  {response.response_text[:300]}...")

            # Check if First Line Software mentioned
            if "First Line" in response.response_text or "FLS" in response.response_text:
                print(f"\n  ✓ First Line Software mentioned!")
            else:
                print(f"\n  ✗ First Line Software not mentioned")

    except Exception as e:
        print(f"\n✗ Error: {e}")


async def test_simulated_engines():
    """Test simulated AI engines using GPT."""
    print("\n" + "="*80)
    print("SIMULATED ENGINE TEST")
    print("="*80 + "\n")

    load_dotenv()

    openai_key = os.getenv("OPENAI_API_KEY")

    if not openai_key:
        print("⚠️  OPENAI_API_KEY not found in .env")
        print("   Simulated engines require OpenAI API access")
        print("   Skipping simulation test\n")
        return

    # Test simulating different engines
    test_engines = [
        (AIEngine.CHROME_AI, "Google AI Overview"),
        (AIEngine.PERPLEXITY, "Perplexity"),
        (AIEngine.DEEPSEEK, "DeepSeek"),
    ]

    test_query = "managed AI services for enterprises"

    for target_engine, name in test_engines:
        print(f"\nSimulating {name} ({target_engine.value})")
        print("-" * 80)

        engine = SimulatedAIEngine(
            openai_api_key=openai_key,
            target_engine=target_engine
        )

        print(f"Engine configured: {engine.is_configured()}")
        print(f"Query: '{test_query}'")
        print("Generating simulated response...")

        try:
            response = await engine.query(test_query, max_tokens=300)

            print(f"\n✓ Response generated")
            print(f"  Latency: {response.latency_ms:.0f}ms")
            print(f"  Simulated: {response.metadata.get('simulated', False)}")
            print(f"  Model: {response.metadata.get('model', 'N/A')}")

            if response.error:
                print(f"  Error: {response.error}")
            else:
                print(f"\n  Response preview (first 250 chars):")
                print(f"  {response.response_text[:250]}...")

                # Check mentions
                if "First Line" in response.response_text:
                    print(f"\n  ✓ First Line Software mentioned!")
                else:
                    print(f"\n  ℹ First Line Software not mentioned (expected in simulation)")

        except Exception as e:
            print(f"\n✗ Error: {e}")


async def test_engine_factory():
    """Test engine factory with new capabilities."""
    print("\n" + "="*80)
    print("ENGINE FACTORY TEST")
    print("="*80 + "\n")

    load_dotenv()

    credentials = EngineCredentials(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        searchapi_api_key=os.getenv("SEARCHAPI_API_KEY"),
    )

    print("Testing Chrome AI engine creation...")
    print("-" * 80)

    # Test Chrome AI creation (should use SearchAPI if available, else simulate)
    try:
        chrome_ai = EngineFactory.create_engine(
            AIEngine.CHROME_AI,
            credentials
        )

        print(f"✓ Chrome AI engine created")
        print(f"  Type: {type(chrome_ai).__name__}")
        print(f"  Configured: {chrome_ai.is_configured()}")

        # Quick test
        response = await chrome_ai.query("AI consulting services", max_tokens=200)
        print(f"  Test query successful: {not response.error}")
        if response.metadata.get('simulated'):
            print(f"  Using: Simulation (GPT)")
        elif response.metadata.get('provider') == 'searchapi':
            print(f"  Using: SearchAPI (real AI Overview)")
        else:
            print(f"  Using: Mock")

    except Exception as e:
        print(f"✗ Error: {e}")

    print("\n" + "="*80)


async def main():
    """Run all tests."""
    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║        SearchAPI & Simulated Engine Integration Tests       ║")
    print("╚══════════════════════════════════════════════════════════════╝")

    await test_searchapi()
    await test_simulated_engines()
    await test_engine_factory()

    print("\n" + "="*80)
    print("TESTS COMPLETE")
    print("="*80 + "\n")

    print("Summary:")
    print("  • SearchAPI provides real Google AI Overview results")
    print("  • Simulated engines use GPT to approximate AI responses")
    print("  • Engine factory intelligently selects best available option")
    print("\nSee SEARCHAPI_GUIDE.md for more information\n")


if __name__ == "__main__":
    asyncio.run(main())
