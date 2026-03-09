"""Config flow for LISA Scheduler integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_DRY_RUN,
    CONF_ENABLED,
    CONF_LOGO_URL,
    CONF_PRE_EVENT_TRIGGERS,
    CONF_SCAN_INTERVAL,
    CONF_SCHEDULE_URL,
    DEFAULT_DRY_RUN,
    DEFAULT_ENABLED,
    DEFAULT_PRE_EVENT_TRIGGERS,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)
from .scraper import ScheduleScraper

_LOGGER = logging.getLogger(__name__)


def _parse_triggers(value: str) -> list[int]:
    """Parse a comma-separated string of trigger minutes into a sorted list."""
    try:
        parts = [part.strip() for part in value.split(",") if part.strip()]
        if not parts:
            raise vol.Invalid("At least one trigger time is required")
        values = [int(p) for p in parts]
        for v in values:
            if not (0 <= v <= 1440):
                raise vol.Invalid(
                    f"Trigger time {v} is out of range (must be 0–1440)"
                )
        # Deduplicate and sort descending
        return sorted(set(values), reverse=True)
    except vol.Invalid:
        raise
    except (ValueError, TypeError) as err:
        raise vol.Invalid(f"Invalid trigger times: {err}") from err


async def validate_schedule_url(hass: HomeAssistant, url: str) -> bool:
    """Validate that the schedule URL is accessible."""
    session = async_get_clientsession(hass)
    scraper = ScheduleScraper(url, session)
    try:
        await scraper.fetch_schedule(days_ahead=1)
        return True
    except aiohttp.ClientError as err:
        _LOGGER.error("Cannot connect to schedule URL: %s", err)
        return False
    except Exception as err:
        _LOGGER.error("Unexpected error validating URL: %s", err)
        return False


class LISASchedulerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for LISA Scheduler."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        errors = {}

        if user_input is not None:
            url_valid = await validate_schedule_url(self.hass, user_input[CONF_SCHEDULE_URL])
            if not url_valid:
                errors["base"] = "cannot_connect"

            if not errors:
                await self.async_set_unique_id(user_input[CONF_SCHEDULE_URL])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title="LISA Scheduler", data=user_input)

        default_triggers_str = ", ".join(str(m) for m in DEFAULT_PRE_EVENT_TRIGGERS)
        data_schema = vol.Schema(
            {
                vol.Required(CONF_SCHEDULE_URL): str,
                vol.Optional(CONF_LOGO_URL, default=""): str,
                vol.Optional(
                    CONF_PRE_EVENT_TRIGGERS,
                    default=default_triggers_str,
                ): vol.All(str, _parse_triggers),
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=DEFAULT_SCAN_INTERVAL,
                ): vol.All(vol.Coerce(int), vol.Range(min=600, max=86400)),
                vol.Optional(CONF_DRY_RUN, default=DEFAULT_DRY_RUN): bool,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_import(self, import_config: dict[str, Any]) -> dict[str, Any]:
        """Import a config entry from configuration.yaml."""
        await self.async_set_unique_id(import_config[CONF_SCHEDULE_URL])
        self._abort_if_unique_id_configured()
        return self.async_create_entry(title="LISA Scheduler", data=import_config)

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> LISASchedulerOptionsFlow:
        return LISASchedulerOptionsFlow(config_entry)


class LISASchedulerOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for LISA Scheduler."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_logo_url = self.config_entry.options.get(
            CONF_LOGO_URL,
            self.config_entry.data.get(CONF_LOGO_URL, ""),
        )
        current_triggers = self.config_entry.options.get(
            CONF_PRE_EVENT_TRIGGERS,
            self.config_entry.data.get(CONF_PRE_EVENT_TRIGGERS, DEFAULT_PRE_EVENT_TRIGGERS),
        )
        current_triggers_str = ", ".join(str(m) for m in current_triggers)
        current_scan_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL,
            self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )
        current_enabled = self.config_entry.options.get(
            CONF_ENABLED,
            self.config_entry.data.get(CONF_ENABLED, DEFAULT_ENABLED),
        )
        current_dry_run = self.config_entry.options.get(
            CONF_DRY_RUN,
            self.config_entry.data.get(CONF_DRY_RUN, DEFAULT_DRY_RUN),
        )

        options_schema = vol.Schema(
            {
                vol.Optional(CONF_LOGO_URL, default=current_logo_url): str,
                vol.Optional(
                    CONF_PRE_EVENT_TRIGGERS,
                    default=current_triggers_str,
                ): vol.All(str, _parse_triggers),
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=current_scan_interval,
                ): vol.All(vol.Coerce(int), vol.Range(min=600, max=86400)),
                vol.Optional(CONF_ENABLED, default=current_enabled): bool,
                vol.Optional(CONF_DRY_RUN, default=current_dry_run): bool,
            }
        )

        return self.async_show_form(step_id="init", data_schema=options_schema)
