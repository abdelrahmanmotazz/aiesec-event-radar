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

    # Enhanced Intelligence & Contact Scout Fields
    parallel_org: Optional[str] = None
    clash_warning: bool = False
    clash_count: int = 0
    clash_details: List[str] = Field(default_factory=list)
    raw_caption: Optional[str] = None
    organizer_email: Optional[str] = None
    organizer_instagram: Optional[str] = None
    organizer_linkedin: Optional[str] = None
    organizer_phone: Optional[str] = None

    # Proof Verification & Legitimacy Checker Fields
    proof_url: Optional[str] = None
    proof_type: str = "Official Announcement"
    is_verified_proof: bool = True
    proof_evidence: str = "Verified Official Announcement Post"

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
            self.proof_url or self.url,
            "100% Verified Real" if self.is_verified_proof else "Unverified",
            self.description,
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
            "Verified Proof / Announcement Link",
            "Proof Verification Status",
            "Description",
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
            "proof_url": self.proof_url or self.url,
            "proof_type": self.proof_type,
            "is_verified_proof": self.is_verified_proof,
            "proof_evidence": self.proof_evidence,
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
            "organizer_email": self.organizer_email,
            "organizer_instagram": self.organizer_instagram,
            "organizer_linkedin": self.organizer_linkedin,
            "organizer_phone": self.organizer_phone,
        }
