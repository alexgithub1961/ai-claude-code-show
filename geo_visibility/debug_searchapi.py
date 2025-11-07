"""
Debug script to see what SearchAPI is actually returning.
"""
import asyncio
import httpx
import json


async def test_searchapi():
    """Test SearchAPI with various queries to see raw responses."""
    api_key = "dUngVqvqnKPAr1p1BKqKENJW"
    base_url = "https://www.searchapi.io/api/v1/search"

    test_queries = [
        "what is python programming",  # Very basic query
        "EPAM Systems company",  # Specific company
        "software development outsourcing",  # General service
    ]

    print("\n" + "="*80)
    print("SEARCHAPI DEBUG - RAW RESPONSES")
    print("="*80 + "\n")

    for query in test_queries:
        print(f"\n{'='*80}")
        print(f"Query: {query}")
        print(f"{'='*80}\n")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    base_url,
                    params={
                        "q": query,
                        "api_key": api_key,
                        "engine": "google",
                    },
                    timeout=30.0,
                )

                print(f"Status Code: {response.status_code}")

                if response.status_code == 200:
                    data = response.json()

                    print(f"\nTop-level keys in response:")
                    for key in data.keys():
                        print(f"  - {key}")

                    # Check for AI Overview
                    ai_overview = data.get("ai_overview")
                    print(f"\nai_overview present: {ai_overview is not None}")
                    if ai_overview:
                        print(f"ai_overview type: {type(ai_overview)}")
                        if isinstance(ai_overview, dict):
                            print(f"ai_overview keys: {list(ai_overview.keys())}")
                            if "text" in ai_overview:
                                print(f"ai_overview text length: {len(ai_overview['text'])} chars")

                    # Check for organic results
                    organic_results = data.get("organic_results", [])
                    print(f"\norganic_results count: {len(organic_results)}")
                    if organic_results:
                        print(f"First result title: {organic_results[0].get('title', 'N/A')}")

                    # Check for error
                    if "error" in data:
                        print(f"\nError in response: {data['error']}")

                    # Save full response to file for inspection
                    filename = f"searchapi_response_{query.replace(' ', '_')[:30]}.json"
                    with open(filename, 'w') as f:
                        json.dump(data, f, indent=2)
                    print(f"\nFull response saved to: {filename}")

                else:
                    print(f"Error: {response.text}")

        except Exception as e:
            print(f"Exception: {e}")
            import traceback
            traceback.print_exc()

        await asyncio.sleep(2)


if __name__ == "__main__":
    asyncio.run(test_searchapi())
