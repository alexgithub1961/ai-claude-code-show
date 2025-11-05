"""
Output formatters for visibility reports.
"""
import json
from typing import Dict, Any
from datetime import datetime
from tabulate import tabulate

from ..config import AssessmentReport, VisibilityScore


class ConsoleFormatter:
    """Format reports for console output."""

    @staticmethod
    def format_report(report: AssessmentReport) -> str:
        """Format a report for console display."""
        lines = []

        # Header
        lines.append("=" * 80)
        lines.append(f"GEO VISIBILITY ASSESSMENT REPORT".center(80))
        lines.append(f"{report.company}".center(80))
        lines.append("=" * 80)
        lines.append(f"\nGenerated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # Overall Score
        lines.append("OVERALL VISIBILITY SCORE")
        lines.append("-" * 80)
        score_bar = ConsoleFormatter._create_score_bar(report.overall_visibility_score)
        lines.append(f"{score_bar} {report.overall_visibility_score:.1f}/100")
        lines.append(f"Total Queries: {report.total_queries}")
        lines.append(f"Total Mentions: {report.total_mentions}")
        lines.append(f"Mention Rate: {(report.total_mentions/report.total_queries*100):.1f}%" if report.total_queries > 0 else "Mention Rate: 0%")
        lines.append("")

        # Engine Breakdown
        lines.append("VISIBILITY BY AI ENGINE")
        lines.append("-" * 80)
        engine_data = [
            [
                engine.value,
                f"{score:.1f}",
                ConsoleFormatter._create_score_bar(score, width=30)
            ]
            for engine, score in sorted(
                report.engine_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )
        ]
        lines.append(tabulate(
            engine_data,
            headers=["Engine", "Score", "Visual"],
            tablefmt="simple"
        ))
        lines.append("")

        # Business Area Breakdown
        lines.append("VISIBILITY BY BUSINESS AREA")
        lines.append("-" * 80)
        area_data = [
            [
                area.value.replace("_", " ").title(),
                f"{score:.1f}",
                ConsoleFormatter._create_score_bar(score, width=30)
            ]
            for area, score in sorted(
                report.business_area_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )
        ]
        lines.append(tabulate(
            area_data,
            headers=["Business Area", "Score", "Visual"],
            tablefmt="simple"
        ))
        lines.append("")

        # Strengths
        lines.append("KEY STRENGTHS")
        lines.append("-" * 80)
        for i, strength in enumerate(report.strengths, 1):
            lines.append(f"{i}. {strength}")
        lines.append("")

        # Weaknesses
        lines.append("AREAS FOR IMPROVEMENT")
        lines.append("-" * 80)
        for i, weakness in enumerate(report.weaknesses, 1):
            lines.append(f"{i}. {weakness}")
        lines.append("")

        # Recommendations
        lines.append("RECOMMENDATIONS")
        lines.append("-" * 80)
        for i, rec in enumerate(report.recommendations, 1):
            lines.append(f"{i}. {rec}")
        lines.append("")

        # Top Results
        lines.append("TOP 10 VISIBILITY SCORES")
        lines.append("-" * 80)
        top_results = sorted(
            report.results,
            key=lambda x: x.prominence_score,
            reverse=True
        )[:10]

        result_data = [
            [
                result.engine.value[:15],
                result.query[:40] + "..." if len(result.query) > 40 else result.query,
                "Yes" if result.is_mentioned else "No",
                f"{result.prominence_score:.2f}",
                result.sentiment[:3].upper(),
            ]
            for result in top_results
        ]
        lines.append(tabulate(
            result_data,
            headers=["Engine", "Query", "Mentioned", "Score", "Sentiment"],
            tablefmt="simple"
        ))

        lines.append("")
        lines.append("=" * 80)

        return "\n".join(lines)

    @staticmethod
    def _create_score_bar(score: float, width: int = 40) -> str:
        """Create a visual score bar."""
        filled = int((score / 100) * width)
        empty = width - filled

        # Color coding
        if score >= 70:
            symbol = "█"
        elif score >= 40:
            symbol = "▓"
        else:
            symbol = "░"

        return f"[{symbol * filled}{' ' * empty}]"


class MarkdownFormatter:
    """Format reports as Markdown."""

    @staticmethod
    def format_report(report: AssessmentReport) -> str:
        """Format a report as Markdown."""
        lines = []

        # Header
        lines.append(f"# GEO Visibility Assessment Report")
        lines.append(f"## {report.company}")
        lines.append(f"\n**Generated:** {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Overall Score
        lines.append(f"## Overall Visibility Score\n")
        lines.append(f"### **{report.overall_visibility_score:.1f}/100**\n")
        lines.append(f"- **Total Queries:** {report.total_queries}")
        lines.append(f"- **Total Mentions:** {report.total_mentions}")
        mention_rate = (report.total_mentions/report.total_queries*100) if report.total_queries > 0 else 0
        lines.append(f"- **Mention Rate:** {mention_rate:.1f}%\n")

        # Engine Breakdown
        lines.append(f"## Visibility by AI Engine\n")
        lines.append("| Engine | Score |")
        lines.append("|--------|-------|")
        for engine, score in sorted(report.engine_scores.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"| {engine.value} | {score:.1f} |")
        lines.append("")

        # Business Area Breakdown
        lines.append(f"## Visibility by Business Area\n")
        lines.append("| Business Area | Score |")
        lines.append("|---------------|-------|")
        for area, score in sorted(report.business_area_scores.items(), key=lambda x: x[1], reverse=True):
            area_name = area.value.replace("_", " ").title()
            lines.append(f"| {area_name} | {score:.1f} |")
        lines.append("")

        # Strengths
        lines.append(f"## Key Strengths\n")
        for i, strength in enumerate(report.strengths, 1):
            lines.append(f"{i}. {strength}")
        lines.append("")

        # Weaknesses
        lines.append(f"## Areas for Improvement\n")
        for i, weakness in enumerate(report.weaknesses, 1):
            lines.append(f"{i}. {weakness}")
        lines.append("")

        # Recommendations
        lines.append(f"## Recommendations\n")
        for i, rec in enumerate(report.recommendations, 1):
            lines.append(f"{i}. {rec}")
        lines.append("")

        return "\n".join(lines)


class JSONFormatter:
    """Format reports as JSON."""

    @staticmethod
    def format_report(report: AssessmentReport) -> str:
        """Format a report as JSON."""
        data = {
            "company": report.company,
            "generated_at": report.generated_at.isoformat(),
            "summary": {
                "overall_visibility_score": report.overall_visibility_score,
                "total_queries": report.total_queries,
                "total_mentions": report.total_mentions,
                "mention_rate": (report.total_mentions / report.total_queries * 100) if report.total_queries > 0 else 0,
            },
            "engine_scores": {
                engine.value: score
                for engine, score in report.engine_scores.items()
            },
            "business_area_scores": {
                area.value: score
                for area, score in report.business_area_scores.items()
            },
            "strengths": report.strengths,
            "weaknesses": report.weaknesses,
            "recommendations": report.recommendations,
            "detailed_results": [
                {
                    "engine": result.engine.value,
                    "query": result.query,
                    "business_area": result.business_area.value,
                    "category": result.query_category.value,
                    "is_mentioned": result.is_mentioned,
                    "prominence_score": result.prominence_score,
                    "context_quality": result.context_quality,
                    "sentiment": result.sentiment,
                    "company_rank": result.company_rank,
                    "total_companies_mentioned": result.total_companies_mentioned,
                    "competitor_mentions": result.competitor_mentions,
                }
                for result in report.results
            ]
        }

        return json.dumps(data, indent=2)
