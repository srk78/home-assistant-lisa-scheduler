"""Data update coordinator for LISA Scheduler."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_SCRAPER_SOURCES,
    CONF_DATE_FORMAT,
    CONF_TIME_FORMAT,
    CONF_TIMEZONE,
    DEFAULT_DATE_FORMAT,
    DEFAULT_TIME_FORMAT,
    DEFAULT_TIMEZONE,
    DOMAIN,
    EVENT_WINDOW_STARTED,
    EVENT_WINDOW_ENDED,
    EVENT_EVENT_STARTED,
    EVENT_EVENT_ENDED,
    EVENT_PRE_EVENT_TRIGGER,
    EVENT_FIRST_EVENT_STARTED,
    EVENT_LAST_EVENT_ENDED,
    EVENT_PRE_FIRST_EVENT_TRIGGER,
    EVENT_PRE_LAST_EVENT_END_TRIGGER,
    EVENT_POST_LAST_EVENT_TRIGGER,
    UPDATE_INTERVAL_SCHEDULE,
)
from .scheduler import EventScheduler, EventWindow
from .scraper import Event, ScheduleScraper
from .configurable_scraper import ConfigurableScraper

_LOGGER = logging.getLogger(__name__)


class LISASchedulerCoordinator(DataUpdateCoordinator):
    """Coordinator that tracks the scraped schedule and fires HA events on transitions."""

    def __init__(
        self,
        hass: HomeAssistant,
        schedule_url: str,
        pre_event_triggers: list[int] | None = None,
        scan_interval: int = 21600,
        enabled: bool = True,
        dry_run: bool = False,
        logo_url: str = "",
        pre_first_event_triggers: list[int] | None = None,
        pre_last_event_end_triggers: list[int] | None = None,
        post_last_event_triggers: list[int] | None = None,
        scraper_sources: list[dict] | None = None,
        date_format: str = DEFAULT_DATE_FORMAT,
        time_format: str = DEFAULT_TIME_FORMAT,
        timezone: str = DEFAULT_TIMEZONE,
        session: aiohttp.ClientSession | None = None,
    ):
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=60),
        )

        self.schedule_url = schedule_url
        self.logo_url = logo_url
        self.scan_interval = scan_interval
        self.enabled = enabled
        self.dry_run = dry_run

        self.pre_first_event_triggers = sorted(pre_first_event_triggers or [], reverse=True)
        self.pre_last_event_end_triggers = sorted(pre_last_event_end_triggers or [], reverse=True)
        self.post_last_event_triggers = sorted(post_last_event_triggers or [], reverse=True)

        self.scheduler = EventScheduler(pre_event_triggers)

        if scraper_sources:
            _LOGGER.info("Using configurable scraper with %d sources", len(scraper_sources))
            self.scraper = ConfigurableScraper(
                sources=scraper_sources,
                date_format=date_format,
                time_format=time_format,
                timezone=timezone,
                session=session,
            )
        else:
            _LOGGER.info("Using basic scraper for URL: %s", schedule_url)
            self.scraper = ScheduleScraper(schedule_url, session)

        # State tracking
        self.events: list[Event] = []
        self.event_windows: list[EventWindow] = []
        self.last_schedule_update: datetime | None = None
        self.last_error: str | None = None
        self.is_window_active: bool = False
        self.is_event_active: bool = False
        self.manual_override: tuple[datetime, datetime] | None = None
        self._fired_triggers: set[tuple[str, int]] = set()
        self._fired_first_event_started: set[str] = set()
        self._fired_last_event_ended: set[str] = set()
        self._fired_pre_first_triggers: set[tuple[str, int]] = set()
        self._fired_pre_last_end_triggers: set[tuple[str, int]] = set()
        self._fired_post_last_triggers: set[tuple[str, int]] = set()

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            now = datetime.now()
            if self._should_refresh_schedule(now):
                await self._refresh_schedule()

            new_window_active = self._calculate_window_state(now)
            new_event_active = self._calculate_event_state(now)

            if self.enabled:
                if self.dry_run:
                    if new_window_active != self.is_window_active:
                        _LOGGER.info(
                            "DRY RUN: window_active would change %s → %s",
                            self.is_window_active,
                            new_window_active,
                        )
                    if new_event_active != self.is_event_active:
                        _LOGGER.info(
                            "DRY RUN: event_active would change %s → %s",
                            self.is_event_active,
                            new_event_active,
                        )
                else:
                    self._fire_transition_events(
                        new_window_active, new_event_active, now
                    )

            self.is_window_active = new_window_active
            self.is_event_active = new_event_active

            self._fire_pre_event_triggers(now)
            self._fire_day_boundary_events(now)

            summary = self.scheduler.get_schedule_summary(self.event_windows, now)

            return {
                "is_window_active": self.is_window_active,
                "is_event_active": self.is_event_active,
                "enabled": self.enabled,
                "events": [e.to_dict() for e in self.events],
                "event_windows": [w.to_dict() for w in self.event_windows],
                "last_schedule_update": (
                    self.last_schedule_update.isoformat()
                    if self.last_schedule_update
                    else None
                ),
                "last_error": self.last_error,
                "summary": summary,
                "manual_override": self.manual_override is not None,
            }

        except Exception as err:
            self.last_error = str(err)
            _LOGGER.error("Error updating coordinator: %s", err, exc_info=True)
            raise UpdateFailed(f"Error communicating with schedule: {err}")

    def _should_refresh_schedule(self, now: datetime) -> bool:
        if self.last_schedule_update is None:
            return True
        time_since_update = (now - self.last_schedule_update).total_seconds()
        return time_since_update >= self.scan_interval

    async def _refresh_schedule(self) -> None:
        try:
            _LOGGER.info("Refreshing schedule from website")
            self.events = await self.scraper.fetch_schedule(days_ahead=14)
            self.event_windows = self.scheduler.calculate_event_windows(self.events)
            self.last_schedule_update = datetime.now()
            self.last_error = None
            _LOGGER.info(
                "Schedule updated: %d events, %d windows",
                len(self.events),
                len(self.event_windows),
            )
            # Clean up fired trigger keys whose event_start is older than 24 hours
            cutoff = datetime.now() - timedelta(hours=24)
            self._fired_triggers = {
                (event_start_iso, minutes_before)
                for event_start_iso, minutes_before in self._fired_triggers
                if datetime.fromisoformat(event_start_iso) > cutoff
            }
            # Clean up day-keyed tracking sets older than 2 days
            now = datetime.now()
            day_cutoff = (now - timedelta(days=2)).date().isoformat()
            for s in (self._fired_first_event_started, self._fired_last_event_ended):
                s.discard(day_cutoff)
            for s in (self._fired_pre_first_triggers, self._fired_pre_last_end_triggers, self._fired_post_last_triggers):
                s.difference_update({k for k in s if k[0] <= day_cutoff})
        except Exception as e:
            self.last_error = f"Schedule refresh failed: {e}"
            _LOGGER.error(self.last_error, exc_info=True)

    def _calculate_window_state(self, now: datetime) -> bool:
        if not self.enabled:
            return False
        if self.manual_override:
            override_start, override_end = self.manual_override
            if override_start <= now <= override_end:
                return True
            _LOGGER.info("Manual override expired")
            self.manual_override = None
        return self.scheduler.is_in_window(self.event_windows, now)

    def _calculate_event_state(self, now: datetime) -> bool:
        if not self.enabled:
            return False
        if self.manual_override:
            override_start, override_end = self.manual_override
            if override_start <= now <= override_end:
                return True
        return self.scheduler.is_event_active(self.event_windows, now)

    def _fire_transition_events(
        self, new_window_active: bool, new_event_active: bool, now: datetime
    ) -> None:
        current_window = self.scheduler.get_current_window(self.event_windows, now)
        window_data = current_window.to_dict() if current_window else {}

        if new_window_active and not self.is_window_active:
            _LOGGER.info("Pre-event window started")
            self.hass.bus.async_fire(EVENT_WINDOW_STARTED, window_data)
        elif not new_window_active and self.is_window_active:
            _LOGGER.info("Pre-event window ended")
            self.hass.bus.async_fire(EVENT_WINDOW_ENDED, {})

        if new_event_active and not self.is_event_active:
            _LOGGER.info("Event started")
            self.hass.bus.async_fire(EVENT_EVENT_STARTED, window_data)
        elif not new_event_active and self.is_event_active:
            _LOGGER.info("Event ended")
            self.hass.bus.async_fire(EVENT_EVENT_ENDED, {})

    def _fire_pre_event_triggers(self, now: datetime) -> None:
        """Fire pre-event trigger HA events for each configured trigger time."""
        if not self.enabled:
            return
        if self.dry_run:
            _LOGGER.info("DRY RUN: skipping pre-event trigger checks")
            return
        for window in self.event_windows:
            for minutes_before in self.scheduler.pre_event_triggers:
                trigger_time = window.event_start - timedelta(minutes=minutes_before)
                fire_key = (window.event_start.isoformat(), minutes_before)
                if trigger_time <= now and fire_key not in self._fired_triggers:
                    self._fired_triggers.add(fire_key)
                    # Only fire if trigger time is within 2 minutes (prevents stale fires after restart)
                    if trigger_time > now - timedelta(seconds=120):
                        payload = {**window.to_dict(), "minutes_before": minutes_before}
                        _LOGGER.info(
                            "Pre-event trigger fired: %d min before event at %s",
                            minutes_before,
                            window.event_start.isoformat(),
                        )
                        self.hass.bus.async_fire(EVENT_PRE_EVENT_TRIGGER, payload)

    def _fire_day_boundary_events(self, now: datetime) -> None:
        """Fire day-boundary HA events for first/last event of the day."""
        if not self.enabled:
            return

        staleness = timedelta(seconds=120)
        today_str = now.date().isoformat()

        first_window = self.scheduler.get_first_window_today(self.event_windows, now)
        last_window = self.scheduler.get_last_window_today(self.event_windows, now)

        if first_window:
            # first_event_started
            if first_window.event_start <= now and today_str not in self._fired_first_event_started:
                self._fired_first_event_started.add(today_str)
                if first_window.event_start > now - staleness:
                    if self.dry_run:
                        _LOGGER.info("DRY RUN: would fire lisa_scheduler_first_event_started")
                    else:
                        _LOGGER.info("First event of the day started")
                        self.hass.bus.async_fire(EVENT_FIRST_EVENT_STARTED, first_window.to_dict())

            # pre_first_event_triggers
            for minutes in self.pre_first_event_triggers:
                trigger_time = first_window.event_start - timedelta(minutes=minutes)
                key = (today_str, minutes)
                if trigger_time <= now and key not in self._fired_pre_first_triggers:
                    self._fired_pre_first_triggers.add(key)
                    if trigger_time > now - staleness:
                        if self.dry_run:
                            _LOGGER.info("DRY RUN: would fire lisa_scheduler_pre_first_event_trigger minutes_before=%d", minutes)
                        else:
                            _LOGGER.info("Pre-first-event trigger: %d min before first event", minutes)
                            self.hass.bus.async_fire(EVENT_PRE_FIRST_EVENT_TRIGGER, {**first_window.to_dict(), "minutes_before": minutes})

        if last_window:
            # last_event_ended
            if last_window.window_end <= now and today_str not in self._fired_last_event_ended:
                self._fired_last_event_ended.add(today_str)
                if last_window.window_end > now - staleness:
                    if self.dry_run:
                        _LOGGER.info("DRY RUN: would fire lisa_scheduler_last_event_ended")
                    else:
                        _LOGGER.info("Last event of the day ended")
                        self.hass.bus.async_fire(EVENT_LAST_EVENT_ENDED, last_window.to_dict())

            # pre_last_event_end_triggers
            for minutes in self.pre_last_event_end_triggers:
                trigger_time = last_window.window_end - timedelta(minutes=minutes)
                key = (today_str, minutes)
                if trigger_time <= now and key not in self._fired_pre_last_end_triggers:
                    self._fired_pre_last_end_triggers.add(key)
                    if trigger_time > now - staleness:
                        if self.dry_run:
                            _LOGGER.info("DRY RUN: would fire lisa_scheduler_pre_last_event_end_trigger minutes_before=%d", minutes)
                        else:
                            _LOGGER.info("Pre-last-event-end trigger: %d min before last event ends", minutes)
                            self.hass.bus.async_fire(EVENT_PRE_LAST_EVENT_END_TRIGGER, {**last_window.to_dict(), "minutes_before": minutes})

            # post_last_event_triggers
            for minutes in self.post_last_event_triggers:
                trigger_time = last_window.window_end + timedelta(minutes=minutes)
                key = (today_str, minutes)
                if trigger_time <= now and key not in self._fired_post_last_triggers:
                    self._fired_post_last_triggers.add(key)
                    if trigger_time > now - staleness:
                        if self.dry_run:
                            _LOGGER.info("DRY RUN: would fire lisa_scheduler_post_last_event_trigger minutes_after=%d", minutes)
                        else:
                            _LOGGER.info("Post-last-event trigger: %d min after last event ended", minutes)
                            self.hass.bus.async_fire(EVENT_POST_LAST_EVENT_TRIGGER, {**last_window.to_dict(), "minutes_after": minutes})

    def set_enabled(self, enabled: bool) -> None:
        self.enabled = enabled
        _LOGGER.info("Scheduler %s", "enabled" if enabled else "disabled")
        self.hass.async_create_task(self.async_request_refresh())

    def set_override(self, start_time: datetime, end_time: datetime) -> None:
        self.manual_override = (start_time, end_time)
        _LOGGER.info("Manual override set: %s to %s", start_time, end_time)
        self.hass.async_create_task(self.async_request_refresh())

    def clear_override(self) -> None:
        self.manual_override = None
        _LOGGER.info("Manual override cleared")
        self.hass.async_create_task(self.async_request_refresh())

    def update_settings(
        self,
        pre_event_triggers: list[int] | None = None,
        scan_interval: int | None = None,
    ) -> None:
        if pre_event_triggers is not None:
            self.scheduler.update_settings(pre_event_triggers)
            self.event_windows = self.scheduler.calculate_event_windows(self.events)

        if scan_interval is not None:
            self.scan_interval = scan_interval
            _LOGGER.info("Scan interval updated to %ds", scan_interval)

        self.hass.async_create_task(self.async_request_refresh())

    async def async_shutdown(self) -> None:
        _LOGGER.info("Shutting down coordinator")

    async def async_refresh(self) -> None:
        await self._refresh_schedule()
        await self.async_request_refresh()
