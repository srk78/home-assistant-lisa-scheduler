"""Sidebar panel listing upcoming matches and training sessions."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import voluptuous as vol

from homeassistant.components import frontend, panel_custom, websocket_api
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN, EVENT_TYPE_MATCH, EVENT_TYPE_TRAINING

PANEL_URL_PATH = "lisa-scheduler"
PANEL_TITLE = "LISA Schedule"
PANEL_ICON = "mdi:calendar-clock"
PANEL_WEB_COMPONENT = "lisa-scheduler-panel"
PANEL_STATIC_URL = f"/{DOMAIN}_static"
PANEL_MODULE_URL = f"{PANEL_STATIC_URL}/lisa-scheduler-panel.js"
PANEL_FRONTEND_DIR = Path(__file__).parent / "frontend"

WS_TYPE_UPCOMING_EVENTS = f"{DOMAIN}/upcoming_events"

_PANEL_REGISTERED_KEY = f"{DOMAIN}_panel_registered"


def upcoming_events(
    events: list[dict[str, Any]],
    now: datetime,
    event_types: set[str] | None = None,
) -> list[dict[str, Any]]:
    """Return events that have not ended yet, soonest first.

    ``events`` hold naive schedule-local ISO timestamps, as does ``now``.
    """
    upcoming = [
        event
        for event in events
        if datetime.fromisoformat(event["end_time"]) > now
        and (event_types is None or event["event_type"] in event_types)
    ]
    return sorted(upcoming, key=lambda event: event["start_time"])


@callback
@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_TYPE_UPCOMING_EVENTS,
        vol.Optional("event_types"): [vol.In([EVENT_TYPE_MATCH, EVENT_TYPE_TRAINING])],
    }
)
def ws_upcoming_events(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Send upcoming events from every configured LISA Scheduler entry."""
    event_types = set(msg["event_types"]) if "event_types" in msg else None
    result: list[dict[str, Any]] = []
    timezone = None
    for coordinator in hass.data.get(DOMAIN, {}).values():
        if not coordinator.data:
            continue
        timezone = timezone or coordinator.data.get("timezone")
        result.extend(
            upcoming_events(
                coordinator.data.get("events", []),
                coordinator.schedule_now(),
                event_types,
            )
        )
    result.sort(key=lambda event: event["start_time"])
    connection.send_result(msg["id"], {"timezone": timezone, "events": result})


async def async_register_panel(hass: HomeAssistant) -> None:
    """Register the sidebar panel and its websocket API once."""
    if hass.data.get(_PANEL_REGISTERED_KEY):
        return
    hass.data[_PANEL_REGISTERED_KEY] = True

    websocket_api.async_register_command(hass, ws_upcoming_events)
    await hass.http.async_register_static_paths(
        [StaticPathConfig(PANEL_STATIC_URL, str(PANEL_FRONTEND_DIR), False)]
    )
    await panel_custom.async_register_panel(
        hass,
        webcomponent_name=PANEL_WEB_COMPONENT,
        frontend_url_path=PANEL_URL_PATH,
        module_url=PANEL_MODULE_URL,
        sidebar_title=PANEL_TITLE,
        sidebar_icon=PANEL_ICON,
        require_admin=False,
    )


def async_unregister_panel(hass: HomeAssistant) -> None:
    """Remove the sidebar panel when the last entry is unloaded."""
    if hass.data.pop(_PANEL_REGISTERED_KEY, None):
        frontend.async_remove_panel(hass, PANEL_URL_PATH)
