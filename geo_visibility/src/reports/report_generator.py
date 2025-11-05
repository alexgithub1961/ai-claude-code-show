"""
Generate comprehensive GEO visibility reports.
"""
from typing import List, Dict, Optional
from datetime import datetime
from collections import defaultdict

from ..config import (
    AssessmentReport,
    VisibilityScore,
    AIEngine,
    BusinessArea,
    QueryCategory,
)


class ReportGenerator:
    """Generates visibility assessment reports."""

    def __init__(self, company_name: str = "First Line Software"):
        """
        Initialize report generator.

        Args:
            company_name: Name of the company
        """
        self.company_name = company_name

    def generate_report(
        self,
        visibility_scores: List[VisibilityScore],
        business_areas: List[BusinessArea],
        engines: List[AIEngine],
    ) -> AssessmentReport:
        """
        Generate a comprehensive assessment report.

        Args:
            visibility_scores: List of all visibility scores
            business_areas: Business areas tested
            engines: AI engines tested

        Returns:
            AssessmentReport object
        """
        # Calculate overall metrics
        total_queries = len(visibility_scores)
        total_mentions = sum(1 for score in visibility_scores if score.is_mentioned)

        # Calculate overall visibility score (0-100)
        if total_queries > 0:
            mention_rate = total_mentions / total_queries
            avg_prominence = sum(s.prominence_score for s in visibility_scores) / total_queries
            avg_context = sum(s.context_quality for s in visibility_scores) / total_queries

            # Weighted score
            overall_score = (
                mention_rate * 50 +  # 50% weight on mention rate
                avg_prominence * 30 +  # 30% weight on prominence
                avg_context * 20  # 20% weight on context quality
            )
        else:
            overall_score = 0.0

        # Calculate per-engine scores
        engine_scores = self._calculate_engine_scores(visibility_scores)

        # Calculate per-business area scores
        business_area_scores = self._calculate_business_area_scores(visibility_scores)

        # Generate insights
        strengths = self._identify_strengths(visibility_scores, engine_scores, business_area_scores)
        weaknesses = self._identify_weaknesses(visibility_scores, engine_scores, business_area_scores)
        recommendations = self._generate_recommendations(
            visibility_scores, engine_scores, business_area_scores, weaknesses
        )

        return AssessmentReport(
            company=self.company_name,
            generated_at=datetime.now(),
            business_areas=business_areas,
            engines_tested=engines,
            total_queries=total_queries,
            total_mentions=total_mentions,
            overall_visibility_score=overall_score,
            engine_scores=engine_scores,
            business_area_scores=business_area_scores,
            results=visibility_scores,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations,
        )

    def _calculate_engine_scores(
        self,
        scores: List[VisibilityScore]
    ) -> Dict[AIEngine, float]:
        """Calculate visibility score for each engine."""
        engine_groups = defaultdict(list)

        for score in scores:
            engine_groups[score.engine].append(score)

        engine_scores = {}
        for engine, engine_scores_list in engine_groups.items():
            if not engine_scores_list:
                engine_scores[engine] = 0.0
                continue

            total = len(engine_scores_list)
            mentions = sum(1 for s in engine_scores_list if s.is_mentioned)
            avg_prominence = sum(s.prominence_score for s in engine_scores_list) / total
            avg_context = sum(s.context_quality for s in engine_scores_list) / total

            score = (
                (mentions / total) * 50 +
                avg_prominence * 30 +
                avg_context * 20
            )
            engine_scores[engine] = score

        return engine_scores

    def _calculate_business_area_scores(
        self,
        scores: List[VisibilityScore]
    ) -> Dict[BusinessArea, float]:
        """Calculate visibility score for each business area."""
        area_groups = defaultdict(list)

        for score in scores:
            area_groups[score.business_area].append(score)

        area_scores = {}
        for area, area_scores_list in area_groups.items():
            if not area_scores_list:
                area_scores[area] = 0.0
                continue

            total = len(area_scores_list)
            mentions = sum(1 for s in area_scores_list if s.is_mentioned)
            avg_prominence = sum(s.prominence_score for s in area_scores_list) / total
            avg_context = sum(s.context_quality for s in area_scores_list) / total

            score = (
                (mentions / total) * 50 +
                avg_prominence * 30 +
                avg_context * 20
            )
            area_scores[area] = score

        return area_scores

    def _identify_strengths(
        self,
        scores: List[VisibilityScore],
        engine_scores: Dict[AIEngine, float],
        area_scores: Dict[BusinessArea, float]
    ) -> List[str]:
        """Identify strengths in visibility."""
        strengths = []

        # Best performing engines
        if engine_scores:
            best_engine = max(engine_scores.items(), key=lambda x: x[1])
            if best_engine[1] > 60:
                strengths.append(
                    f"Strong visibility on {best_engine[0].value} ({best_engine[1]:.1f}/100)"
                )

        # Best performing areas
        if area_scores:
            best_area = max(area_scores.items(), key=lambda x: x[1])
            if best_area[1] > 60:
                strengths.append(
                    f"Good visibility in {best_area[0].value.replace('_', ' ')} ({best_area[1]:.1f}/100)"
                )

        # High quality mentions
        high_quality = [s for s in scores if s.context_quality > 0.7]
        if len(high_quality) > len(scores) * 0.3:
            strengths.append(
                f"High quality context in {len(high_quality)} mentions ({len(high_quality)/len(scores)*100:.1f}%)"
            )

        # Positive sentiment
        positive = [s for s in scores if s.sentiment == "positive"]
        if len(positive) > len(scores) * 0.4:
            strengths.append(
                f"Predominantly positive sentiment ({len(positive)/len(scores)*100:.1f}%)"
            )

        return strengths if strengths else ["Limited visibility detected"]

    def _identify_weaknesses(
        self,
        scores: List[VisibilityScore],
        engine_scores: Dict[AIEngine, float],
        area_scores: Dict[BusinessArea, float]
    ) -> List[str]:
        """Identify weaknesses in visibility."""
        weaknesses = []

        # Poor performing engines
        for engine, score in engine_scores.items():
            if score < 30:
                weaknesses.append(
                    f"Low visibility on {engine.value} ({score:.1f}/100)"
                )

        # Poor performing areas
        for area, score in area_scores.items():
            if score < 30:
                weaknesses.append(
                    f"Limited visibility in {area.value.replace('_', ' ')} ({score:.1f}/100)"
                )

        # Low mention rate
        if scores:
            mention_rate = sum(1 for s in scores if s.is_mentioned) / len(scores)
            if mention_rate < 0.3:
                weaknesses.append(
                    f"Low mention rate across all queries ({mention_rate*100:.1f}%)"
                )

        # Poor rankings
        ranked_scores = [s for s in scores if s.company_rank]
        if ranked_scores:
            avg_rank = sum(s.company_rank for s in ranked_scores) / len(ranked_scores)
            if avg_rank > 3:
                weaknesses.append(
                    f"Average rank among competitors: {avg_rank:.1f} (lower is better)"
                )

        return weaknesses if weaknesses else ["No major weaknesses detected"]

    def _generate_recommendations(
        self,
        scores: List[VisibilityScore],
        engine_scores: Dict[AIEngine, float],
        area_scores: Dict[BusinessArea, float],
        weaknesses: List[str]
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        # Recommendations based on weaknesses
        for weakness in weaknesses:
            if "Low visibility on" in weakness:
                engine_name = weakness.split("Low visibility on ")[1].split(" ")[0]
                recommendations.append(
                    f"Optimize content and backlinks for {engine_name} indexing"
                )

            if "Limited visibility in" in weakness:
                area = weakness.split("Limited visibility in ")[1].split(" (")[0]
                recommendations.append(
                    f"Create more authoritative content about {area} capabilities"
                )

            if "Low mention rate" in weakness:
                recommendations.append(
                    "Increase brand awareness through thought leadership and PR"
                )
                recommendations.append(
                    "Publish more case studies and success stories"
                )

            if "Average rank" in weakness:
                recommendations.append(
                    "Improve SEO and content marketing to rank higher in AI search results"
                )
                recommendations.append(
                    "Build more high-quality backlinks from industry sources"
                )

        # General recommendations
        if not scores or sum(1 for s in scores if s.is_mentioned) / len(scores) < 0.5:
            recommendations.extend([
                "Develop comprehensive content strategy for GEO optimization",
                "Engage with AI platforms and ensure company information is accurate",
                "Create authoritative industry content and thought leadership pieces",
            ])

        # Query-specific recommendations
        service_queries = [s for s in scores if s.query_category == QueryCategory.SERVICE]
        if service_queries:
            mentioned_rate = sum(1 for s in service_queries if s.is_mentioned) / len(service_queries)
            if mentioned_rate < 0.4:
                recommendations.append(
                    "Improve service descriptions and use cases on website and third-party platforms"
                )

        return recommendations[:10]  # Limit to top 10
