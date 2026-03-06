"""Event scheduler logic for ZHC Scheduler."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from .scraper import Event

_LOGGER = logging.getLogger(__name__)


class EventWindow:
    """A time window spanning the pre-event lead time through the event end."""

    def __init__(
        self,
        window_start: datetime,
        event_start: datetime,
        window_end: datetime,
        events: list[Event] | None = None,
    ):
        self.window_start = window_start
        self.event_start = event_start  # earliest event start within this window
        self.window_end = window_end
        self.events = events or []

    def __repr__(self) -> str:
        return (
            f"EventWindow("
            f"window_start={self.window_start.isoformat()}, "
            f"event_start={self.event_start.isoformat()}, "
            f"window_end={self.window_end.isoformat()}, "
            f"events={len(self.events)})"
        )

    def overlaps(self, other: EventWindow) -> bool:
        return self.window_start <= other.window_end and other.window_start <= self.window_end

    def merge(self, other: EventWindow) -> EventWindow:
        return EventWindow(
            window_start=min(self.window_start, other.window_start),
            event_start=min(self.event_start, other.event_start),
            window_end=max(self.window_end, other.window_end),
            events=self.events + other.events,
        )

    def in_window(self, dt: datetime) -> bool:
        """True anywhere within the full window (pre-event lead time + event)."""
        return self.window_start <= dt <= self.window_end

    def in_event_period(self, dt: datetime) -> bool:
        """True only during the actual event time (after pre-event lead time)."""
        return self.event_start <= dt <= self.window_end

    def to_dict(self) -> dict[str, Any]:
        return {
            "window_start": self.window_start.isoformat(),
            "event_start": self.event_start.isoformat(),
            "window_end": self.window_end.isoformat(),
            "pre_event_minutes": int(
                (self.event_start - self.window_start).total_seconds() / 60
            ),
            "duration_minutes": int(
                (self.window_end - self.window_start).total_seconds() / 60
            ),
            "event_count": len(self.events),
            "events": [event.to_dict() for event in self.events],
        }


class EventScheduler:
    """Calculate event windows from a scraped schedule."""

    def __init__(self, pre_event_minutes: int = 120):
        self.pre_event_minutes = pre_event_minutes

    def calculate_event_windows(
        self, events: list[Event], now: datetime | None = None
    ) -> list[EventWindow]:
        """
        Calculate event windows from a list of events.

        Each window starts `pre_event_minutes` before the event and ends at
        the event end. Overlapping windows are merged.
        """
        if now is None:
            now = datetime.now()

        windows = []
        for event in events:
            if event.end_time < now:
                continue

            window_start = event.start_time - timedelta(minutes=self.pre_event_minutes)
            window_end = event.end_time

            # Don't schedule the lead-time in the past
            if window_start < now:
                window_start = now

            windows.append(
                EventWindow(window_start, event.start_time, window_end, [event])
            )

        merged = self._merge_windows(windows)
        merged.sort(key=lambda w: w.window_start)

        _LOGGER.debug(
            "Calculated %d event windows from %d events", len(merged), len(events)
        )
        return merged

    def _merge_windows(self, windows: list[EventWindow]) -> list[EventWindow]:
        if not windows:
            return []

        sorted_windows = sorted(windows, key=lambda w: w.window_start)
        merged = [sorted_windows[0]]

        for current in sorted_windows[1:]:
            last = merged[-1]
            if current.overlaps(last):
                merged[-1] = last.merge(current)
            else:
                merged.append(current)

        return merged

    def is_in_window(
        self, windows: list[EventWindow], now: datetime | None = None
    ) -> bool:
        if now is None:
            now = datetime.now()
        return any(w.in_window(now) for w in windows)

    def is_event_active(
        self, windows: list[EventWindow], now: datetime | None = None
    ) -> bool:
        if now is None:
            now = datetime.now()
        return any(w.in_event_period(now) for w in windows)

    def get_current_window(
        self, windows: list[EventWindow], now: datetime | None = None
    ) -> EventWindow | None:
        if now is None:
            now = datetime.now()
        for window in windows:
            if window.in_window(now):
                return window
        return None

    def get_next_window(
        self, windows: list[EventWindow], now: datetime | None = None
    ) -> EventWindow | None:
        if now is None:
            now = datetime.now()
        future = [w for w in windows if w.window_start > now]
        return min(future, key=lambda w: w.window_start) if future else None

    def get_next_state_change(
        self, windows: list[EventWindow], now: datetime | None = None
    ) -> tuple[datetime | None, bool]:
        if now is None:
            now = datetime.now()
        current = self.get_current_window(windows, now)
        if current:
            return current.window_end, False
        next_w = self.get_next_window(windows, now)
        if next_w:
            return next_w.window_start, True
        return None, False

    def get_schedule_summary(
        self, windows: list[EventWindow], now: datetime | None = None
    ) -> dict[str, Any]:
        if now is None:
            now = datetime.now()

        current = self.get_current_window(windows, now)
        next_w = self.get_next_window(windows, now)
        next_change, will_be_active = self.get_next_state_change(windows, now)

        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        today_windows = [
            w
            for w in windows
            if w.window_start < today_end and w.window_end > today_start
        ]
        total_window_minutes = sum(
            int(
                (w.window_end - max(w.window_start, today_start)).total_seconds() / 60
            )
            for w in today_windows
            if w.window_end > today_start
        )

        return {
            "is_window_active": current is not None,
            "is_event_active": self.is_event_active(windows, now),
            "current_window": current.to_dict() if current else None,
            "next_window": next_w.to_dict() if next_w else None,
            "next_state_change": next_change.isoformat() if next_change else None,
            "next_state_active": will_be_active,
            "windows_today": len(today_windows),
            "total_window_minutes_today": total_window_minutes,
            "total_windows": len(windows),
        }

    def update_settings(self, pre_event_minutes: int) -> None:
        self.pre_event_minutes = pre_event_minutes
        _LOGGER.info("Scheduler settings updated: pre_event=%d min", pre_event_minutes)
