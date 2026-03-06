"""Data update coordinator for ZHC Scheduler."""
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
    UPDATE_INTERVAL_SCHEDULE,
)
from .scheduler import EventScheduler, EventWindow
from .scraper import Event, ScheduleScraper
from .configurable_scraper import ConfigurableScraper

_LOGGER = logging.getLogger(__name__)


class ZHCHeatingCoordinator(DataUpdateCoordinator):
    """Coordinator that tracks the scraped schedule and fires HA events on transitions."""

    def __init__(
        self,
        hass: HomeAssistant,
        schedule_url: str,
        pre_event_minutes: int,
        scan_interval: int,
        enabled: bool = True,
        dry_run: bool = False,
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
        self.scan_interval = scan_interval
        self.enabled = enabled
        self.dry_run = dry_run

        self.scheduler = EventScheduler(pre_event_minutes)

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
        pre_event_minutes: int | None = None,
        scan_interval: int | None = None,
    ) -> None:
        if pre_event_minutes is not None:
            self.scheduler.update_settings(pre_event_minutes)
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
