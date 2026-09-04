"""Local Exporter: Saves results as beautifully styled Excel (.xlsx) and CSV files."""

import os
from datetime import datetime
from typing import List
import pandas as pd

from ..models import EventRecord


class LocalExporter:
    """Handles local disk exports to Excel and CSV."""

    def __init__(self, output_dir: str = "data"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def export(self, events: List[EventRecord], base_filename: str = "aiesec_egypt_events") -> dict:
        """
        Exports events to both Excel and CSV.
        Returns paths to the generated files.
        """
        if not events:
            rows = []
        else:
            rows = [ev.to_sheet_row() for ev in events]

        headers = EventRecord.sheet_headers()
        df = pd.DataFrame(rows, columns=headers)

        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        latest_xlsx = os.path.join(self.output_dir, f"{base_filename}_latest.xlsx")
        timestamped_xlsx = os.path.join(self.output_dir, f"{base_filename}_{timestamp_str}.xlsx")
        latest_csv = os.path.join(self.output_dir, f"{base_filename}_latest.csv")

        # Export CSV (utf-8-sig ensures Arabic and special characters render cleanly in Excel)
        df.to_csv(latest_csv, index=False, encoding="utf-8-sig")

        # Export Styled Excel
        for filepath in [latest_xlsx, timestamped_xlsx]:
            with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name="AIESEC Event Radar", index=False)
                
                # Auto-adjust column widths
                ws = writer.sheets["AIESEC Event Radar"]
                for col in ws.columns:
                    max_len = max(len(str(cell.value or "")) for cell in col)
                    col_letter = col[0].column_letter
                    ws.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 45)

                # Freeze top header row
                ws.freeze_panes = "A2"

        return {
            "excel_latest": os.path.abspath(latest_xlsx),
            "excel_snapshot": os.path.abspath(timestamped_xlsx),
            "csv_latest": os.path.abspath(latest_csv),
            "total_records": len(events)
        }
