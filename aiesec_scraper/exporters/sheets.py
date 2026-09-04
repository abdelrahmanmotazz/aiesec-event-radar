"""Google Sheets Exporter using gspread with graceful setup detection and formatting."""

import logging
import os
from typing import List, Optional
import gspread
from google.oauth2.service_account import Credentials

from ..models import EventRecord

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


class GoogleSheetsExporter:
    """Synchronizes scraped event records directly to Google Sheets."""

    def __init__(
        self,
        service_account_file: str = "service_account.json",
        sheet_name: str = "AIESEC Egypt B2C Event Radar",
        sheet_id: Optional[str] = None
    ):
        self.service_account_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", service_account_file)
        self.sheet_name = os.getenv("GOOGLE_SHEET_NAME", sheet_name)
        self.sheet_id = os.getenv("GOOGLE_SHEET_ID", sheet_id)

    def is_configured(self) -> bool:
        """Check if service account file exists on disk."""
        return os.path.exists(self.service_account_file)

    def get_service_account_email(self) -> Optional[str]:
        """Read client_email from credentials file so user can share the sheet with it."""
        if not self.is_configured():
            return None
        try:
            import json
            with open(self.service_account_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("client_email")
        except Exception:
            return None

    def sync(self, events: List[EventRecord]) -> dict:
        """
        Uploads event records to Google Sheets.
        If credentials are missing, returns an informative status guide.
        """
        if not self.is_configured():
            return {
                "success": False,
                "error": "MISSING_CREDENTIALS",
                "message": (
                    f"Google Service Account key '{self.service_account_file}' not found.\n"
                    "To enable automatic sync:\n"
                    "1. Download your Google Cloud Service Account JSON key.\n"
                    f"2. Save it as '{self.service_account_file}' in the project root.\n"
                    "3. Share your target Google Sheet with your service account email with 'Editor' permissions."
                )
            }

        try:
            creds = Credentials.from_service_account_file(self.service_account_file, scopes=SCOPES)
            gc = gspread.authorize(creds)

            # Open sheet by ID or by Name
            sh = None
            if self.sheet_id:
                sh = gc.open_by_key(self.sheet_id)
            else:
                try:
                    sh = gc.open(self.sheet_name)
                except gspread.exceptions.SpreadsheetNotFound:
                    logger.info(f"Spreadsheet '{self.sheet_name}' not found. Creating a new one...")
                    sh = gc.create(self.sheet_name)

            worksheet = sh.get_worksheet(0)
            if not worksheet:
                worksheet = sh.add_worksheet(title="Events Radar", rows=1000, cols=20)
            else:
                worksheet.update_title("Events Radar")

            # Prepare data payload
            headers = EventRecord.sheet_headers()
            rows = [headers] + [ev.to_sheet_row() for ev in events]

            # Clear and bulk-update
            worksheet.clear()
            worksheet.update(rows, "A1")

            # Apply styling & formatting via gspread
            try:
                worksheet.format("A1:M1", {
                    "textFormat": {"bold": True, "foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0}},
                    "backgroundColor": {"red": 0.0, "green": 0.38, "blue": 0.69},  # AIESEC Blue (#0060B0)
                    "horizontalAlignment": "CENTER",
                })
                worksheet.freeze(rows=1)
            except Exception as format_err:
                logger.debug(f"Formatting notice: {format_err}")

            return {
                "success": True,
                "sheet_title": sh.title,
                "sheet_url": sh.url,
                "records_synced": len(events)
            }

        except Exception as e:
            logger.error(f"Failed to sync to Google Sheets: {e}")
            return {
                "success": False,
                "error": "SYNC_FAILED",
                "message": str(e)
            }
