"""Data update coordinator for ZHC Heating Scheduler."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

import aiohttp

from homeassistant.components.climate import (
    ATTR_TEMPERATURE,
    SERVICE_SET_TEMPERATURE,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, UPDATE_INTERVAL_SCHEDULE
from .scheduler import HeatingScheduler, HeatingWindow
from .scraper import Event, ScheduleScraper

_LOGGER = logging.getLogger(__name__)


class ZHCHeatingCoordinator(DataUpdateCoordinator):
    """Coordinator to manage heating schedule and device control."""

    def __init__(
        self,
        hass: HomeAssistant,
        schedule_url: str,
        climate_entity: str,
        pre_heat_hours: int,
        cool_down_minutes: int,
        target_temperature: float,
        scan_interval: int,
        enabled: bool = True,
        dry_run: bool = False,
    ):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=60),  # Check state every minute
        )

        self.schedule_url = schedule_url
        self.climate_entity = climate_entity
        self.target_temperature = target_temperature
        self.scan_interval = scan_interval
        self.enabled = enabled
        self.dry_run = dry_run

        # Initialize scheduler
        self.scheduler = HeatingScheduler(pre_heat_hours, cool_down_minutes)

        # Initialize scraper
        self._session = aiohttp.ClientSession()
        self.scraper = ScheduleScraper(schedule_url, self._session)

        # State tracking
        self.events: list[Event] = []
        self.heating_windows: list[HeatingWindow] = []
        self.last_schedule_update: datetime | None = None
        self.last_error: str | None = None
        self.is_heating: bool = False
        self.manual_override: tuple[datetime, datetime] | None = None

        # Schedule the first update
        self._schedule_refresh_time = datetime.now()

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch and process data."""
        try:
            # Check if we need to refresh the schedule
            now = datetime.now()
            if self._should_refresh_schedule(now):
                await self._refresh_schedule()

            # Calculate current heating state
            current_heating_state = self._calculate_heating_state(now)

            # Control the climate device if enabled
            if self.enabled and not self.dry_run:
                await self._control_heating(current_heating_state, now)
            elif self.dry_run:
                _LOGGER.info(
                    f"DRY RUN: Would set heating to {current_heating_state} "
                    f"(currently {self.is_heating})"
                )

            # Update state
            self.is_heating = current_heating_state

            # Get schedule summary
            summary = self.scheduler.get_schedule_summary(self.heating_windows, now)

            return {
                "is_heating": self.is_heating,
                "enabled": self.enabled,
                "events": [e.to_dict() for e in self.events],
                "heating_windows": [w.to_dict() for w in self.heating_windows],
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
            _LOGGER.error(f"Error updating coordinator: {err}", exc_info=True)
            raise UpdateFailed(f"Error communicating with schedule: {err}")

    def _should_refresh_schedule(self, now: datetime) -> bool:
        """Check if schedule should be refreshed."""
        if self.last_schedule_update is None:
            return True

        time_since_update = (now - self.last_schedule_update).total_seconds()
        return time_since_update >= self.scan_interval

    async def _refresh_schedule(self) -> None:
        """Refresh the event schedule from the website."""
        try:
            _LOGGER.info("Refreshing schedule from website")

            # Fetch events from website
            self.events = await self.scraper.fetch_schedule(days_ahead=14)

            # Calculate heating windows
            self.heating_windows = self.scheduler.calculate_heating_windows(
                self.events
            )

            self.last_schedule_update = datetime.now()
            self.last_error = None

            _LOGGER.info(
                f"Schedule updated: {len(self.events)} events, "
                f"{len(self.heating_windows)} heating windows"
            )

        except Exception as e:
            self.last_error = f"Schedule refresh failed: {str(e)}"
            _LOGGER.error(self.last_error, exc_info=True)
            # Don't raise - continue with existing schedule

    def _calculate_heating_state(self, now: datetime) -> bool:
        """Calculate whether heating should be on."""
        if not self.enabled:
            return False

        # Check for manual override
        if self.manual_override:
            override_start, override_end = self.manual_override
            if override_start <= now <= override_end:
                _LOGGER.debug("Manual override active")
                return True
            else:
                # Override expired
                _LOGGER.info("Manual override expired")
                self.manual_override = None

        # Check heating windows
        return self.scheduler.should_heat_now(self.heating_windows, now)

    async def _control_heating(self, should_heat: bool, now: datetime) -> None:
        """Control the climate device."""
        if should_heat == self.is_heating:
            # No change needed
            return

        try:
            if should_heat:
                _LOGGER.info(
                    f"Starting heating (target: {self.target_temperature}°C)"
                )
                # Turn on heating and set temperature
                await self.hass.services.async_call(
                    "climate",
                    SERVICE_TURN_ON,
                    {ATTR_ENTITY_ID: self.climate_entity},
                    blocking=True,
                )
                await self.hass.services.async_call(
                    "climate",
                    SERVICE_SET_TEMPERATURE,
                    {
                        ATTR_ENTITY_ID: self.climate_entity,
                        ATTR_TEMPERATURE: self.target_temperature,
                    },
                    blocking=True,
                )
            else:
                _LOGGER.info("Stopping heating")
                await self.hass.services.async_call(
                    "climate",
                    SERVICE_TURN_OFF,
                    {ATTR_ENTITY_ID: self.climate_entity},
                    blocking=True,
                )

        except Exception as e:
            _LOGGER.error(f"Error controlling climate device: {e}", exc_info=True)
            raise

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the scheduler."""
        self.enabled = enabled
        _LOGGER.info(f"Scheduler {'enabled' if enabled else 'disabled'}")
        # Trigger immediate update
        self.hass.async_create_task(self.async_request_refresh())

    def set_override(self, start_time: datetime, end_time: datetime) -> None:
        """Set a manual heating override."""
        self.manual_override = (start_time, end_time)
        _LOGGER.info(f"Manual override set: {start_time} to {end_time}")
        # Trigger immediate update
        self.hass.async_create_task(self.async_request_refresh())

    def clear_override(self) -> None:
        """Clear any manual override."""
        self.manual_override = None
        _LOGGER.info("Manual override cleared")
        # Trigger immediate update
        self.hass.async_create_task(self.async_request_refresh())

    def update_settings(
        self,
        pre_heat_hours: int | None = None,
        cool_down_minutes: int | None = None,
        target_temperature: float | None = None,
        scan_interval: int | None = None,
    ) -> None:
        """Update coordinator settings."""
        if pre_heat_hours is not None or cool_down_minutes is not None:
            current_pre_heat = (
                pre_heat_hours
                if pre_heat_hours is not None
                else self.scheduler.pre_heat_hours
            )
            current_cool_down = (
                cool_down_minutes
                if cool_down_minutes is not None
                else self.scheduler.cool_down_minutes
            )
            self.scheduler.update_settings(current_pre_heat, current_cool_down)

            # Recalculate heating windows with new settings
            self.heating_windows = self.scheduler.calculate_heating_windows(
                self.events
            )

        if target_temperature is not None:
            self.target_temperature = target_temperature
            _LOGGER.info(f"Target temperature updated to {target_temperature}°C")

        if scan_interval is not None:
            self.scan_interval = scan_interval
            _LOGGER.info(f"Scan interval updated to {scan_interval}s")

        # Trigger immediate update
        self.hass.async_create_task(self.async_request_refresh())

    async def async_shutdown(self) -> None:
        """Shutdown the coordinator."""
        _LOGGER.info("Shutting down coordinator")
        if self._session:
            await self._session.close()

    async def async_refresh(self) -> None:
        """Force a schedule refresh."""
        await self._refresh_schedule()
        await self.async_request_refresh()

