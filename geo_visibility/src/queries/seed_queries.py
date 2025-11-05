"""
Seed test queries for GEO visibility assessment.
Focuses on Gen AI/Managed AI Services and Digital Publishing/DX.
"""
from typing import Dict, List
from ..config import BusinessArea, QueryCategory, QuerySet


# Gen AI / Managed AI Services Queries
GEN_AI_QUERIES = {
    QueryCategory.DIRECT: [
        "First Line Software AI services",
        "What does First Line Software offer for AI development",
        "First Line Software managed AI solutions",
        "First Line Software generative AI capabilities",
        "First Line Software machine learning services",
    ],

    QueryCategory.SERVICE: [
        "managed AI services for enterprises",
        "AI consulting and implementation services",
        "generative AI development partners",
        "custom LLM implementation services",
        "AI model training and deployment services",
        "enterprise AI transformation consulting",
        "AI infrastructure management services",
        "conversational AI development companies",
        "AI-powered automation solutions",
        "end-to-end AI solution providers",
    ],

    QueryCategory.COMPARISON: [
        "best managed AI service providers",
        "top AI consulting companies 2024",
        "enterprise AI solutions comparison",
        "AI development partners for Fortune 500",
        "managed AI services vs in-house development",
        "leading AI transformation consultants",
    ],

    QueryCategory.PROBLEM_SOLVING: [
        "how to implement AI in enterprise workflows",
        "best practices for AI model deployment",
        "how to scale AI solutions in production",
        "integrating generative AI into existing systems",
        "managing AI infrastructure costs",
        "building secure AI applications",
        "AI governance and compliance solutions",
        "reducing AI implementation time and cost",
    ],

    QueryCategory.INDUSTRY: [
        "AI solutions for financial services",
        "healthcare AI implementation services",
        "retail AI transformation partners",
        "manufacturing AI automation",
        "AI for supply chain optimization",
        "AI in customer service and support",
        "AI-powered business intelligence",
    ],
}


# Digital Publishing / DX (Digital Experience) Queries
DIGITAL_PUBLISHING_QUERIES = {
    QueryCategory.DIRECT: [
        "First Line Software digital publishing solutions",
        "First Line Software DX platform",
        "First Line Software content management",
        "First Line Software digital experience services",
        "First Line Software publishing technology",
    ],

    QueryCategory.SERVICE: [
        "digital publishing platform development",
        "content management system development",
        "digital experience platform services",
        "headless CMS implementation",
        "omnichannel publishing solutions",
        "digital asset management services",
        "publishing workflow automation",
        "content delivery optimization",
        "digital magazine platform development",
        "e-book publishing technology solutions",
    ],

    QueryCategory.COMPARISON: [
        "best digital publishing platforms",
        "top DX platform developers",
        "enterprise content management solutions",
        "digital publishing software comparison",
        "headless CMS vs traditional CMS",
        "best publishing workflow tools",
    ],

    QueryCategory.PROBLEM_SOLVING: [
        "how to modernize legacy publishing systems",
        "migrating print publishing to digital",
        "scaling digital content delivery",
        "improving publishing workflow efficiency",
        "integrating multiple content sources",
        "personalizing digital reading experiences",
        "optimizing content for multiple devices",
        "reducing time-to-publish for digital content",
        "managing multi-format content publishing",
    ],

    QueryCategory.INDUSTRY: [
        "digital publishing for education",
        "enterprise publishing solutions",
        "academic journal publishing platforms",
        "corporate communications DX",
        "media and entertainment publishing tech",
        "B2B content publishing platforms",
        "government digital publishing solutions",
    ],
}


def get_seed_queries(business_area: BusinessArea) -> Dict[QueryCategory, List[str]]:
    """
    Get seed queries for a specific business area.

    Args:
        business_area: The business area to get queries for

    Returns:
        Dictionary mapping query categories to lists of queries
    """
    if business_area == BusinessArea.GEN_AI:
        return GEN_AI_QUERIES
    elif business_area == BusinessArea.DIGITAL_PUBLISHING:
        return DIGITAL_PUBLISHING_QUERIES
    else:
        raise ValueError(f"Unknown business area: {business_area}")


def get_all_query_sets() -> List[QuerySet]:
    """
    Get all seed query sets for all business areas.

    Returns:
        List of QuerySet objects
    """
    query_sets = []

    for business_area in [BusinessArea.GEN_AI, BusinessArea.DIGITAL_PUBLISHING]:
        queries_by_category = get_seed_queries(business_area)

        for category, queries in queries_by_category.items():
            query_set = QuerySet(
                business_area=business_area,
                category=category,
                queries=queries,
                metadata={
                    "version": "1.0",
                    "created": "2024",
                    "total_count": str(len(queries))
                }
            )
            query_sets.append(query_set)

    return query_sets


def count_total_queries() -> Dict[str, int]:
    """
    Count total queries by business area and category.

    Returns:
        Dictionary with query counts
    """
    counts = {
        "total": 0,
        "by_business_area": {},
        "by_category": {},
    }

    for query_set in get_all_query_sets():
        area_name = query_set.business_area.value
        category_name = query_set.category.value
        count = len(query_set.queries)

        counts["total"] += count
        counts["by_business_area"][area_name] = counts["by_business_area"].get(area_name, 0) + count
        counts["by_category"][category_name] = counts["by_category"].get(category_name, 0) + count

    return counts


if __name__ == "__main__":
    # Display query statistics
    print("GEO Visibility Assessment - Seed Queries\n")
    print("=" * 60)

    counts = count_total_queries()
    print(f"\nTotal Queries: {counts['total']}")

    print("\nBy Business Area:")
    for area, count in counts['by_business_area'].items():
        print(f"  {area}: {count}")

    print("\nBy Category:")
    for category, count in counts['by_category'].items():
        print(f"  {category}: {count}")

    print("\n" + "=" * 60)
    print("\nSample Queries:\n")

    for query_set in get_all_query_sets()[:2]:  # Show first 2 sets
        print(f"{query_set.business_area.value} - {query_set.category.value}:")
        for query in query_set.queries[:3]:  # Show first 3 queries
            print(f"  - {query}")
        print()
