"""
Query refinement and improvement functionality.
Uses AI to generate variations and improvements of seed queries.
"""
import asyncio
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
import re

from ..config import BusinessArea, QueryCategory, QuerySet


@dataclass
class QueryVariation:
    """A variation of a query."""
    original: str
    variation: str
    variation_type: str  # e.g., "synonym", "expansion", "specific", "general"
    confidence: float


class QueryRefiner:
    """
    Refines and improves test queries for better GEO visibility assessment.
    """

    def __init__(self):
        self.variation_strategies = {
            "synonym": self._generate_synonym_variations,
            "expansion": self._generate_expanded_variations,
            "specific": self._generate_specific_variations,
            "conversational": self._generate_conversational_variations,
            "question": self._generate_question_variations,
        }

    def refine_query_set(
        self,
        query_set: QuerySet,
        strategies: Optional[List[str]] = None
    ) -> List[str]:
        """
        Refine a query set using specified strategies.

        Args:
            query_set: QuerySet to refine
            strategies: List of strategy names to use (default: all)

        Returns:
            List of refined queries
        """
        if strategies is None:
            strategies = list(self.variation_strategies.keys())

        refined_queries: Set[str] = set(query_set.queries)

        for query in query_set.queries:
            for strategy in strategies:
                if strategy in self.variation_strategies:
                    variations = self.variation_strategies[strategy](
                        query,
                        query_set.business_area,
                        query_set.category
                    )
                    refined_queries.update(variations)

        return sorted(list(refined_queries))

    def _generate_synonym_variations(
        self,
        query: str,
        business_area: BusinessArea,
        category: QueryCategory
    ) -> List[str]:
        """Generate variations using synonyms."""
        variations = []

        # Domain-specific synonyms
        synonyms = {
            # Gen AI synonyms
            "AI": ["artificial intelligence", "machine learning", "ML"],
            "generative AI": ["gen AI", "GenAI", "generative artificial intelligence"],
            "LLM": ["large language model", "language model"],
            "managed": ["managed", "fully-managed", "turnkey"],
            "services": ["solutions", "offerings", "capabilities"],

            # Digital Publishing synonyms
            "digital publishing": ["digital content", "online publishing", "e-publishing"],
            "DX": ["digital experience", "digital transformation"],
            "CMS": ["content management system", "content platform"],
            "platform": ["solution", "system", "framework"],
        }

        query_lower = query.lower()
        for term, replacements in synonyms.items():
            if term.lower() in query_lower:
                for replacement in replacements:
                    # Simple replacement
                    variation = re.sub(
                        re.escape(term),
                        replacement,
                        query,
                        flags=re.IGNORECASE
                    )
                    if variation != query:
                        variations.append(variation)

        return variations[:3]  # Limit to top 3

    def _generate_expanded_variations(
        self,
        query: str,
        business_area: BusinessArea,
        category: QueryCategory
    ) -> List[str]:
        """Generate more detailed/expanded variations."""
        variations = []

        # Add context-specific expansions
        if business_area == BusinessArea.GEN_AI:
            expansions = [
                f"{query} for enterprises",
                f"{query} with custom integration",
                f"enterprise-grade {query}",
            ]
        elif business_area == BusinessArea.DIGITAL_PUBLISHING:
            expansions = [
                f"{query} for large publishers",
                f"scalable {query}",
                f"{query} with analytics",
            ]
        else:
            expansions = []

        # Only add if they make sense
        for exp in expansions:
            if not any(word in query.lower() for word in ["enterprise", "scalable", "custom"]):
                variations.append(exp)

        return variations[:2]

    def _generate_specific_variations(
        self,
        query: str,
        business_area: BusinessArea,
        category: QueryCategory
    ) -> List[str]:
        """Generate more specific variations."""
        variations = []

        # Add industry-specific variations
        if category == QueryCategory.SERVICE:
            industries = ["finance", "healthcare", "retail", "manufacturing"]
            variations.extend([f"{query} for {ind}" for ind in industries[:2]])

        # Add use-case specific variations
        if "implement" in query.lower() or "development" in query.lower():
            variations.append(f"{query} best practices")
            variations.append(f"{query} step by step")

        return variations[:2]

    def _generate_conversational_variations(
        self,
        query: str,
        business_area: BusinessArea,
        category: QueryCategory
    ) -> List[str]:
        """Generate conversational/natural language variations."""
        variations = []

        # Convert to conversational questions
        if not query.lower().startswith(("what", "how", "who", "where", "why", "which")):
            conversational_templates = [
                f"What are the best {query}",
                f"Who provides {query}",
                f"Where can I find {query}",
                f"How to choose {query}",
            ]

            # Pick most appropriate template
            if "service" in query.lower() or "solution" in query.lower():
                variations.append(conversational_templates[1])  # Who provides
            else:
                variations.append(conversational_templates[0])  # What are the best

        return variations

    def _generate_question_variations(
        self,
        query: str,
        business_area: BusinessArea,
        category: QueryCategory
    ) -> List[str]:
        """Generate question-based variations."""
        variations = []

        if category == QueryCategory.PROBLEM_SOLVING:
            if not query.lower().startswith("how"):
                variations.append(f"How to {query}")
                variations.append(f"What is the best way to {query}")

        elif category == QueryCategory.COMPARISON:
            if "best" not in query.lower():
                variations.append(f"What are the best {query}")
                variations.append(f"Which {query} should I choose")

        return variations[:1]

    def generate_improved_queries(
        self,
        business_area: BusinessArea,
        max_queries: int = 100
    ) -> Dict[QueryCategory, List[str]]:
        """
        Generate an improved set of queries for a business area.

        Args:
            business_area: Business area to generate queries for
            max_queries: Maximum queries per category

        Returns:
            Dictionary of improved queries by category
        """
        from .seed_queries import get_seed_queries

        seed_queries = get_seed_queries(business_area)
        improved_queries = {}

        for category, queries in seed_queries.items():
            query_set = QuerySet(
                business_area=business_area,
                category=category,
                queries=queries
            )

            refined = self.refine_query_set(query_set)
            improved_queries[category] = refined[:max_queries]

        return improved_queries

    def suggest_new_queries(
        self,
        business_area: BusinessArea,
        category: QueryCategory,
        count: int = 10
    ) -> List[str]:
        """
        Suggest new queries based on patterns and trends.

        Args:
            business_area: Business area
            category: Query category
            count: Number of suggestions to generate

        Returns:
            List of suggested queries
        """
        suggestions = []

        # Template-based suggestions
        templates = {}
        domains = []
        problems = []

        if business_area == BusinessArea.GEN_AI:
            templates = {
                QueryCategory.SERVICE: [
                    "AI-powered {domain} solutions",
                    "{domain} automation with AI",
                    "intelligent {domain} systems",
                ],
                QueryCategory.PROBLEM_SOLVING: [
                    "how to leverage AI for {problem}",
                    "AI solutions for {problem}",
                    "automating {problem} with machine learning",
                ],
                QueryCategory.COMPARISON: [
                    "best AI platforms for {domain}",
                    "comparing AI solutions for {domain}",
                ],
            }
            domains = ["analytics", "customer service", "operations", "decision making"]
            problems = ["data processing", "workflow optimization", "quality control"]

        elif business_area == BusinessArea.DIGITAL_PUBLISHING:
            templates = {
                QueryCategory.SERVICE: [
                    "{domain} publishing platform",
                    "digital {domain} management",
                    "modern {domain} solutions",
                ],
                QueryCategory.PROBLEM_SOLVING: [
                    "how to modernize {problem}",
                    "improving {problem} in publishing",
                    "optimizing {problem} workflow",
                ],
                QueryCategory.COMPARISON: [
                    "best {domain} publishing platforms",
                    "comparing {domain} CMS solutions",
                ],
            }
            domains = ["magazine", "book", "journal", "news"]
            problems = ["content distribution", "reader monetization", "engagement tracking"]

        # Generate from templates
        if category in templates:
            for template in templates[category][:3]:
                if "{domain}" in template:
                    suggestions.extend([template.format(domain=d) for d in domains[:2]])
                elif "{problem}" in template:
                    suggestions.extend([template.format(problem=p) for p in problems[:2]])

        return suggestions[:count]


if __name__ == "__main__":
    # Demo query refinement
    print("Query Refinement Demo\n")
    print("=" * 60)

    refiner = QueryRefiner()

    # Example refinement
    from .seed_queries import get_all_query_sets

    query_sets = get_all_query_sets()
    sample_set = query_sets[0]

    print(f"\nBusiness Area: {sample_set.business_area.value}")
    print(f"Category: {sample_set.category.value}")
    print(f"\nOriginal queries ({len(sample_set.queries)}):")
    for q in sample_set.queries[:3]:
        print(f"  - {q}")

    refined = refiner.refine_query_set(sample_set)
    print(f"\nRefined queries ({len(refined)}):")
    for q in refined[:5]:
        print(f"  - {q}")

    # Generate suggestions
    print(f"\n\nNew query suggestions:")
    suggestions = refiner.suggest_new_queries(
        sample_set.business_area,
        sample_set.category,
        count=5
    )
    for s in suggestions:
        print(f"  - {s}")
