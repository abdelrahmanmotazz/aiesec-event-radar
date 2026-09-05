"""FastAPI Web Server for AIESEC Egypt B2C Event Radar & Command Center."""

import os
from typing import Dict, List, Optional
import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from ..models import EventRecord
from ..pipeline import EventPipeline
from ..exporters import GoogleSheetsExporter, LocalExporter
from ..notifications import EmailNotificationService
from ..analyzers.pitch_generator import PitchGenerator

app = FastAPI(title="AIESEC Egypt B2C Event Radar", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory cached events
CACHED_EVENTS: List[EventRecord] = []
PIPELINE = EventPipeline()
LOCAL_EXPORTER = LocalExporter()
SHEETS_EXPORTER = GoogleSheetsExporter()
EMAIL_SERVICE = EmailNotificationService()

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def load_initial_events():
    """Load latest events from local Excel if available, and ensure summits & TicketsMarche are seeded."""
    global CACHED_EVENTS
    latest_xlsx = "data/aiesec_egypt_events_latest.xlsx"
    events = []
    if os.path.exists(latest_xlsx):
        try:
            import pandas as pd
            df = pd.read_excel(latest_xlsx)
            for idx, row in df.iterrows():
                rec = EventRecord(
                    event_id=f"rec_{idx}",
                    title=str(row.get("Event Title", "")),
                    source=str(row.get("Platform", "Eventbrite")),
                    date_display=str(row.get("Date & Time", "")),
                    location=str(row.get("Venue / Location", "TBA")),
                    city=str(row.get("City", "Egypt")),
                    country="Egypt",
                    url=str(row.get("Event Link", "#")),
                    ticket_type=str(row.get("Pricing / Ticket", "Unknown")),
                    organizer=str(row.get("Organizer", "Unknown")),
                    category=str(row.get("Primary Category", "General")),
                    parallel_org=str(row.get("Student Org / Partner")) if str(row.get("Student Org / Partner")) not in ["Independent", "nan", "None"] else None,
                    b2c_score=float(row.get("B2C Score (1-10)", 5.0)),
                    b2c_priority=str(row.get("AIESEC Priority", "LOW")),
                    clash_warning="Clash" in str(row.get("Clash Status", "")),
                    recommended_action=str(row.get("Recommended B2C Action", "General Monitoring"))
                )
                events.append(rec)
        except Exception:
            pass

    # Ensure flagship summits (Techne Summit, RiseUp, etc.) are present
    existing_titles = {e.title.lower() for e in events}
    if not any("techne" in t for t in existing_titles):
        try:
            from ..scrapers import EgyptSummitsScraper
            summit_events = EgyptSummitsScraper().scrape(city=None)
            from ..scorers import B2CScorer
            scorer = B2CScorer()
            for ev in summit_events:
                score, priority, category, tags, action, parallel = scorer.evaluate(ev.title, ev.description, ev.location)
                ev.b2c_score = score
                ev.b2c_priority = priority
                ev.category = category
                ev.aiesec_tags = tags
                ev.recommended_action = action
                ev.parallel_org = parallel
                events.insert(0, ev)
        except Exception as e:
            logger.error(f"Error seeding summits: {e}")

    # Ensure TicketsMarche events are present
    if not any("ticketsmarche" in e.source.lower() for e in events):
        try:
            from ..scrapers import TicketsMarcheScraper
            tm_events = TicketsMarcheScraper().scrape(city=None)
            from ..scorers import B2CScorer
            scorer = B2CScorer()
            for ev in tm_events:
                score, priority, category, tags, action, parallel = scorer.evaluate(ev.title, ev.description, ev.location)
                ev.b2c_score = score
                ev.b2c_priority = priority
                ev.category = category
                ev.aiesec_tags = tags
                ev.recommended_action = action
                ev.parallel_org = parallel
                events.append(ev)
        except Exception as e:
            logger.error(f"Error seeding TicketsMarche: {e}")

    CACHED_EVENTS = events
    if events:
        try:
            LOCAL_EXPORTER.export(events)
        except Exception:
            pass


@app.on_event("startup")
def startup_event():
    load_initial_events()


@app.get("/", response_class=HTMLResponse)
def get_dashboard_root():
    """Serve the dashboard web application."""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>AIESEC Egypt B2C Event Radar</h1><p>Dashboard static files initializing...</p>"


@app.get("/api/events")
def get_events(
    sort: str = Query("score_desc", pattern="^(score_desc|score_asc|date_asc|date_desc)$"),
    priority: str = "all",
    category: str = "all",
    city: str = "all",
    source: str = "all",
    search: str = "",
    clash_only: bool = False,
    partner_only: bool = False
):
    """Retrieve filtered and sorted events with summary metrics."""
    filtered = list(CACHED_EVENTS)

    # City filter
    if city and city.lower() != "all":
        filtered = [e for e in filtered if e.city.lower() == city.lower()]

    # Priority filter
    if priority and priority.upper() != "ALL":
        filtered = [e for e in filtered if e.b2c_priority.upper() == priority.upper()]

    # Source filter
    if source and source.lower() != "all":
        filtered = [e for e in filtered if source.lower() in e.source.lower()]

    # Category filter
    if category and category.lower() != "all":
        filtered = [e for e in filtered if category.lower() in e.category.lower()]

    # Parallel Org only filter
    if partner_only:
        filtered = [e for e in filtered if e.parallel_org]

    # Clash only filter
    if clash_only:
        filtered = [e for e in filtered if e.clash_warning]

    # Keyword Search
    if search:
        q = search.lower()
        filtered = [
            e for e in filtered
            if q in e.title.lower() or q in e.location.lower() or q in e.organizer.lower() or q in e.description.lower() or q in e.category.lower()
        ]

    # Sorting logic
    if sort == "score_desc":
        filtered.sort(key=lambda x: x.b2c_score, reverse=True)
    elif sort == "score_asc":
        filtered.sort(key=lambda x: x.b2c_score)
    elif sort == "date_asc":
        filtered.sort(key=lambda x: (x.start_date is None, x.start_date))
    elif sort == "date_desc":
        filtered.sort(key=lambda x: (x.start_date is not None, x.start_date), reverse=True)

    # Calculate metrics
    metrics = {
        "total_events": len(CACHED_EVENTS),
        "high_priority": sum(1 for e in CACHED_EVENTS if e.b2c_priority == "HIGH"),
        "clashes": sum(1 for e in CACHED_EVENTS if e.clash_warning),
        "partner_orgs": sum(1 for e in CACHED_EVENTS if e.parallel_org),
        "summits_count": sum(1 for e in CACHED_EVENTS if "summit" in e.source.lower()),
        "ticketsmarche_count": sum(1 for e in CACHED_EVENTS if "ticketsmarche" in e.source.lower())
    }

    return {
        "events": [e.to_api_dict() for e in filtered],
        "total_filtered": len(filtered),
        "metrics": metrics
    }


class PitchRequest(BaseModel):
    event_id: str
    member_name: str
    member_email: str
    member_phone: str
    purpose: str = "event_collaboration"
    custom_notes: Optional[str] = None


@app.post("/api/pitch")
def generate_pitch(req: PitchRequest):
    """Generate partnership or PR pitch tailored to an event."""
    target_event = next((e for e in CACHED_EVENTS if e.event_id == req.event_id), None)
    if not target_event:
        # Fallback dummy event with reasonable title
        target_event = EventRecord(
            event_id=req.event_id,
            title="Campus Career & Leadership Summit",
            source="AIESEC Radar",
            url="http://aiesec.org.eg",
            organizer="Organizing Committee"
        )

    pitch = PitchGenerator.generate_pitch(
        event=target_event,
        member_name=req.member_name,
        member_email=req.member_email,
        member_phone=req.member_phone,
        purpose=req.purpose,
        custom_notes=req.custom_notes
    )
    return pitch


class ScrapeRequest(BaseModel):
    city: Optional[str] = None
    country: str = "egypt"


@app.post("/api/scrape")
def trigger_scrape(req: ScrapeRequest):
    """Trigger a live scrape across event discovery platforms."""
    global CACHED_EVENTS
    events = PIPELINE.run(city=req.city, country=req.country)
    CACHED_EVENTS = events
    LOCAL_EXPORTER.export(events)
    return {
        "success": True,
        "events_count": len(events),
        "message": f"Successfully scraped and scored {len(events)} events!"
    }


@app.post("/api/sync-sheets")
def trigger_sheets_sync():
    """Sync current events to Google Sheets."""
    res = SHEETS_EXPORTER.sync(CACHED_EVENTS)
    return res


class EmailRequest(BaseModel):
    recipients: Optional[List[str]] = None


@app.post("/api/send-email")
def trigger_email_alert(req: EmailRequest):
    """Send high priority digest to specified or configured emails."""
    res = EMAIL_SERVICE.send_digest(CACHED_EVENTS, recipients=req.recipients)
    return res


@app.get("/api/export/{file_format}")
def download_export(file_format: str):
    """Directly download the latest Excel (.xlsx) or CSV file."""
    if file_format.lower() == "excel" or file_format.lower() == "xlsx":
        path = "data/aiesec_egypt_events_latest.xlsx"
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = "AIESEC_Egypt_Events_Latest.xlsx"
    elif file_format.lower() == "csv":
        path = "data/aiesec_egypt_events_latest.csv"
        media_type = "text/csv"
        filename = "AIESEC_Egypt_Events_Latest.csv"
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Use 'excel' or 'csv'.")

    if not os.path.exists(path):
        LOCAL_EXPORTER.export(CACHED_EVENTS)

    return FileResponse(path, media_type=media_type, filename=filename)


def start_dashboard(host: str = "0.0.0.0", port: int = 8000):
    """Start uvicorn server for the dashboard."""
    uvicorn.run(app, host=host, port=port)
