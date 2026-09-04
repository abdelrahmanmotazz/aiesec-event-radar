"""Command-Line Interface for the AIESEC Egypt B2C Event Scraper & Command Center."""

import argparse
import logging
import os
import socket
import sys
import yaml
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .pipeline import EventPipeline
from .exporters import GoogleSheetsExporter, LocalExporter
from .scheduler import ScraperScheduler
from .notifications import EmailNotificationService

# Ensure safe UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

console = Console(safe_box=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from yaml file if available."""
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            console.print(f"[yellow]Warning: Could not parse {config_path}: {e}. Using defaults.[/yellow]")
    return {}


def handle_run(args):
    """Execute on-demand scraping run."""
    config = load_config(args.config)
    if args.months:
        config["date_window_months"] = args.months

    target_display = f"City: {args.city.capitalize()}" if args.city else f"Country: {args.country.capitalize()} (Nationwide)"
    console.print(Panel(
        f"[bold cyan]AIESEC Egypt B2C Event Radar[/bold cyan]\n"
        f"Target Scope: [bold yellow]{target_display}[/bold yellow]\n"
        f"Date Window: [green]Next {config.get('date_window_months', 6)} Months[/green]\n"
        f"Platforms: [magenta]Eventbrite, AllEvents.in, Meetup, 10times, Social Media[/magenta]",
        title="Starting Scrape Run",
        expand=False
    ))

    pipeline = EventPipeline(config)
    events = pipeline.run(city=args.city, country=args.country)

    if not events:
        console.print("[yellow]No upcoming events found matching the criteria.[/yellow]")
        return

    # 1. Export locally (always generated first)
    local_exporter = LocalExporter(output_dir=config.get("output", {}).get("output_dir", "data"))
    export_paths = local_exporter.export(events)
    console.print(f"\n[bold green]✓ Local Exports Saved:[/bold green]")
    console.print(f"  • Excel (.xlsx): [cyan]{export_paths['excel_latest']}[/cyan]")
    console.print(f"  • CSV:          [cyan]{export_paths['csv_latest']}[/cyan]")

    # 2. Sync to Google Sheets
    sheets_exporter = GoogleSheetsExporter(
        service_account_file=config.get("output", {}).get("google_sheets", {}).get("service_account_file", "service_account.json"),
        sheet_name=config.get("output", {}).get("google_sheets", {}).get("sheet_name", "AIESEC Egypt B2C Event Radar")
    )
    sheets_res = sheets_exporter.sync(events)
    if sheets_res.get("success"):
        console.print(f"\n[bold green]✓ Google Sheets Synced Successfully![/bold green]")
        console.print(f"  • Spreadsheet URL: [link={sheets_res['sheet_url']}]{sheets_res['sheet_url']}[/link]")
        console.print(f"  • Records Synced: [bold]{sheets_res['records_synced']}[/bold]")
    else:
        console.print(f"\n[yellow]Google Sheets Notice:[/yellow] {sheets_res.get('message')}")

    # 3. Print summary table in terminal
    try:
        table = Table(title=f"Top Upcoming Events (Total Found: {len(events)})", show_lines=True)
        table.add_column("Score", justify="center", style="bold green", width=7)
        table.add_column("Priority", justify="center", width=8)
        table.add_column("Event Title", style="cyan", width=32)
        table.add_column("Date", width=18)
        table.add_column("City", width=12)
        table.add_column("Partner Org", width=12)
        table.add_column("Recommended B2C Action", style="italic yellow", width=30)

        for ev in events[:15]:
            priority_color = "red" if ev.b2c_priority == "HIGH" else ("yellow" if ev.b2c_priority == "MEDIUM" else "white")
            safe_title = ev.title.encode("ascii", "ignore").decode("ascii") if not ev.title.isascii() else ev.title
            if not safe_title.strip():
                safe_title = ev.title[:30]
            safe_action = ev.recommended_action.encode("ascii", "ignore").decode("ascii")

            table.add_row(
                f"{ev.b2c_score:.1f}",
                f"[{priority_color}]{ev.b2c_priority}[/{priority_color}]",
                safe_title[:30] + ("..." if len(safe_title) > 30 else ""),
                ev.date_display[:16],
                ev.city,
                ev.parallel_org or "General",
                safe_action[:28] + ("..." if len(safe_action) > 28 else "")
            )

        console.print(table)
        if len(events) > 15:
            console.print(f"[dim]... and {len(events) - 15} more events in export files.[/dim]")
    except Exception as table_err:
        console.print(f"[dim](Table display skipped: {table_err})[/dim]")


def handle_schedule(args):
    """Run recurring scheduler."""
    config = load_config(args.config)
    scheduler = ScraperScheduler(config)
    interval = args.interval_days or config.get("schedule_interval_days", 3)
    console.print(f"[bold cyan]Starting AIESEC Event Scraper Scheduler (Interval: {interval} days)...[/bold cyan]")
    scheduler.run_loop(interval_days=interval, city=args.city, country=args.country)


def handle_notify(args):
    """Dispatch email digest on demand."""
    config = load_config(args.config)
    pipeline = EventPipeline(config)
    events = pipeline.run(city=args.city, country=args.country)
    email_service = EmailNotificationService(config)

    recipients = [r.strip() for r in args.to.split(",")] if args.to else None
    res = email_service.send_digest(events, recipients=recipients)

    if res.get("success"):
        console.print(f"[bold green]✓ Email alert sent successfully to {res.get('recipients')}![/bold green]")
    else:
        console.print(f"[yellow]Email Notice:[/yellow] {res.get('message')}")


def handle_dashboard(args):
    """Start the FastAPI interactive dashboard server."""
    import uvicorn
    from .web.app import app

    config = load_config(args.config)
    host = args.host or config.get("web", {}).get("host", "0.0.0.0")
    port = args.port or config.get("web", {}).get("port", 8000)

    # Get local LAN IP address so members on the same network can access
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        local_ip = "127.0.0.1"

    console.print(Panel(
        f"[bold cyan]AIESEC Egypt B2C Event Radar & Command Center[/bold cyan]\n\n"
        f"• Local Access: [bold green]http://localhost:{port}[/bold green]\n"
        f"• Network Access (Same Wi-Fi): [bold green]http://{local_ip}:{port}[/bold green]\n\n"
        f"[bold white]To share with ANYONE across the internet (Public URL):[/bold white]\n"
        f"Run this in a second terminal:\n"
        f"[cyan]npx cloudflared tunnel --url http://localhost:{port}[/cyan]\n"
        f"Or with ngrok:\n"
        f"[cyan]ngrok http {port}[/cyan]",
        title="Web Dashboard Started",
        expand=False
    ))

    uvicorn.run(app, host=host, port=port)


def handle_setup_task(args):
    """Generate Windows Task Runner script."""
    script_path = ScraperScheduler.generate_windows_task_script()
    console.print(Panel(
        f"[bold green]Windows Task Runner Created![/bold green]\n\n"
        f"Script Location: [cyan]{script_path}[/cyan]\n\n"
        f"To schedule this to run automatically every 3 days in Windows:\n"
        f"1. Press [bold]Win + R[/bold], type [cyan]taskschd.msc[/cyan] and press Enter.\n"
        f"2. Click [bold]'Create Basic Task...'[/bold] on the right pane.\n"
        f"3. Name it [bold]'AIESEC Event Radar Scraper'[/bold].\n"
        f"4. Trigger: Choose [bold]'Daily'[/bold], recur every [bold]3 days[/bold].\n"
        f"5. Action: [bold]'Start a program'[/bold] -> select [cyan]{script_path}[/cyan].\n"
        f"6. Click Finish! Your Google Sheet and local Excel files will refresh every 3 days automatically.",
        title="Windows Scheduled Task Setup"
    ))


def main():
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="AIESEC Egypt B2C Event Scraper, Dashboard & Outreach Engine",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: run
    run_parser = subparsers.add_parser("run", help="Run on-demand event scrape")
    run_parser.add_argument("--city", type=str, default=None, help="Target Egyptian city (e.g. cairo, alexandria). If omitted, scrapes nationwide.")
    run_parser.add_argument("--country", type=str, default="egypt", help="Target country")
    run_parser.add_argument("--months", type=int, default=6, help="Date window in months (default 6 months)")
    run_parser.add_argument("--config", type=str, default="config.yaml", help="Path to config.yaml")

    # Command: dashboard
    dash_parser = subparsers.add_parser("dashboard", help="Start the interactive web UI dashboard")
    dash_parser.add_argument("--host", type=str, default="0.0.0.0", help="Host address")
    dash_parser.add_argument("--port", type=int, default=8000, help="Port number")
    dash_parser.add_argument("--config", type=str, default="config.yaml", help="Path to config.yaml")

    # Command: notify
    notify_parser = subparsers.add_parser("notify", help="Send AIESEC email digest alert")
    notify_parser.add_argument("--to", type=str, default=None, help="Comma-separated recipient emails")
    notify_parser.add_argument("--city", type=str, default=None, help="Target city")
    notify_parser.add_argument("--country", type=str, default="egypt", help="Target country")
    notify_parser.add_argument("--config", type=str, default="config.yaml", help="Path to config.yaml")

    # Command: schedule
    sched_parser = subparsers.add_parser("schedule", help="Start recurring background scraper")
    sched_parser.add_argument("--interval-days", type=int, default=3, help="Interval between runs in days (default: 3)")
    sched_parser.add_argument("--city", type=str, default=None, help="Target city")
    sched_parser.add_argument("--country", type=str, default="egypt", help="Target country")
    sched_parser.add_argument("--config", type=str, default="config.yaml", help="Path to config.yaml")

    # Command: setup-task
    subparsers.add_parser("setup-task", help="Generate Windows Task Scheduler runner script")

    args = parser.parse_args()

    if args.command == "run":
        handle_run(args)
    elif args.command == "dashboard":
        handle_dashboard(args)
    elif args.command == "notify":
        handle_notify(args)
    elif args.command == "schedule":
        handle_schedule(args)
    elif args.command == "setup-task":
        handle_setup_task(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
