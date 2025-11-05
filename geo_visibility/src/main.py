"""
Main CLI for GEO Visibility Assessment Tool.
"""
import asyncio
import os
import sys
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import json

import click
from dotenv import load_dotenv
from tqdm import tqdm
import structlog

from .config import (
    CompanyConfig,
    BusinessArea,
    AIEngine,
    EngineCredentials,
    QueryCategory,
)
from .queries import get_all_query_sets, QueryRefiner
from .engines import EngineFactory
from .analyzers import VisibilityAnalyzer
from .reports import ReportGenerator, ConsoleFormatter, MarkdownFormatter, JSONFormatter


# Setup logging
logger = structlog.get_logger()


class GEOAssessment:
    """Main GEO visibility assessment orchestrator."""

    def __init__(
        self,
        company_config: CompanyConfig,
        credentials: EngineCredentials,
        output_dir: Path,
    ):
        """
        Initialize the assessment.

        Args:
            company_config: Company configuration
            credentials: API credentials for engines
            output_dir: Directory for output files
        """
        self.company_config = company_config
        self.credentials = credentials
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.analyzer = VisibilityAnalyzer(company_config)
        self.report_generator = ReportGenerator(company_config.name)

    async def run_assessment(
        self,
        engines: Optional[List[AIEngine]] = None,
        business_areas: Optional[List[BusinessArea]] = None,
        max_queries_per_category: int = 5,
        refine_queries: bool = True,
    ):
        """
        Run the complete GEO visibility assessment.

        Args:
            engines: List of engines to test (default: all configured)
            business_areas: Business areas to test (default: all)
            max_queries_per_category: Maximum queries per category
            refine_queries: Whether to use query refinement
        """
        logger.info("Starting GEO visibility assessment", company=self.company_config.name)

        # Setup
        if engines is None:
            engines = [AIEngine.CHATGPT, AIEngine.PERPLEXITY, AIEngine.CLAUDE]

        if business_areas is None:
            business_areas = self.company_config.business_areas

        # Create engines
        engine_instances = {}
        for engine_type in engines:
            try:
                engine = EngineFactory.create_engine(engine_type, self.credentials)
                if engine.is_configured():
                    engine_instances[engine_type] = engine
                    logger.info(f"Configured engine: {engine_type.value}")
                else:
                    logger.warning(f"Engine not configured: {engine_type.value}")
            except Exception as e:
                logger.error(f"Failed to create engine {engine_type.value}: {e}")

        if not engine_instances:
            logger.error("No engines configured. Please set up API keys.")
            return None

        # Get queries
        logger.info("Generating test queries...")
        all_queries = []

        for area in business_areas:
            from .queries.seed_queries import get_seed_queries

            queries_by_category = get_seed_queries(area)

            if refine_queries:
                refiner = QueryRefiner()

            for category, queries in queries_by_category.items():
                # Limit queries per category
                selected_queries = queries[:max_queries_per_category]

                # Optionally refine
                if refine_queries:
                    from .queries.seed_queries import QuerySet
                    query_set = QuerySet(
                        business_area=area,
                        category=category,
                        queries=selected_queries
                    )
                    selected_queries = refiner.refine_query_set(query_set)[:max_queries_per_category]

                for query in selected_queries:
                    all_queries.append((area, category, query))

        logger.info(f"Total queries to test: {len(all_queries)}")

        # Run queries across all engines
        all_scores = []
        total_ops = len(all_queries) * len(engine_instances)

        with tqdm(total=total_ops, desc="Running queries") as pbar:
            for area, category, query in all_queries:
                for engine_type, engine in engine_instances.items():
                    try:
                        # Query the engine
                        response = await engine.query(query)

                        # Analyze response
                        score = self.analyzer.analyze_response(response, area, category)
                        all_scores.append(score)

                        pbar.set_postfix({
                            "engine": engine_type.value[:10],
                            "mentions": sum(1 for s in all_scores if s.is_mentioned),
                        })

                    except Exception as e:
                        logger.error(f"Error querying {engine_type.value}: {e}")

                    finally:
                        pbar.update(1)

                    # Rate limiting
                    await asyncio.sleep(0.5)

        # Generate report
        logger.info("Generating report...")
        report = self.report_generator.generate_report(
            visibility_scores=all_scores,
            business_areas=business_areas,
            engines=list(engine_instances.keys()),
        )

        # Save report
        self._save_report(report)

        logger.info("Assessment complete!")
        return report

    def _save_report(self, report):
        """Save report in multiple formats."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Console format
        console_output = ConsoleFormatter.format_report(report)
        console_path = self.output_dir / f"report_{timestamp}.txt"
        console_path.write_text(console_output)
        logger.info(f"Saved console report: {console_path}")

        # Markdown format
        markdown_output = MarkdownFormatter.format_report(report)
        markdown_path = self.output_dir / f"report_{timestamp}.md"
        markdown_path.write_text(markdown_output)
        logger.info(f"Saved markdown report: {markdown_path}")

        # JSON format
        json_output = JSONFormatter.format_report(report)
        json_path = self.output_dir / f"report_{timestamp}.json"
        json_path.write_text(json_output)
        logger.info(f"Saved JSON report: {json_path}")

        # Print to console
        print("\n" + console_output)


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """GEO Visibility Assessment Tool for First Line Software."""
    pass


@cli.command()
@click.option("--engines", "-e", multiple=True, help="AI engines to test (chatgpt, perplexity, claude, etc.)")
@click.option("--business-areas", "-b", multiple=True, help="Business areas to test (gen_ai, digital_publishing)")
@click.option("--max-queries", "-m", default=5, help="Maximum queries per category")
@click.option("--refine/--no-refine", default=True, help="Use query refinement")
@click.option("--output-dir", "-o", default="reports", help="Output directory for reports")
def assess(engines, business_areas, max_queries, refine, output_dir):
    """Run GEO visibility assessment."""
    # Load environment variables
    load_dotenv()

    # Setup credentials
    credentials = EngineCredentials(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        perplexity_api_key=os.getenv("PERPLEXITY_API_KEY"),
        deepseek_api_key=os.getenv("DEEPSEEK_API_KEY"),
        grok_api_key=os.getenv("GROK_API_KEY"),
    )

    # Setup company config
    company_config = CompanyConfig()

    # Parse engines
    if engines:
        engine_list = [AIEngine(e) for e in engines]
    else:
        engine_list = None

    # Parse business areas
    if business_areas:
        area_list = [BusinessArea(a) for a in business_areas]
    else:
        area_list = None

    # Create assessment
    assessment = GEOAssessment(
        company_config=company_config,
        credentials=credentials,
        output_dir=Path(output_dir),
    )

    # Run
    asyncio.run(assessment.run_assessment(
        engines=engine_list,
        business_areas=area_list,
        max_queries_per_category=max_queries,
        refine_queries=refine,
    ))


@cli.command()
def list_queries():
    """List all seed queries."""
    from .queries.seed_queries import get_all_query_sets, count_total_queries

    counts = count_total_queries()

    print("\nGEO Visibility Assessment - Seed Queries\n")
    print("=" * 80)
    print(f"\nTotal Queries: {counts['total']}")

    print("\nBy Business Area:")
    for area, count in counts['by_business_area'].items():
        print(f"  {area}: {count}")

    print("\nBy Category:")
    for category, count in counts['by_category'].items():
        print(f"  {category}: {count}")

    print("\n" + "=" * 80)

    # Show sample queries
    query_sets = get_all_query_sets()
    for query_set in query_sets[:2]:
        print(f"\n{query_set.business_area.value} - {query_set.category.value}:")
        for query in query_set.queries[:5]:
            print(f"  • {query}")


@cli.command()
@click.argument("business_area", type=click.Choice(["gen_ai", "digital_publishing"]))
@click.option("--count", "-c", default=10, help="Number of suggestions")
def suggest_queries(business_area, count):
    """Generate query suggestions."""
    from .queries import QueryRefiner

    # Map CLI argument to enum
    area_map = {
        "gen_ai": BusinessArea.GEN_AI,
        "digital_publishing": BusinessArea.DIGITAL_PUBLISHING,
    }
    area = area_map[business_area]
    refiner = QueryRefiner()

    print(f"\nQuery Suggestions for {area.value}\n")
    print("=" * 80)

    for category in QueryCategory:
        print(f"\n{category.value.upper()}:")
        suggestions = refiner.suggest_new_queries(area, category, count=count)
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion}")


@cli.command()
@click.option("--create", is_flag=True, help="Create a template .env file")
def config(create):
    """Manage configuration."""
    if create:
        env_template = """# GEO Visibility Assessment - API Keys

# OpenAI (ChatGPT)
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic (Claude)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Perplexity
PERPLEXITY_API_KEY=your_perplexity_api_key_here

# DeepSeek
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Grok (xAI)
GROK_API_KEY=your_grok_api_key_here
"""
        Path(".env").write_text(env_template)
        print("Created .env template. Please add your API keys.")
    else:
        print("Use --create to generate a .env template")


if __name__ == "__main__":
    cli()
