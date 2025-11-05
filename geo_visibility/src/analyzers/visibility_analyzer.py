"""
Main visibility analyzer that processes engine responses.
"""
from typing import List, Dict, Optional
from datetime import datetime
import re

from ..config import (
    VisibilityScore,
    AIEngine,
    QueryCategory,
    BusinessArea,
    CompanyConfig,
)
from ..engines.base import EngineResponse
from .company_detector import CompanyDetector


class VisibilityAnalyzer:
    """Analyzes AI engine responses for company visibility."""

    def __init__(self, company_config: CompanyConfig):
        """
        Initialize the analyzer.

        Args:
            company_config: Configuration for the company being analyzed
        """
        self.company_config = company_config
        self.detector = CompanyDetector(
            target_company=company_config.name,
            aliases=company_config.aliases
        )

    def analyze_response(
        self,
        response: EngineResponse,
        business_area: BusinessArea,
        category: QueryCategory,
    ) -> VisibilityScore:
        """
        Analyze a single engine response.

        Args:
            response: The engine response
            business_area: Business area of the query
            category: Query category

        Returns:
            VisibilityScore object
        """
        # Find company mentions
        target_mentions = self.detector.find_target_mentions(response.response_text)
        all_companies = self.detector.find_all_companies(response.response_text)

        # Calculate metrics
        is_mentioned = len(target_mentions) > 0
        mention_count = len(target_mentions)
        mention_position = target_mentions[0].position if target_mentions else None

        # Get rank among companies
        rank, total_companies = self.detector.get_company_rank(response.response_text)

        # Calculate prominence score
        prominence_score = self.detector.calculate_prominence_score(response.response_text)

        # Analyze context quality
        context_quality = self._analyze_context_quality(target_mentions, response.response_text)

        # Detect sentiment
        sentiment = self._detect_sentiment(target_mentions)

        # Extract key phrases
        key_phrases = self._extract_key_phrases(target_mentions)

        # Find competitor mentions
        competitors = [
            company.name for company in all_companies
            if not company.is_target_company
        ]

        return VisibilityScore(
            engine=response.engine,
            query=response.query,
            query_category=category,
            business_area=business_area,
            timestamp=response.timestamp,
            is_mentioned=is_mentioned,
            mention_position=mention_position,
            mention_count=mention_count,
            prominence_score=prominence_score,
            context_quality=context_quality,
            response_text=response.response_text,
            total_companies_mentioned=len(all_companies),
            company_rank=rank if rank > 0 else None,
            sentiment=sentiment,
            key_phrases=key_phrases,
            competitor_mentions=competitors[:10],  # Limit to top 10
        )

    def _analyze_context_quality(
        self,
        mentions: List,
        full_text: str
    ) -> float:
        """
        Analyze the quality of context around mentions.

        Args:
            mentions: List of CompanyMention objects
            full_text: Full response text

        Returns:
            Quality score from 0-1
        """
        if not mentions:
            return 0.0

        quality_score = 0.0

        # Check for positive indicators in context
        positive_indicators = [
            r'\b(leading|top|best|premier|expert|specialist|innovative|advanced)\b',
            r'\b(provide|offer|deliver|specialize|focus)\b',
            r'\b(solution|service|platform|technology|expertise)\b',
            r'\b(enterprise|professional|comprehensive|custom)\b',
        ]

        for mention in mentions:
            context_lower = mention.context.lower()
            indicator_count = sum(
                1 for pattern in positive_indicators
                if re.search(pattern, context_lower, re.IGNORECASE)
            )
            quality_score += min(1.0, indicator_count / 4)

        return min(1.0, quality_score / len(mentions) if mentions else 0)

    def _detect_sentiment(self, mentions: List) -> str:
        """
        Detect sentiment around company mentions.

        Args:
            mentions: List of CompanyMention objects

        Returns:
            Sentiment: "positive", "neutral", "negative", or "unknown"
        """
        if not mentions:
            return "unknown"

        positive_words = [
            "excellent", "great", "best", "leading", "top", "innovative",
            "outstanding", "superior", "premier", "expert", "strong"
        ]

        negative_words = [
            "poor", "weak", "limited", "lacking", "inferior", "bad",
            "disappointing", "inadequate", "subpar"
        ]

        positive_count = 0
        negative_count = 0

        for mention in mentions:
            context_lower = mention.context.lower()
            positive_count += sum(1 for word in positive_words if word in context_lower)
            negative_count += sum(1 for word in negative_words if word in context_lower)

        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        elif positive_count > 0 or negative_count > 0:
            return "neutral"
        else:
            return "neutral"

    def _extract_key_phrases(self, mentions: List) -> List[str]:
        """
        Extract key phrases from mention contexts.

        Args:
            mentions: List of CompanyMention objects

        Returns:
            List of key phrases
        """
        if not mentions:
            return []

        key_phrases = set()

        # Common phrase patterns
        phrase_patterns = [
            r'(?:provides?|offers?|delivers?|specializes? in)\s+([^.,]+)',
            r'(?:known for|recognized for|leader in)\s+([^.,]+)',
            r'(?:expertise in|experience in|focus on)\s+([^.,]+)',
        ]

        for mention in mentions:
            for pattern in phrase_patterns:
                matches = re.finditer(pattern, mention.context, re.IGNORECASE)
                for match in matches:
                    phrase = match.group(1).strip()
                    if len(phrase) < 100:  # Reasonable length
                        key_phrases.add(phrase)

        return sorted(list(key_phrases))[:5]  # Return top 5

    def batch_analyze(
        self,
        responses: List[EngineResponse],
        business_area: BusinessArea,
        category: QueryCategory,
    ) -> List[VisibilityScore]:
        """
        Analyze multiple responses.

        Args:
            responses: List of engine responses
            business_area: Business area
            category: Query category

        Returns:
            List of VisibilityScore objects
        """
        return [
            self.analyze_response(response, business_area, category)
            for response in responses
        ]

    def calculate_aggregate_metrics(
        self,
        scores: List[VisibilityScore]
    ) -> Dict[str, float]:
        """
        Calculate aggregate metrics across multiple scores.

        Args:
            scores: List of visibility scores

        Returns:
            Dictionary of aggregate metrics
        """
        if not scores:
            return {
                "mention_rate": 0.0,
                "avg_prominence": 0.0,
                "avg_context_quality": 0.0,
                "avg_rank": 0.0,
                "positive_sentiment_rate": 0.0,
            }

        total = len(scores)
        mentioned = sum(1 for s in scores if s.is_mentioned)

        return {
            "mention_rate": mentioned / total if total > 0 else 0.0,
            "avg_prominence": sum(s.prominence_score for s in scores) / total,
            "avg_context_quality": sum(s.context_quality for s in scores) / total,
            "avg_rank": sum(
                s.company_rank for s in scores if s.company_rank
            ) / max(1, sum(1 for s in scores if s.company_rank)),
            "positive_sentiment_rate": sum(
                1 for s in scores if s.sentiment == "positive"
            ) / total if total > 0 else 0.0,
        }
