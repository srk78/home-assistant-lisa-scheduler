"""The LISA Scheduler integration."""

from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import ConfigType

from .api_client import normalize_api_url
from .const import (
    CONF_API_TIMEZONE,
    CONF_API_URL,
    CONF_DRY_RUN,
    CONF_ENABLED,
    CONF_INCLUDE_EXTERNAL_EVENTS,
    CONF_LOGO_URL,
    CONF_PRE_EVENT_TRIGGERS,
    CONF_PRE_FIRST_EVENT_TRIGGERS,
    CONF_PRE_LAST_EVENT_END_TRIGGERS,
    CONF_POST_LAST_EVENT_TRIGGERS,
    CONF_SCAN_INTERVAL,
    DEFAULT_DRY_RUN,
    DEFAULT_ENABLED,
    DEFAULT_INCLUDE_EXTERNAL_EVENTS,
    DEFAULT_PRE_EVENT_TRIGGERS,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_TIMEZONE,
    DOMAIN,
    LEGACY_CONF_SCHEDULE_URL,
    SERVICE_CLEAR_OVERRIDE,
    SERVICE_DISABLE,
    SERVICE_ENABLE,
    SERVICE_REFRESH_SCHEDULE,
    SERVICE_SET_OVERRIDE,
)
from .coordinator import LISASchedulerCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.BUTTON]

TRIGGER_LIST_SCHEMA = vol.All(
    cv.ensure_list, [vol.All(cv.positive_int, vol.Range(max=1440))]
)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_API_URL): cv.url,
                vol.Optional(
                    CONF_INCLUDE_EXTERNAL_EVENTS,
                    default=DEFAULT_INCLUDE_EXTERNAL_EVENTS,
                ): cv.boolean,
                vol.Optional(CONF_LOGO_URL, default=""): cv.string,
                vol.Optional(
                    CONF_PRE_EVENT_TRIGGERS, default=DEFAULT_PRE_EVENT_TRIGGERS
                ): TRIGGER_LIST_SCHEMA,
                vol.Optional(
                    CONF_PRE_FIRST_EVENT_TRIGGERS, default=[]
                ): TRIGGER_LIST_SCHEMA,
                vol.Optional(
                    CONF_PRE_LAST_EVENT_END_TRIGGERS, default=[]
                ): TRIGGER_LIST_SCHEMA,
                vol.Optional(
                    CONF_POST_LAST_EVENT_TRIGGERS, default=[]
                ): TRIGGER_LIST_SCHEMA,
                vol.Optional(
                    CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                ): vol.All(cv.positive_int, vol.Range(min=600, max=86400)),
                vol.Optional(CONF_ENABLED, default=DEFAULT_ENABLED): cv.boolean,
                vol.Optional(CONF_DRY_RUN, default=DEFAULT_DRY_RUN): cv.boolean,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the LISA Scheduler component from YAML."""
    hass.data.setdefault(DOMAIN, {})

    if DOMAIN not in config:
        return True

    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": "import"},
            data=config[DOMAIN],
        )
    )
    return True


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate experimental scraper entries to the API-only schema."""
    if entry.version >= 2:
        return True

    data = dict(entry.data)
    options = dict(entry.options)
    legacy_url = data.pop(LEGACY_CONF_SCHEDULE_URL, None)
    if legacy_url and CONF_API_URL not in data:
        try:
            data[CONF_API_URL] = normalize_api_url(legacy_url)
        except ValueError:
            data[CONF_API_URL] = legacy_url

    for key in ("scraper_sources", "date_format", "time_format", "timezone"):
        data.pop(key, None)
        options.pop(key, None)

    data.setdefault(CONF_API_TIMEZONE, DEFAULT_TIMEZONE)
    data.setdefault(CONF_INCLUDE_EXTERNAL_EVENTS, DEFAULT_INCLUDE_EXTERNAL_EVENTS)
    hass.config_entries.async_update_entry(entry, data=data, options=options, version=2)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up LISA Scheduler from a config entry."""
    _LOGGER.info("Setting up LISA Scheduler")

    coordinator = LISASchedulerCoordinator(
        hass,
        entry.data[CONF_API_URL],
        pre_event_triggers=entry.options.get(
            CONF_PRE_EVENT_TRIGGERS,
            entry.data.get(CONF_PRE_EVENT_TRIGGERS, DEFAULT_PRE_EVENT_TRIGGERS),
        ),
        scan_interval=entry.options.get(
            CONF_SCAN_INTERVAL,
            entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        ),
        enabled=entry.options.get(
            CONF_ENABLED, entry.data.get(CONF_ENABLED, DEFAULT_ENABLED)
        ),
        dry_run=entry.options.get(
            CONF_DRY_RUN, entry.data.get(CONF_DRY_RUN, DEFAULT_DRY_RUN)
        ),
        logo_url=entry.options.get(CONF_LOGO_URL, entry.data.get(CONF_LOGO_URL, "")),
        pre_first_event_triggers=entry.options.get(
            CONF_PRE_FIRST_EVENT_TRIGGERS,
            entry.data.get(CONF_PRE_FIRST_EVENT_TRIGGERS, []),
        ),
        pre_last_event_end_triggers=entry.options.get(
            CONF_PRE_LAST_EVENT_END_TRIGGERS,
            entry.data.get(CONF_PRE_LAST_EVENT_END_TRIGGERS, []),
        ),
        post_last_event_triggers=entry.options.get(
            CONF_POST_LAST_EVENT_TRIGGERS,
            entry.data.get(CONF_POST_LAST_EVENT_TRIGGERS, []),
        ),
        timezone=entry.data.get(CONF_API_TIMEZONE, DEFAULT_TIMEZONE),
        include_external_events=entry.options.get(
            CONF_INCLUDE_EXTERNAL_EVENTS,
            entry.data.get(
                CONF_INCLUDE_EXTERNAL_EVENTS, DEFAULT_INCLUDE_EXTERNAL_EVENTS
            ),
        ),
        session=async_get_clientsession(hass),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def handle_refresh_schedule(call: ServiceCall) -> None:
        await coordinator.async_refresh()

    async def handle_enable(call: ServiceCall) -> None:
        coordinator.set_enabled(True)

    async def handle_disable(call: ServiceCall) -> None:
        coordinator.set_enabled(False)

    async def handle_set_override(call: ServiceCall) -> None:
        coordinator.set_override(call.data["start_time"], call.data["end_time"])

    async def handle_clear_override(call: ServiceCall) -> None:
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
        schema=vol.Schema(  # type: ignore[arg-type]
            {
                vol.Required("start_time"): cv.datetime,
                vol.Required("end_time"): cv.datetime,
            }
        ),
    )
    hass.services.async_register(DOMAIN, SERVICE_CLEAR_OVERRIDE, handle_clear_override)

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    _LOGGER.info("Unloading LISA Scheduler")

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_shutdown()

    if not hass.data[DOMAIN]:
        hass.services.async_remove(DOMAIN, SERVICE_REFRESH_SCHEDULE)
        hass.services.async_remove(DOMAIN, SERVICE_ENABLE)
        hass.services.async_remove(DOMAIN, SERVICE_DISABLE)
        hass.services.async_remove(DOMAIN, SERVICE_SET_OVERRIDE)
        hass.services.async_remove(DOMAIN, SERVICE_CLEAR_OVERRIDE)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
