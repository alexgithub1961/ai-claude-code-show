"""
Test the query refinement and suggestion capabilities.
"""
from src.queries import QueryRefiner, get_seed_queries
from src.config import BusinessArea, QueryCategory, QuerySet


def test_query_refinement():
    """Test query refinement variations."""
    print("\n" + "="*80)
    print("QUERY REFINEMENT TEST")
    print("="*80 + "\n")

    refiner = QueryRefiner()

    # Test original query
    original_query = "managed AI services for enterprises"

    print(f"Original Query: '{original_query}'")
    print("\nGenerated Variations:\n")

    # Create a query set
    query_set = QuerySet(
        business_area=BusinessArea.GEN_AI,
        category=QueryCategory.SERVICE,
        queries=[original_query]
    )

    # Generate refinements
    refined = refiner.refine_query_set(query_set)

    for i, variation in enumerate(refined, 1):
        if variation != original_query:
            print(f"  {i}. {variation}")

    print("\n")


def test_query_suggestions():
    """Test new query suggestions."""
    print("="*80)
    print("QUERY SUGGESTION TEST")
    print("="*80 + "\n")

    refiner = QueryRefiner()

    test_cases = [
        (BusinessArea.GEN_AI, QueryCategory.SERVICE),
        (BusinessArea.GEN_AI, QueryCategory.PROBLEM_SOLVING),
        (BusinessArea.DIGITAL_PUBLISHING, QueryCategory.SERVICE),
        (BusinessArea.DIGITAL_PUBLISHING, QueryCategory.COMPARISON),
    ]

    for business_area, category in test_cases:
        print(f"Area: {business_area.value}")
        print(f"Category: {category.value}")
        print("-" * 80)

        suggestions = refiner.suggest_new_queries(business_area, category, count=8)

        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion}")

        print("\n")


def test_full_refinement():
    """Test full query set refinement."""
    print("="*80)
    print("FULL QUERY SET REFINEMENT")
    print("="*80 + "\n")

    refiner = QueryRefiner()

    # Get seed queries for Gen AI
    seed_queries = get_seed_queries(BusinessArea.GEN_AI)

    print("Business Area: Gen AI / Managed AI Services")
    print(f"Categories: {len(seed_queries)}")
    print(f"Original total queries: {sum(len(queries) for queries in seed_queries.values())}\n")

    # Refine service queries
    service_queries = seed_queries[QueryCategory.SERVICE]

    print(f"Original SERVICE queries ({len(service_queries)}):")
    for i, q in enumerate(service_queries[:3], 1):
        print(f"  {i}. {q}")

    print("\nRefining queries...")

    query_set = QuerySet(
        business_area=BusinessArea.GEN_AI,
        category=QueryCategory.SERVICE,
        queries=service_queries[:3]  # Just refine first 3
    )

    refined = refiner.refine_query_set(query_set, strategies=["synonym", "conversational"])

    print(f"\nRefined queries ({len(refined)}):")
    for i, q in enumerate(refined, 1):
        print(f"  {i}. {q}")


if __name__ == "__main__":
    test_query_refinement()
    test_query_suggestions()
    test_full_refinement()
