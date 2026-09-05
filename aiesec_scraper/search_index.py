"""In-Memory SQLite FTS5 Full-Text Search Engine for Bilingual Event Matching."""

import re
import sqlite3
from typing import List, Optional
from .models import EventRecord


class EventSearchIndex:
    """High-performance SQLite FTS5 search engine for fuzzy bilingual querying."""

    def __init__(self, events: Optional[List[EventRecord]] = None):
        self.conn = sqlite3.connect(":memory:")
        self._init_fts_table()
        if events:
            self.index_events(events)

    def _init_fts_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS events_fts USING fts5(
                event_id UNINDEXED,
                title,
                description,
                city,
                location,
                category,
                organizer,
                tokenize = 'unicode61 remove_diacritics 2'
            );
        """)
        self.conn.commit()

    def index_events(self, events: List[EventRecord]):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM events_fts")
        for ev in events:
            cursor.execute(
                """
                INSERT INTO events_fts (event_id, title, description, city, location, category, organizer)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    ev.event_id,
                    ev.title or "",
                    ev.description or "",
                    ev.city or "",
                    ev.location or "",
                    ev.category or "",
                    ev.organizer or ""
                )
            )
        self.conn.commit()

    def search(self, query: str, limit: int = 50) -> List[str]:
        """Return ranked event_ids matching the query."""
        if not query or not query.strip():
            return []

        clean_tokens = [re.sub(r"[^\w]", "", t) for t in query.strip().split()]
        clean_tokens = [t for t in clean_tokens if t]
        if not clean_tokens:
            return []

        fts_query = " ".join(f'"{t}"*' for t in clean_tokens)

        cursor = self.conn.cursor()
        try:
            cursor.execute(
                """
                SELECT event_id, rank
                FROM events_fts
                WHERE events_fts MATCH ?
                ORDER BY rank
                LIMIT ?
                """,
                (fts_query, limit)
            )
            return [row[0] for row in cursor.fetchall()]
        except Exception:
            like_term = f"%{query.strip()}%"
            cursor.execute(
                """
                SELECT event_id FROM events_fts
                WHERE title LIKE ? OR description LIKE ? OR city LIKE ?
                LIMIT ?
                """,
                (like_term, like_term, like_term, limit)
            )
            return [row[0] for row in cursor.fetchall()]