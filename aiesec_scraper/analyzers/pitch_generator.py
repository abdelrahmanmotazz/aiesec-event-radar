"""Automated Partnership and PR Collaboration Pitch Generator for AIESEC Team Members."""

import urllib.parse
from typing import Dict, Optional
from ..models import EventRecord


class PitchGenerator:
    """Generates customized, high-converting outreach emails for event organizers."""

    @staticmethod
    def generate_pitch(
        event: EventRecord,
        member_name: str,
        member_email: str,
        member_phone: str,
        purpose: str = "event_collaboration",
        custom_notes: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generates a tailored email pitch.
        
        purpose options:
          - 'event_collaboration': Booth booking, flyering, speaking slot, physical recruitment
          - 'pr_collaboration': Media partnership, social media shoutout, cross-promotion
        """
        org = event.organizer if event.organizer and event.organizer != "Unknown" else "Event Organizing Committee"
        date_str = event.date_display or "upcoming dates"
        venue_str = event.location or "your venue"

        if purpose == "pr_collaboration":
            subject = f"PR & Media Partnership Proposal: Youth Event Radar Egypt x {event.title}"
            body = (
                f"Dear {org},\n\n"
                f"I hope this email finds you well.\n\n"
                f"My name is {member_name}, representing Youth Event Radar Egypt — Egypt's premier youth leadership and student event discovery network. "
                f"We noticed your upcoming event, \"{event.title}\", scheduled for {date_str} at {venue_str}, and wanted to applaud your initiative in creating such an engaging platform for youth and students.\n\n"
                f"We would love to explore a PR & Media Cross-Promotion Collaboration between our organizations. Specifically, we can offer:\n"
                f"• Mutual social media exposure reaching our national network of over 10,000+ Egyptian university students and fresh graduates.\n"
                f"• Inclusion of your event in our weekly student community newsletter and campus announcement channels.\n"
                f"• Dedicated shoutouts and co-branded promotional assets.\n\n"
                f"In return, we would be delighted to discuss featuring youth exchange and leadership development opportunities as a partner on your digital channels.\n\n"
                f"Could we schedule a brief 10-minute discovery call this week to align on this partnership?\n\n"
                f"Best regards,\n"
                f"{member_name}\n"
                f"Business-to-Consumer (B2C) Partnerships Team\n"
                f"Youth Event Radar Egypt\n"
                f"Email: {member_email}\n"
                f"Phone / WhatsApp: {member_phone}\n"
                f"Website: eventradar.org.eg\n"
            )
        else:
            # Default: Event Collaboration / Physical Booth
            subject = f"Event Collaboration & Booth Partnership: Youth Event Radar Egypt x {event.title}"
            body = (
                f"Dear {org},\n\n"
                f"I hope you are having a productive week.\n\n"
                f"My name is {member_name}, reaching out from the B2C & Campus Activations team at Youth Event Radar Egypt. "
                f"We have been following the preparations for \"{event.title}\" ({date_str} at {venue_str}) and believe our mission of empowering youth through skill-building and leadership development aligns directly with your audience.\n\n"
                f"We would like to formally request an on-ground collaboration during your event, such as:\n"
                f"1. A physical youth information booth / stand for student advisory and leadership opportunities.\n"
                f"2. Student engagement activation (interactive games, leadership quizzes, and youth empowerment talks).\n"
                f"3. Active promotion of your event across our campus networks at top Egyptian universities.\n\n"
                f"Could you please share your exhibitor/partnership deck or let us know who is responsible for on-ground booth allocations? "
                f"I would appreciate a quick phone call or meeting to discuss how we can bring mutual value to your attendees.\n\n"
                f"Looking forward to hearing from you.\n\n"
                f"Warm regards,\n"
                f"{member_name}\n"
                f"Business-to-Consumer (B2C) Team\n"
                f"Youth Event Radar Egypt\n"
                f"Email: {member_email}\n"
                f"Phone / WhatsApp: {member_phone}\n"
                f"Website: eventradar.org.eg\n"
            )

        if custom_notes:
            body += f"\nAdditional Note: {custom_notes}\n"

        # Generate direct mailto link
        query_params = {
            "subject": subject,
            "body": body
        }
        mailto_url = f"mailto:?{urllib.parse.urlencode(query_params, quote_via=urllib.parse.quote)}"

        return {
            "subject": subject,
            "body": body,
            "mailto_url": mailto_url,
            "event_title": event.title,
            "purpose": purpose
        }
