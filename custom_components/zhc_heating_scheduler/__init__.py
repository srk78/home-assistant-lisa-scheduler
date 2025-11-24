"""The ZHC Heating Scheduler integration."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

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
    SERVICE_CLEAR_OVERRIDE,
    SERVICE_DISABLE,
    SERVICE_ENABLE,
    SERVICE_REFRESH_SCHEDULE,
    SERVICE_SET_OVERRIDE,
)
from .coordinator import ZHCHeatingCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR]

# YAML configuration schema
CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_SCHEDULE_URL): cv.url,
                vol.Required(CONF_CLIMATE_ENTITY): cv.entity_id,
                vol.Optional(
                    CONF_PRE_HEAT_HOURS, default=DEFAULT_PRE_HEAT_HOURS
                ): cv.positive_int,
                vol.Optional(
                    CONF_COOL_DOWN_MINUTES, default=DEFAULT_COOL_DOWN_MINUTES
                ): cv.positive_int,
                vol.Optional(
                    CONF_TARGET_TEMPERATURE, default=DEFAULT_TARGET_TEMPERATURE
                ): vol.Coerce(float),
                vol.Optional(
                    CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                ): cv.positive_int,
                vol.Optional(CONF_ENABLED, default=DEFAULT_ENABLED): cv.boolean,
                vol.Optional(CONF_DRY_RUN, default=DEFAULT_DRY_RUN): cv.boolean,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the ZHC Heating Scheduler component from YAML."""
    hass.data.setdefault(DOMAIN, {})

    if DOMAIN not in config:
        return True

    conf = config[DOMAIN]
    
    # Create a config entry from YAML if one doesn't exist
    # This allows seamless migration to config flow
    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": "import"},
            data=conf,
        )
    )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up ZHC Heating Scheduler from a config entry."""
    _LOGGER.info("Setting up ZHC Heating Scheduler")

    coordinator = ZHCHeatingCoordinator(
        hass,
        entry.data[CONF_SCHEDULE_URL],
        entry.data[CONF_CLIMATE_ENTITY],
        entry.options.get(CONF_PRE_HEAT_HOURS, entry.data.get(CONF_PRE_HEAT_HOURS, DEFAULT_PRE_HEAT_HOURS)),
        entry.options.get(CONF_COOL_DOWN_MINUTES, entry.data.get(CONF_COOL_DOWN_MINUTES, DEFAULT_COOL_DOWN_MINUTES)),
        entry.options.get(CONF_TARGET_TEMPERATURE, entry.data.get(CONF_TARGET_TEMPERATURE, DEFAULT_TARGET_TEMPERATURE)),
        entry.options.get(CONF_SCAN_INTERVAL, entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)),
        entry.options.get(CONF_ENABLED, entry.data.get(CONF_ENABLED, DEFAULT_ENABLED)),
        entry.options.get(CONF_DRY_RUN, entry.data.get(CONF_DRY_RUN, DEFAULT_DRY_RUN)),
    )

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services
    async def handle_refresh_schedule(call: ServiceCall) -> None:
        """Handle the refresh schedule service call."""
        _LOGGER.info("Manual schedule refresh requested")
        await coordinator.async_refresh()

    async def handle_enable(call: ServiceCall) -> None:
        """Handle the enable service call."""
        _LOGGER.info("Scheduler enabled via service call")
        coordinator.set_enabled(True)

    async def handle_disable(call: ServiceCall) -> None:
        """Handle the disable service call."""
        _LOGGER.info("Scheduler disabled via service call")
        coordinator.set_enabled(False)

    async def handle_set_override(call: ServiceCall) -> None:
        """Handle the set override service call."""
        start_time = call.data.get("start_time")
        end_time = call.data.get("end_time")
        _LOGGER.info(f"Manual override set: {start_time} to {end_time}")
        coordinator.set_override(start_time, end_time)

    async def handle_clear_override(call: ServiceCall) -> None:
        """Handle the clear override service call."""
        _LOGGER.info("Manual override cleared")
        coordinator.clear_override()

    hass.services.async_register(
        DOMAIN, SERVICE_REFRESH_SCHEDULE, handle_refresh_schedule
    )
    hass.services.async_register(DOMAIN, SERVICE_ENABLE, handle_enable)
    hass.services.async_register(DOMAIN, SERVICE_DISABLE, handle_disable)
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_OVERRIDE,
        handle_set_override,
        schema=vol.Schema(
            {
                vol.Required("start_time"): cv.datetime,
                vol.Required("end_time"): cv.datetime,
            }
        ),
    )
    hass.services.async_register(DOMAIN, SERVICE_CLEAR_OVERRIDE, handle_clear_override)

    # Handle options updates
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.info("Unloading ZHC Heating Scheduler")

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        # Stop the coordinator
        await coordinator.async_shutdown()

    # Remove services if this is the last entry
    if not hass.data[DOMAIN]:
        hass.services.async_remove(DOMAIN, SERVICE_REFRESH_SCHEDULE)
        hass.services.async_remove(DOMAIN, SERVICE_ENABLE)
        hass.services.async_remove(DOMAIN, SERVICE_DISABLE)
        hass.services.async_remove(DOMAIN, SERVICE_SET_OVERRIDE)
        hass.services.async_remove(DOMAIN, SERVICE_CLEAR_OVERRIDE)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)

