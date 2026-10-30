"""Tests for the upcoming events sidebar panel."""

from datetime import datetime
from unittest.mock import MagicMock

from custom_components.lisa_scheduler.const import DOMAIN
from custom_components.lisa_scheduler.panel import ws_upcoming_events, upcoming_events

NOW = datetime(2026, 3, 10, 12, 0)


def _event(event_type, start, end):
    return {
        "event_type": event_type,
        "start_time": start,
        "end_time": end,
        "title": event_type,
    }


EVENTS = [
    _event("training", "2026-03-12T18:00:00", "2026-03-12T19:30:00"),
    _event("match", "2026-03-11T10:00:00", "2026-03-11T12:00:00"),
    _event("match", "2026-03-09T10:00:00", "2026-03-09T12:00:00"),
    _event("training", "2026-03-10T11:00:00", "2026-03-10T13:00:00"),
]


def test_upcoming_events_drops_ended_and_sorts_by_start():
    result = upcoming_events(EVENTS, NOW)

    assert [e["start_time"] for e in result] == [
        "2026-03-10T11:00:00",
        "2026-03-11T10:00:00",
        "2026-03-12T18:00:00",
    ]


def test_upcoming_events_filters_by_type():
    result = upcoming_events(EVENTS, NOW, {"match"})

    assert [e["event_type"] for e in result] == ["match"]
    assert result[0]["start_time"] == "2026-03-11T10:00:00"


def _hass_with(*coordinators):
    hass = MagicMock()
    hass.data = {DOMAIN: {str(i): c for i, c in enumerate(coordinators)}}
    return hass


def _coordinator(events, data=True):
    coordinator = MagicMock()
    coordinator.data = {"events": events, "timezone": "Europe/Amsterdam"} if data else None
    coordinator.schedule_now.return_value = NOW
    return coordinator


def test_ws_upcoming_events_merges_entries_and_skips_unloaded():
    connection = MagicMock()
    hass = _hass_with(
        _coordinator(EVENTS[:2]), _coordinator(EVENTS[2:]), _coordinator([], data=False)
    )

    # The decorated handler is a plain callable underneath the websocket_command wrapper.
    ws_upcoming_events(hass, connection, {"id": 7, "type": "lisa_scheduler/upcoming_events"})

    connection.send_result.assert_called_once()
    msg_id, payload = connection.send_result.call_args.args
    assert msg_id == 7
    assert payload["timezone"] == "Europe/Amsterdam"
    assert [e["start_time"] for e in payload["events"]] == [
        "2026-03-10T11:00:00",
        "2026-03-11T10:00:00",
        "2026-03-12T18:00:00",
    ]
