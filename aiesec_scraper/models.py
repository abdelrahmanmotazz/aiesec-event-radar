"""Unified Data Models for Scraped Events, Clash Detection, and AIESEC B2C Metadata."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class EventRecord(BaseModel):
    """Standardized event representation across all platforms."""
    event_id: str
    title: str
    source: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    date_display: str = ""
    location: str = "TBA / Online"
    city: str = "Egypt"
    country: str = "Egypt"
    url: str
    ticket_type: str = "Unknown"
    organizer: str = "Unknown"
    description: str = ""
    category: str = "General"
    aiesec_tags: List[str] = Field(default_factory=list)
    b2c_score: float = 0.0
    b2c_priority: str = "LOW"
    recommended_action: str = "General Monitoring"

    # Enhanced Intelligence Fields
    parallel_org: Optional[str] = None
    clash_warning: bool = False
    clash_count: int = 0
    clash_details: List[str] = Field(default_factory=list)
    raw_caption: Optional[str] = None

    def to_sheet_row(self) -> List[str]:
        """Convert record to a flat list for Google Sheets / Excel output."""
        return [
            self.title,
            self.date_display or (self.start_date.strftime("%Y-%m-%d %H:%M") if self.start_date else "TBA"),
            self.city,
            self.location,
            self.source,
            self.category,
            self.parallel_org or "Independent",
            self.ticket_type,
            f"{self.b2c_score:.1f}",
            self.b2c_priority,
            "⚠️ Clash" if self.clash_warning else "Clear",
            ", ".join(self.aiesec_tags),
            self.recommended_action,
            self.organizer,
            self.url,
        ]

    @classmethod
    def sheet_headers(cls) -> List[str]:
        """Header names for the spreadsheet export."""
        return [
            "Event Title",
            "Date & Time",
            "City",
            "Venue / Location",
            "Platform",
            "Primary Category",
            "Student Org / Partner",
            "Pricing / Ticket",
            "B2C Score (1-10)",
            "AIESEC Priority",
            "Clash Status",
            "Relevant Tags",
            "Recommended B2C Action",
            "Organizer",
            "Event Link",
        ]

    def to_api_dict(self) -> Dict[str, Any]:
        """Dictionary representation suitable for web API responses."""
        return {
            "event_id": self.event_id,
            "title": self.title,
            "source": self.source,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "date_display": self.date_display,
            "location": self.location,
            "city": self.city,
            "country": self.country,
            "url": self.url,
            "ticket_type": self.ticket_type,
            "organizer": self.organizer,
            "description": self.description,
            "category": self.category,
            "aiesec_tags": self.aiesec_tags,
            "b2c_score": self.b2c_score,
            "b2c_priority": self.b2c_priority,
            "recommended_action": self.recommended_action,
            "parallel_org": self.parallel_org,
            "clash_warning": self.clash_warning,
            "clash_count": self.clash_count,
            "clash_details": self.clash_details,
        }
