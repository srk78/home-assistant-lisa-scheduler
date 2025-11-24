"""Config flow for ZHC Heating Scheduler integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_URL
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_CLIMATE_ENTITY,
    CONF_COOL_DOWN_MINUTES,
    CONF_DRY_RUN,
    CONF_ENABLED,
    CONF_PRE_HEAT_HOURS,
    CONF_SCAN_INTERVAL,
    CONF_SCHEDULE_URL,
    CONF_TARGET_TEMPERATURE,
    DEFAULT_COOL_DOWN_MINUTES,
    DEFAULT_DRY_RUN,
    DEFAULT_ENABLED,
    DEFAULT_PRE_HEAT_HOURS,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_TARGET_TEMPERATURE,
    DOMAIN,
)
from .scraper import ScheduleScraper

_LOGGER = logging.getLogger(__name__)


async def validate_schedule_url(hass: HomeAssistant, url: str) -> bool:
    """Validate that the schedule URL is accessible."""
    session = async_get_clientsession(hass)
    scraper = ScheduleScraper(url, session)

    try:
        # Try to fetch the schedule
        await scraper.fetch_schedule(days_ahead=1)
        return True
    except aiohttp.ClientError as err:
        _LOGGER.error(f"Cannot connect to schedule URL: {err}")
        return False
    except Exception as err:
        _LOGGER.error(f"Unexpected error validating URL: {err}")
        return False


class ZHCHeatingSchedulerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ZHC Heating Scheduler."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate the schedule URL
            url_valid = await validate_schedule_url(
                self.hass, user_input[CONF_SCHEDULE_URL]
            )

            if not url_valid:
                errors["base"] = "cannot_connect"
            else:
                # Validate climate entity exists
                climate_entity = user_input[CONF_CLIMATE_ENTITY]
                state = self.hass.states.get(climate_entity)
                
                if state is None:
                    errors["base"] = "invalid_climate_entity"
                elif not climate_entity.startswith("climate."):
                    errors["base"] = "invalid_climate_entity"

            if not errors:
                # Create the config entry
                await self.async_set_unique_id(user_input[CONF_SCHEDULE_URL])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title="ZHC Heating Scheduler",
                    data=user_input,
                )

        # Show the configuration form
        data_schema = vol.Schema(
            {
                vol.Required(CONF_SCHEDULE_URL): str,
                vol.Required(CONF_CLIMATE_ENTITY): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="climate")
                ),
                vol.Optional(
                    CONF_PRE_HEAT_HOURS,
                    default=DEFAULT_PRE_HEAT_HOURS,
                ): vol.All(vol.Coerce(int), vol.Range(min=0, max=24)),
                vol.Optional(
                    CONF_COOL_DOWN_MINUTES,
                    default=DEFAULT_COOL_DOWN_MINUTES,
                ): vol.All(vol.Coerce(int), vol.Range(min=0, max=120)),
                vol.Optional(
                    CONF_TARGET_TEMPERATURE,
                    default=DEFAULT_TARGET_TEMPERATURE,
                ): vol.All(vol.Coerce(float), vol.Range(min=5.0, max=35.0)),
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=DEFAULT_SCAN_INTERVAL,
                ): vol.All(vol.Coerce(int), vol.Range(min=600, max=86400)),
                vol.Optional(
                    CONF_DRY_RUN,
                    default=DEFAULT_DRY_RUN,
                ): bool,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_import(self, import_config: dict[str, Any]) -> dict[str, Any]:
        """Import a config entry from configuration.yaml."""
        # Check if already configured
        await self.async_set_unique_id(import_config[CONF_SCHEDULE_URL])
        self._abort_if_unique_id_configured()

        return await self.async_step_user(import_config)

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> ZHCHeatingSchedulerOptionsFlow:
        """Get the options flow for this handler."""
        return ZHCHeatingSchedulerOptionsFlow(config_entry)


class ZHCHeatingSchedulerOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for ZHC Heating Scheduler."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Manage the options."""
        if user_input is not None:
            # Update the config entry options
            return self.async_create_entry(title="", data=user_input)

        # Get current values
        current_pre_heat = self.config_entry.options.get(
            CONF_PRE_HEAT_HOURS,
            self.config_entry.data.get(CONF_PRE_HEAT_HOURS, DEFAULT_PRE_HEAT_HOURS),
        )
        current_cool_down = self.config_entry.options.get(
            CONF_COOL_DOWN_MINUTES,
            self.config_entry.data.get(
                CONF_COOL_DOWN_MINUTES, DEFAULT_COOL_DOWN_MINUTES
            ),
        )
        current_target_temp = self.config_entry.options.get(
            CONF_TARGET_TEMPERATURE,
            self.config_entry.data.get(
                CONF_TARGET_TEMPERATURE, DEFAULT_TARGET_TEMPERATURE
            ),
        )
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
                vol.Optional(
                    CONF_PRE_HEAT_HOURS,
                    default=current_pre_heat,
                ): vol.All(vol.Coerce(int), vol.Range(min=0, max=24)),
                vol.Optional(
                    CONF_COOL_DOWN_MINUTES,
                    default=current_cool_down,
                ): vol.All(vol.Coerce(int), vol.Range(min=0, max=120)),
                vol.Optional(
                    CONF_TARGET_TEMPERATURE,
                    default=current_target_temp,
                ): vol.All(vol.Coerce(float), vol.Range(min=5.0, max=35.0)),
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=current_scan_interval,
                ): vol.All(vol.Coerce(int), vol.Range(min=600, max=86400)),
                vol.Optional(
                    CONF_ENABLED,
                    default=current_enabled,
                ): bool,
                vol.Optional(
                    CONF_DRY_RUN,
                    default=current_dry_run,
                ): bool,
            }
        )

        return self.async_show_form(step_id="init", data_schema=options_schema)

