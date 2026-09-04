"""Email Notification Dispatcher for AIESEC Team Members."""

import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, List, Optional

from ..models import EventRecord

logger = logging.getLogger(__name__)


class EmailNotificationService:
    """Dispatches AIESEC-branded HTML event digest emails via SMTP."""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        notif_cfg = self.config.get("notifications", {})

        self.enabled = notif_cfg.get("enabled", True)
        self.smtp_host = os.getenv("SMTP_HOST", notif_cfg.get("smtp_host", "smtp.gmail.com"))
        self.smtp_port = int(os.getenv("SMTP_PORT", notif_cfg.get("smtp_port", 587)))
        self.smtp_user = os.getenv("SMTP_USER", notif_cfg.get("smtp_user", ""))
        self.smtp_password = os.getenv("SMTP_PASSWORD", notif_cfg.get("smtp_password", ""))
        self.sender_name = notif_cfg.get("sender_name", "AIESEC Egypt B2C Event Radar")
        self.min_score = float(notif_cfg.get("min_score_threshold", 8.5))

        # Recipients list from env or config
        env_recipients = os.getenv("NOTIFICATION_RECIPIENTS")
        if env_recipients:
            self.recipients = [r.strip() for r in env_recipients.split(",") if r.strip()]
        else:
            self.recipients = notif_cfg.get("recipients", ["b2c.egypt@aiesec.net"])

    def is_configured(self) -> bool:
        """Check if SMTP credentials are provided."""
        return bool(self.smtp_user and self.smtp_password)

    def render_html_digest(self, events: List[EventRecord]) -> str:
        """Generates the styled HTML email body from the template."""
        high_priority = [e for e in events if e.b2c_score >= self.min_score]
        if not high_priority:
            high_priority = events[:10]  # Fallback to top 10

        campus_count = sum(1 for e in high_priority if "University" in e.category or "Student" in e.category)

        # Build event cards HTML
        cards_html = []
        for ev in high_priority[:12]:
            partner_badge = f'<span class="badge badge-partner">{ev.parallel_org}</span>' if ev.parallel_org else ""
            clash_badge = '<span class="badge badge-high">⚠️ Weekend Clash</span>' if ev.clash_warning else ""
            
            card = f"""
            <div class="event-card {'high-priority' if ev.b2c_priority == 'HIGH' else ''}">
              <div class="event-header">
                <h3 class="event-title">{ev.title}</h3>
                <div>
                  <span class="badge badge-high">{ev.b2c_priority} ({ev.b2c_score:.1f})</span>
                  {partner_badge}
                  {clash_badge}
                </div>
              </div>
              <div class="event-meta">
                📅 <strong>Date:</strong> {ev.date_display or 'Date TBA'}<br>
                📍 <strong>Location:</strong> {ev.location} ({ev.city})<br>
                🏷️ <strong>Category:</strong> {ev.category} | <strong>Source:</strong> {ev.source}
              </div>
              <div class="action-box">
                🎯 <strong>Recommended AIESEC B2C Action:</strong> {ev.recommended_action}
              </div>
              <a href="{ev.url}" class="btn" target="_blank">View Event Details & Registration →</a>
            </div>
            """
            cards_html.append(card)

        # Read template file
        template_path = os.path.join(os.path.dirname(__file__), "templates", "digest.html")
        template_content = ""
        if os.path.exists(template_path):
            with open(template_path, "r", encoding="utf-8") as f:
                template_content = f.read()

        html = template_content.replace("{{ total_events }}", str(len(events)))
        html = html.replace("{{ high_priority_count }}", str(len(high_priority)))
        html = html.replace("{{ campus_events_count }}", str(campus_count))
        html = html.replace("{{ event_cards_html }}", "\n".join(cards_html))

        return html

    def send_digest(self, events: List[EventRecord], recipients: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Dispatches HTML digest email to team recipients.
        If SMTP credentials are not configured, saves a local HTML preview for inspection.
        """
        target_recipients = recipients or self.recipients
        html_content = self.render_html_digest(events)

        # Always save local HTML preview
        os.makedirs("data", exist_ok=True)
        preview_path = os.path.abspath("data/latest_email_preview.html")
        with open(preview_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        if not self.is_configured():
            return {
                "success": False,
                "error": "MISSING_SMTP_CREDENTIALS",
                "preview_file": preview_path,
                "message": (
                    "SMTP credentials not configured. Generated a local HTML preview instead!\n"
                    f"Preview file: {preview_path}\n"
                    "To enable automatic sending, set SMTP_USER and SMTP_PASSWORD in .env."
                )
            }

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"🎯 AIESEC B2C Opportunity Alert: {len(events)} Upcoming Events in Egypt"
            msg["From"] = f"{self.sender_name} <{self.smtp_user}>"
            msg["To"] = ", ".join(target_recipients)

            # Plain text fallback
            text_body = f"AIESEC Egypt B2C Event Alert\nTotal Events Found: {len(events)}\n\nView full details on your dashboard: http://localhost:8000"
            msg.attach(MIMEText(text_body, "plain"))
            msg.attach(MIMEText(html_content, "html"))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.smtp_user, target_recipients, msg.as_string())

            logger.info(f"Email digest successfully sent to {target_recipients}")
            return {
                "success": True,
                "recipients": target_recipients,
                "events_count": len(events),
                "preview_file": preview_path,
                "message": f"Successfully sent digest email to {', '.join(target_recipients)}"
            }

        except Exception as e:
            logger.error(f"Failed to send email digest: {e}")
            return {
                "success": False,
                "error": "SMTP_ERROR",
                "preview_file": preview_path,
                "message": f"Failed to send email via SMTP: {str(e)}"
            }
