"""Source-neutral schedule models for LISA Scheduler."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class Event:
    """A normalized event consumed by the scheduler."""

    event_type: str
    start_time: datetime
    end_time: datetime
    title: str = ""
    location: str = ""
    source_event_id: str | None = None
    source_record_id: str | None = None
    end_time_estimated: bool = False
    at_club_venue: bool | None = None
    venue_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable representation for entities and HA events."""
        return {
            "event_type": self.event_type,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "title": self.title,
            "location": self.location,
            "source_event_id": self.source_event_id,
            "source_record_id": self.source_record_id,
            "end_time_estimated": self.end_time_estimated,
            "at_club_venue": self.at_club_venue,
            "venue_id": self.venue_id,
        }
