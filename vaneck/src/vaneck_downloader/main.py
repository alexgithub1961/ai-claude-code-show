"""Main CLI application for VanEck ETF downloader."""

import logging
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .config import Config
from .downloader import ETFDownloader
from .scraper import VanEckScraper
from .storage import StorageManager

console = Console()


def setup_logging(log_level: str, log_file: Optional[Path] = None) -> None:
    """Set up logging configuration."""
    # Configure root logger
    handlers = [RichHandler(console=console, rich_tracebacks=True)]
    
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        )
        handlers.append(file_handler)
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        handlers=handlers,
        format="%(message)s",
        datefmt="[%X]",
    )
    
    # Reduce noise from external libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("selenium").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)


@click.group()
@click.option(
    "--config-file",
    type=click.Path(exists=True, path_type=Path),
    help="Path to configuration file",
)
@click.option(
    "--download-dir",
    type=click.Path(path_type=Path),
    default="./download",
    help="Directory to store downloaded files",
)
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
    default="INFO",
    help="Logging level",
)
@click.option(
    "--log-file",
    type=click.Path(path_type=Path),
    help="Log file path",
)
@click.pass_context
def cli(
    ctx: click.Context,
    config_file: Optional[Path],
    download_dir: Path,
    log_level: str,
    log_file: Optional[Path],
) -> None:
    """VanEck ETF Data Downloader - Download ETF documents and data."""
    
    # Create config
    if config_file:
        # TODO: Load from config file if needed
        config = Config.from_env()
    else:
        config = Config.from_env()
    
    # Override with CLI parameters
    config.download_dir = download_dir
    config.log_level = log_level
    
    # Set up logging
    if log_file is None and config.download_dir:
        log_file = config.download_dir / "logs" / "vaneck_downloader.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
    
    setup_logging(log_level, log_file)
    
    # Store config in context
    ctx.ensure_object(dict)
    ctx.obj["config"] = config


@cli.command()
@click.option(
    "--use-selenium",
    is_flag=True,
    help="Force use of Selenium for scraping",
)
@click.option(
    "--output-file",
    type=click.Path(path_type=Path),
    help="Save fund list to JSON file",
)
@click.pass_context
def scrape(
    ctx: click.Context,
    use_selenium: bool,
    output_file: Optional[Path],
) -> None:
    """Scrape fund information from VanEck website."""
    config: Config = ctx.obj["config"]
    
    console.print("[bold blue]VanEck ETF Fund Scraper[/bold blue]")
    console.print(f"Target URL: {config.etf_finder_url}")
    
    storage = StorageManager(config)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        scrape_task = progress.add_task("Scraping fund information...", total=None)
        
        with VanEckScraper(config) as scraper:
            if use_selenium:
                console.print("Using Selenium for scraping...")
                funds = scraper.scrape_fund_list_selenium()
            else:
                console.print("Using static HTML parsing...")
                funds = scraper.scrape_all_funds()
        
        progress.update(scrape_task, completed=1, total=1)
    
    if not funds:
        console.print("[red]No funds found![/red]")
        sys.exit(1)
    
    # Display results
    table = Table(title=f"Found {len(funds)} ETF Funds")
    table.add_column("Symbol", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Documents", justify="right")
    table.add_column("Fact Sheet", justify="center")
    table.add_column("Holdings", justify="center")
    
    for fund in funds[:20]:  # Show first 20
        table.add_row(
            fund.symbol,
            fund.name[:50] + "..." if len(fund.name) > 50 else fund.name,
            str(len(fund.document_urls)),
            "✓" if fund.fact_sheet_url else "✗",
            "✓" if fund.holdings_url else "✗",
        )
    
    if len(funds) > 20:
        table.add_row("...", f"({len(funds) - 20} more funds)", "", "", "")
    
    console.print(table)
    
    # Save results
    for fund in funds:
        storage.save_fund_info(fund)
    
    storage.save_funds_summary(funds)
    
    if output_file:
        import json
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump([fund.dict() for fund in funds], f, indent=2, ensure_ascii=False)
        console.print(f"[green]Saved fund list to {output_file}[/green]")
    
    console.print(f"[green]Successfully scraped {len(funds)} funds[/green]")


@cli.command()
@click.option(
    "--fund-symbol",
    help="Download documents for specific fund only",
)
@click.option(
    "--use-async/--no-async",
    default=True,
    help="Use asynchronous downloads",
)
@click.option(
    "--max-concurrent",
    type=int,
    help="Maximum concurrent downloads",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be downloaded without actually downloading",
)
@click.pass_context
def download(
    ctx: click.Context,
    fund_symbol: Optional[str],
    use_async: bool,
    max_concurrent: Optional[int],
    dry_run: bool,
) -> None:
    """Download ETF documents."""
    config: Config = ctx.obj["config"]
    
    if max_concurrent:
        config.max_concurrent_downloads = max_concurrent
    
    console.print("[bold blue]VanEck ETF Document Downloader[/bold blue]")
    
    storage = StorageManager(config)
    
    # First scrape funds if needed
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        scrape_task = progress.add_task("Scraping fund information...", total=None)
        
        with VanEckScraper(config) as scraper:
            funds = scraper.scrape_all_funds()
        
        progress.update(scrape_task, completed=1, total=1)
    
    if not funds:
        console.print("[red]No funds found![/red]")
        sys.exit(1)
    
    # Filter by symbol if specified
    if fund_symbol:
        funds = [f for f in funds if f.symbol.upper() == fund_symbol.upper()]
        if not funds:
            console.print(f"[red]Fund {fund_symbol} not found![/red]")
            sys.exit(1)
    
    # Calculate total documents
    total_documents = sum(len(fund.document_urls) for fund in funds)
    
    if dry_run:
        console.print(f"[yellow]DRY RUN - Would download {total_documents} documents for {len(funds)} funds[/yellow]")
        
        for fund in funds:
            if fund.document_urls:
                console.print(f"  {fund.symbol}: {len(fund.document_urls)} documents")
        
        return
    
    console.print(f"Downloading {total_documents} documents for {len(funds)} funds...")
    console.print(f"Download directory: {config.download_dir}")
    console.print(f"Async mode: {use_async}")
    console.print(f"Max concurrent: {config.max_concurrent_downloads}")
    
    # Start downloads
    with ETFDownloader(config, storage) as downloader:
        stats = downloader.download_all_funds(funds, use_async=use_async)
    
    # Display results
    summary = stats.get_summary()
    
    results_table = Table(title="Download Results")
    results_table.add_column("Metric", style="cyan")
    results_table.add_column("Value", style="green")
    
    results_table.add_row("Total Files", str(summary["total_files"]))
    results_table.add_row("Downloaded", str(summary["downloaded"]))
    results_table.add_row("Skipped", str(summary["skipped"]))
    results_table.add_row("Failed", str(summary["failed"]))
    results_table.add_row("Total Size", f"{summary['total_mb']} MB")
    results_table.add_row("Time Elapsed", f"{summary['elapsed_seconds']} seconds")
    results_table.add_row("Download Rate", f"{summary['download_rate_mbps']} MB/s")
    results_table.add_row("Success Rate", f"{summary['success_rate']}%")
    
    console.print(results_table)
    
    if summary["errors"]:
        console.print("[red]Recent Errors:[/red]")
        for error in summary["errors"]:
            console.print(f"  • {error}")
    
    # Show storage stats
    storage_stats = storage.get_storage_stats()
    console.print(f"[green]Total storage used: {storage_stats['total_size_mb']} MB[/green]")


@cli.command()
@click.pass_context
def status(ctx: click.Context) -> None:
    """Show download status and statistics."""
    config: Config = ctx.obj["config"]
    
    console.print("[bold blue]VanEck ETF Downloader Status[/bold blue]")
    
    storage = StorageManager(config)
    
    # Load metadata
    metadata = storage.load_metadata()
    downloads = metadata.get("downloads", [])
    
    if not downloads:
        console.print("[yellow]No downloads recorded yet[/yellow]")
        return
    
    # Group by fund
    funds_data = {}
    for download in downloads:
        symbol = download["fund_symbol"]
        if symbol not in funds_data:
            funds_data[symbol] = {"count": 0, "size": 0, "types": set()}
        
        funds_data[symbol]["count"] += 1
        funds_data[symbol]["size"] += download["file_size"]
        if download.get("document_type"):
            funds_data[symbol]["types"].add(download["document_type"])
    
    # Create status table
    table = Table(title=f"Download Status ({len(funds_data)} funds)")
    table.add_column("Fund", style="cyan")
    table.add_column("Files", justify="right")
    table.add_column("Size (MB)", justify="right")
    table.add_column("Document Types")
    
    total_files = 0
    total_size = 0
    
    for symbol, data in sorted(funds_data.items()):
        total_files += data["count"]
        total_size += data["size"]
        
        table.add_row(
            symbol,
            str(data["count"]),
            f"{data['size'] / (1024 * 1024):.1f}",
            ", ".join(sorted(data["types"])) if data["types"] else "general",
        )
    
    console.print(table)
    
    # Summary
    console.print(f"[green]Total: {total_files} files, {total_size / (1024 * 1024):.1f} MB[/green]")
    
    # Storage stats
    storage_stats = storage.get_storage_stats()
    console.print(f"Storage directory: {storage_stats['download_dir']}")


@cli.command()
@click.option(
    "--confirm",
    is_flag=True,
    help="Confirm cleanup without prompting",
)
@click.pass_context
def cleanup(ctx: click.Context, confirm: bool) -> None:
    """Clean up partial downloads and temporary files."""
    config: Config = ctx.obj["config"]
    
    if not confirm:
        if not click.confirm("This will remove partial downloads. Continue?"):
            console.print("Cleanup cancelled.")
            return
    
    storage = StorageManager(config)
    storage.cleanup_partial_downloads()
    
    console.print("[green]Cleanup completed[/green]")


if __name__ == "__main__":
    cli()