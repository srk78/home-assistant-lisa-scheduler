"""Heating scheduler logic for ZHC Heating Scheduler."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from .scraper import Event

_LOGGER = logging.getLogger(__name__)


class HeatingWindow:
    """Represents a time window when heating should be active."""

    def __init__(
        self,
        start_time: datetime,
        end_time: datetime,
        events: list[Event] | None = None,
    ):
        """Initialize a heating window."""
        self.start_time = start_time
        self.end_time = end_time
        self.events = events or []

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"HeatingWindow("
            f"start={self.start_time.isoformat()}, "
            f"end={self.end_time.isoformat()}, "
            f"events={len(self.events)})"
        )

    def overlaps(self, other: HeatingWindow) -> bool:
        """Check if this window overlaps with another."""
        return (
            self.start_time <= other.end_time
            and other.start_time <= self.end_time
        )

    def merge(self, other: HeatingWindow) -> HeatingWindow:
        """Merge with another overlapping window."""
        return HeatingWindow(
            start_time=min(self.start_time, other.start_time),
            end_time=max(self.end_time, other.end_time),
            events=self.events + other.events,
        )

    def contains(self, dt: datetime) -> bool:
        """Check if a datetime is within this window."""
        return self.start_time <= dt <= self.end_time

    def to_dict(self) -> dict[str, Any]:
        """Convert window to dictionary."""
        return {
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "duration_minutes": int((self.end_time - self.start_time).total_seconds() / 60),
            "event_count": len(self.events),
            "events": [event.to_dict() for event in self.events],
        }


class HeatingScheduler:
    """Calculate heating schedules based on events."""

    def __init__(
        self,
        pre_heat_hours: int = 2,
        cool_down_minutes: int = 30,
    ):
        """
        Initialize the heating scheduler.
        
        Args:
            pre_heat_hours: Hours before event to start heating
            cool_down_minutes: Minutes before event end to stop heating
        """
        self.pre_heat_hours = pre_heat_hours
        self.cool_down_minutes = cool_down_minutes

    def calculate_heating_windows(
        self, events: list[Event], now: datetime | None = None
    ) -> list[HeatingWindow]:
        """
        Calculate heating windows from events.
        
        Args:
            events: List of scheduled events
            now: Current datetime (defaults to now)
            
        Returns:
            List of HeatingWindow objects, sorted by start time
        """
        if now is None:
            now = datetime.now()

        # Convert events to heating windows
        windows = []
        for event in events:
            # Skip events that have already ended
            if event.end_time < now:
                continue

            # Calculate heating start and end times
            heating_start = event.start_time - timedelta(hours=self.pre_heat_hours)
            heating_end = event.end_time - timedelta(minutes=self.cool_down_minutes)

            # Ensure heating end is after heating start
            if heating_end <= heating_start:
                _LOGGER.warning(
                    f"Event {event.title} results in invalid heating window "
                    f"(end before start). Adjusting."
                )
                heating_end = heating_start + timedelta(hours=1)

            # Don't schedule heating in the past
            if heating_start < now:
                heating_start = now

            windows.append(HeatingWindow(heating_start, heating_end, [event]))

        # Merge overlapping windows
        merged_windows = self._merge_windows(windows)

        # Sort by start time
        merged_windows.sort(key=lambda w: w.start_time)

        _LOGGER.debug(
            f"Calculated {len(merged_windows)} heating windows from {len(events)} events"
        )

        return merged_windows

    def _merge_windows(self, windows: list[HeatingWindow]) -> list[HeatingWindow]:
        """Merge overlapping heating windows."""
        if not windows:
            return []

        # Sort by start time
        sorted_windows = sorted(windows, key=lambda w: w.start_time)

        merged = [sorted_windows[0]]

        for current in sorted_windows[1:]:
            last = merged[-1]

            if current.overlaps(last):
                # Merge overlapping windows
                merged[-1] = last.merge(current)
            else:
                # Add non-overlapping window
                merged.append(current)

        return merged

    def should_heat_now(
        self, windows: list[HeatingWindow], now: datetime | None = None
    ) -> bool:
        """
        Determine if heating should be active now.
        
        Args:
            windows: List of heating windows
            now: Current datetime (defaults to now)
            
        Returns:
            True if heating should be on
        """
        if now is None:
            now = datetime.now()

        return any(window.contains(now) for window in windows)

    def get_current_window(
        self, windows: list[HeatingWindow], now: datetime | None = None
    ) -> HeatingWindow | None:
        """
        Get the current active heating window.
        
        Args:
            windows: List of heating windows
            now: Current datetime (defaults to now)
            
        Returns:
            Current HeatingWindow or None
        """
        if now is None:
            now = datetime.now()

        for window in windows:
            if window.contains(now):
                return window

        return None

    def get_next_window(
        self, windows: list[HeatingWindow], now: datetime | None = None
    ) -> HeatingWindow | None:
        """
        Get the next upcoming heating window.
        
        Args:
            windows: List of heating windows
            now: Current datetime (defaults to now)
            
        Returns:
            Next HeatingWindow or None
        """
        if now is None:
            now = datetime.now()

        future_windows = [w for w in windows if w.start_time > now]

        if future_windows:
            return min(future_windows, key=lambda w: w.start_time)

        return None

    def get_next_state_change(
        self, windows: list[HeatingWindow], now: datetime | None = None
    ) -> tuple[datetime | None, bool]:
        """
        Get the next time heating state will change.
        
        Args:
            windows: List of heating windows
            now: Current datetime (defaults to now)
            
        Returns:
            Tuple of (change_time, will_be_heating)
        """
        if now is None:
            now = datetime.now()

        current_window = self.get_current_window(windows, now)

        if current_window:
            # Currently heating - next change is when current window ends
            return current_window.end_time, False
        else:
            # Not heating - next change is when next window starts
            next_window = self.get_next_window(windows, now)
            if next_window:
                return next_window.start_time, True
            else:
                return None, False

    def get_schedule_summary(
        self, windows: list[HeatingWindow], now: datetime | None = None
    ) -> dict[str, Any]:
        """
        Get a summary of the heating schedule.
        
        Args:
            windows: List of heating windows
            now: Current datetime (defaults to now)
            
        Returns:
            Dictionary with schedule information
        """
        if now is None:
            now = datetime.now()

        current_window = self.get_current_window(windows, now)
        next_window = self.get_next_window(windows, now)
        next_change, will_be_heating = self.get_next_state_change(windows, now)

        # Get today's windows
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        today_windows = [
            w
            for w in windows
            if w.start_time < today_end and w.end_time > today_start
        ]

        # Calculate total heating time today
        total_heating_minutes = sum(
            int((w.end_time - max(w.start_time, today_start)).total_seconds() / 60)
            for w in today_windows
            if w.end_time > today_start
        )

        return {
            "is_heating": current_window is not None,
            "current_window": current_window.to_dict() if current_window else None,
            "next_window": next_window.to_dict() if next_window else None,
            "next_state_change": next_change.isoformat() if next_change else None,
            "next_state_heating": will_be_heating,
            "windows_today": len(today_windows),
            "total_heating_minutes_today": total_heating_minutes,
            "total_windows": len(windows),
        }

    def update_settings(self, pre_heat_hours: int, cool_down_minutes: int) -> None:
        """
        Update scheduler settings.
        
        Args:
            pre_heat_hours: Hours before event to start heating
            cool_down_minutes: Minutes before event end to stop heating
        """
        self.pre_heat_hours = pre_heat_hours
        self.cool_down_minutes = cool_down_minutes
        _LOGGER.info(
            f"Scheduler settings updated: pre_heat={pre_heat_hours}h, "
            f"cool_down={cool_down_minutes}m"
        )

