"""Sidebar panel listing upcoming matches, training sessions and club events."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from pathlib import Path
from typing import Any

import voluptuous as vol

from homeassistant.components import frontend, panel_custom, websocket_api
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant, callback

from .const import (
    CONF_PANEL_EVENTS,
    CONF_PANEL_MATCHES,
    CONF_PANEL_TRAININGS,
    DOMAIN,
    EVENT_TYPE_CLUB_EVENT,
    EVENT_TYPE_MATCH,
    EVENT_TYPE_TRAINING,
)

PANEL_URL_PATH = "lisa-scheduler"
PANEL_TITLE = "LISA Schedule"
PANEL_ICON = "mdi:calendar-clock"
PANEL_WEB_COMPONENT = "lisa-scheduler-panel"
PANEL_STATIC_URL = f"/{DOMAIN}_static"
PANEL_MODULE_URL = f"{PANEL_STATIC_URL}/lisa-scheduler-panel.js"
PANEL_FRONTEND_DIR = Path(__file__).parent / "frontend"

WS_TYPE_UPCOMING_EVENTS = f"{DOMAIN}/upcoming_events"

_STATIC_REGISTERED_KEY = f"{DOMAIN}_panel_static_registered"
_PANELS_KEY = f"{DOMAIN}_panels"

# Optional extra sidebar panels: option key -> (url path, title, icon, event types)
OPTIONAL_PANELS: dict[str, tuple[str, str, str, list[str]]] = {
    CONF_PANEL_MATCHES: (
        "lisa-scheduler-matches",
        "LISA Matches",
        "mdi:hockey-sticks",
        [EVENT_TYPE_MATCH],
    ),
    CONF_PANEL_TRAININGS: (
        "lisa-scheduler-trainings",
        "LISA Trainings",
        "mdi:run",
        [EVENT_TYPE_TRAINING],
    ),
    CONF_PANEL_EVENTS: (
        "lisa-scheduler-events",
        "LISA Events",
        "mdi:calendar-star",
        [EVENT_TYPE_CLUB_EVENT],
    ),
}


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
        vol.Optional("event_types"): [
            vol.In([EVENT_TYPE_MATCH, EVENT_TYPE_TRAINING, EVENT_TYPE_CLUB_EVENT])
        ],
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


async def async_register_panel(
    hass: HomeAssistant, optional_panels: Iterable[str] = ()
) -> None:
    """Register the main sidebar panel and the enabled optional panels.

    Safe to call repeatedly; panels already registered are left alone.
    """
    if not hass.data.get(_STATIC_REGISTERED_KEY):
        hass.data[_STATIC_REGISTERED_KEY] = True
        websocket_api.async_register_command(hass, ws_upcoming_events)
        await hass.http.async_register_static_paths(
            [StaticPathConfig(PANEL_STATIC_URL, str(PANEL_FRONTEND_DIR), False)]
        )

    registered: set[str] = hass.data.setdefault(_PANELS_KEY, set())
    if PANEL_URL_PATH not in registered:
        registered.add(PANEL_URL_PATH)
        await _register(hass, PANEL_URL_PATH, PANEL_TITLE, PANEL_ICON, None)

    for key in optional_panels:
        url_path, title, icon, event_types = OPTIONAL_PANELS[key]
        if url_path in registered:
            continue
        registered.add(url_path)
        await _register(hass, url_path, title, icon, event_types)


async def _register(
    hass: HomeAssistant,
    url_path: str,
    title: str,
    icon: str,
    event_types: list[str] | None,
) -> None:
    config = {"event_types": event_types, "title": title} if event_types else None
    await panel_custom.async_register_panel(
        hass,
        webcomponent_name=PANEL_WEB_COMPONENT,
        frontend_url_path=url_path,
        module_url=PANEL_MODULE_URL,
        sidebar_title=title,
        sidebar_icon=icon,
        require_admin=False,
        config=config,
    )


def async_unregister_panel(hass: HomeAssistant) -> None:
    """Remove every sidebar panel when the last entry is unloaded."""
    for url_path in hass.data.pop(_PANELS_KEY, set()):
        frontend.async_remove_panel(hass, url_path)
