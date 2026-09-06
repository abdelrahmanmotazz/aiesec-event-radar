"""CLI Runner for Autonomous Facebook Events Extraction using Playwright."""

import argparse
import json
import logging
import sys
from rich.console import Console
from rich.table import Table

from aiesec_scraper.scrapers.meta_playwright import MetaPlaywrightScraper
from aiesec_scraper.exporters import LocalExporter

console = Console()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def main():
    parser = argparse.ArgumentParser(description="Autonomous Facebook Events Scraper")
    parser.add_argument("--city", type=str, default=None, help="Filter by city (e.g. cairo, alexandria, tanta)")
    parser.add_argument("--max", type=int, default=30, help="Maximum events to extract")
    parser.add_argument("--save", action="store_true", help="Save extracted events to local files")
    args = parser.parse_args()

    console.print(f"[bold cyan]Launching Autonomous Facebook Events Harvester (City={args.city or 'All Egypt'})...[/bold cyan]")
    scraper = MetaPlaywrightScraper()
    events = scraper.scrape(city=args.city, max_events=args.max)

    console.print(f"[bold green]Successfully extracted {len(events)} events from Facebook![/bold green]\n")

    if events:
        table = Table(title="Extracted Facebook Events")
        table.add_column("Title", style="white bold")
        table.add_column("City", style="cyan")
        table.add_column("Date", style="yellow")
        table.add_column("Score", style="magenta")
        table.add_column("URL", style="blue")

        for ev in events[:15]:
            table.add_row(ev.title[:35], ev.city, ev.date_display[:20], f"{ev.b2c_score:.1f}", ev.url[:40])
        console.print(table)

        if args.save:
            exporter = LocalExporter()
            exporter.export(events)
            console.print("[bold green]Events exported to local data and static files.[/bold green]")

if __name__ == "__main__":
    main()
