"""
Company name detection and extraction from AI responses.
"""
import re
from typing import List, Tuple, Set
from dataclasses import dataclass


@dataclass
class CompanyMention:
    """A detected company mention."""
    name: str
    position: int  # Character position in text
    context: str  # Surrounding context
    is_target_company: bool = False


class CompanyDetector:
    """Detects company mentions in text."""

    def __init__(self, target_company: str = "First Line Software", aliases: List[str] = None):
        """
        Initialize the detector.

        Args:
            target_company: The company we're tracking
            aliases: Alternative names for the target company
        """
        self.target_company = target_company
        self.aliases = aliases or ["First Line", "FLS", "First Line Software Inc"]

        # Build regex pattern for target company
        all_names = [target_company] + self.aliases
        # Escape special regex characters
        escaped_names = [re.escape(name) for name in all_names]
        self.target_pattern = re.compile(
            r'\b(' + '|'.join(escaped_names) + r')\b',
            re.IGNORECASE
        )

        # Common company suffixes
        self.company_suffixes = [
            r'\b(Inc\.?|LLC|Ltd\.?|Corp\.?|Corporation|Company|Co\.?|LLP|LP)\b',
        ]

        # Pattern to detect company-like names
        # This is a simple heuristic - capitalized words potentially followed by suffix
        self.company_pattern = re.compile(
            r'\b([A-Z][a-z]*(?:\s+[A-Z][a-z]*){0,3}(?:\s+(?:Inc\.?|LLC|Ltd\.?|Corp\.?|Corporation|Company|Co\.?|LLP|LP))?)\b'
        )

    def find_target_mentions(self, text: str) -> List[CompanyMention]:
        """
        Find all mentions of the target company.

        Args:
            text: Text to search

        Returns:
            List of CompanyMention objects
        """
        mentions = []

        for match in self.target_pattern.finditer(text):
            # Get context around mention (50 chars before and after)
            start = max(0, match.start() - 50)
            end = min(len(text), match.end() + 50)
            context = text[start:end]

            mentions.append(CompanyMention(
                name=match.group(0),
                position=match.start(),
                context=context,
                is_target_company=True
            ))

        return mentions

    def find_all_companies(self, text: str) -> List[CompanyMention]:
        """
        Find all company mentions in text.

        Args:
            text: Text to search

        Returns:
            List of CompanyMention objects
        """
        mentions = []
        seen_positions = set()

        # First, find target company
        target_mentions = self.find_target_mentions(text)
        for mention in target_mentions:
            mentions.append(mention)
            seen_positions.add(mention.position)

        # Then find other companies
        for match in self.company_pattern.finditer(text):
            if match.start() in seen_positions:
                continue

            company_name = match.group(0).strip()

            # Filter out common false positives
            if self._is_likely_company(company_name):
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end]

                mentions.append(CompanyMention(
                    name=company_name,
                    position=match.start(),
                    context=context,
                    is_target_company=False
                ))
                seen_positions.add(match.start())

        # Sort by position
        mentions.sort(key=lambda m: m.position)

        return mentions

    def _is_likely_company(self, name: str) -> bool:
        """
        Determine if a name is likely a company.

        Args:
            name: Potential company name

        Returns:
            True if likely a company
        """
        # Filter out common false positives
        false_positives = {
            "The", "This", "That", "These", "Those", "Here", "There",
            "When", "Where", "What", "Which", "Who", "How", "Why",
            "Many", "Some", "All", "Each", "Every", "Any", "Few",
            "First", "Last", "Next", "Previous", "Other", "Another",
            "Digital", "Content", "Service", "Platform", "Solution",
            "AI", "ML", "API", "CMS", "DX",
        }

        # Must be at least 2 words or have a suffix
        words = name.split()
        if len(words) < 2:
            # Single word must have company suffix
            has_suffix = any(
                re.search(suffix, name, re.IGNORECASE)
                for suffix in self.company_suffixes
            )
            if not has_suffix:
                return False

        # Check if it's in false positives
        if name in false_positives or (len(words) == 1 and words[0] in false_positives):
            return False

        # Check for common software/tech terms that aren't companies
        tech_terms = {
            "Machine Learning", "Artificial Intelligence", "Deep Learning",
            "Natural Language", "Computer Vision", "Data Science",
        }
        if name in tech_terms:
            return False

        return True

    def get_company_rank(self, text: str, target_company: str = None) -> Tuple[int, int]:
        """
        Get the rank of the target company among all mentioned companies.

        Args:
            text: Text to analyze
            target_company: Company to rank (default: self.target_company)

        Returns:
            Tuple of (rank, total_companies)
            rank is 1-based (1 = first mentioned)
            Returns (0, total) if company not found
        """
        mentions = self.find_all_companies(text)

        if not mentions:
            return (0, 0)

        # Find first mention of target company
        for i, mention in enumerate(mentions):
            if mention.is_target_company:
                return (i + 1, len(mentions))

        return (0, len(mentions))

    def calculate_prominence_score(self, text: str) -> float:
        """
        Calculate a prominence score for the target company.

        Score is based on:
        - Position of first mention (earlier = better)
        - Total number of mentions
        - Context quality

        Args:
            text: Text to analyze

        Returns:
            Score from 0-1 (1 = most prominent)
        """
        mentions = self.find_target_mentions(text)

        if not mentions:
            return 0.0

        score = 0.0

        # Position score (first mention earlier = better)
        # If mentioned in first 20% of text, higher score
        first_position = mentions[0].position / len(text) if len(text) > 0 else 1.0
        position_score = max(0, 1.0 - first_position)
        score += position_score * 0.5

        # Frequency score
        mention_count = len(mentions)
        frequency_score = min(1.0, mention_count / 5)  # Cap at 5 mentions
        score += frequency_score * 0.3

        # Length/detail score - longer responses with mentions = better
        if len(mentions) > 0:
            avg_context_length = sum(len(m.context) for m in mentions) / len(mentions)
            detail_score = min(1.0, avg_context_length / 100)
            score += detail_score * 0.2

        return min(1.0, score)
