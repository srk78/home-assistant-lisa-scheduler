"""Device triggers for LISA Scheduler."""
from __future__ import annotations

import voluptuous as vol

from homeassistant.components.device_automation import DEVICE_TRIGGER_BASE_SCHEMA
from homeassistant.components.homeassistant.triggers import event as event_trigger
from homeassistant.const import CONF_DEVICE_ID, CONF_DOMAIN, CONF_PLATFORM, CONF_TYPE
from homeassistant.core import HomeAssistant

from .const import (
    DOMAIN,
    EVENT_EVENT_ENDED,
    EVENT_EVENT_STARTED,
    EVENT_PRE_EVENT_TRIGGER,
    EVENT_WINDOW_ENDED,
    EVENT_WINDOW_STARTED,
)

# Maps trigger type key → (event_type, friendly label)
TRIGGER_TYPES: dict[str, tuple[str, str]] = {
    "pre_event_window_opened": (EVENT_WINDOW_STARTED, "Pre-event window opened"),
    "pre_event_window_closed": (EVENT_WINDOW_ENDED, "Pre-event window closed"),
    "event_started": (EVENT_EVENT_STARTED, "Event started"),
    "event_ended": (EVENT_EVENT_ENDED, "Event ended"),
    "pre_event_trigger": (EVENT_PRE_EVENT_TRIGGER, "Pre-event trigger fired"),
}

TRIGGER_SCHEMA = DEVICE_TRIGGER_BASE_SCHEMA.extend(
    {vol.Required(CONF_TYPE): vol.In(TRIGGER_TYPES)}
)


async def async_get_triggers(hass: HomeAssistant, device_id: str) -> list[dict]:
    """Return a list of triggers available for a LISA Scheduler device."""
    return [
        {
            CONF_PLATFORM: "device",
            CONF_DOMAIN: DOMAIN,
            CONF_DEVICE_ID: device_id,
            CONF_TYPE: trigger_type,
        }
        for trigger_type in TRIGGER_TYPES
    ]


async def async_attach_trigger(hass, config, action, trigger_info):
    """Attach a trigger to a LISA Scheduler device event."""
    event_type, _label = TRIGGER_TYPES[config[CONF_TYPE]]
    event_config = event_trigger.TRIGGER_SCHEMA(
        {
            CONF_PLATFORM: "event",
            event_trigger.CONF_EVENT_TYPE: event_type,
        }
    )
    return await event_trigger.async_attach_trigger(
        hass, event_config, action, trigger_info, platform_type="device"
    )
