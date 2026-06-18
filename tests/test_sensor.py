"""Tests for LISA Scheduler sensors."""
from datetime import datetime
from unittest.mock import MagicMock

from custom_components.lisa_scheduler.coordinator import LISASchedulerCoordinator
from custom_components.lisa_scheduler.sensor import (
    LISALastUpdateSensor,
    LISANextEventStartSensor,
)


def _config_entry():
    entry = MagicMock()
    entry.entry_id = "test-entry"
    return entry


def _coordinator(mock_hass, timezone="Europe/Amsterdam"):
    return LISASchedulerCoordinator(
        hass=mock_hass,
        schedule_url="http://example.com/schedule",
        timezone=timezone,
    )


def test_timestamp_sensor_returns_aware_datetime(mock_hass):
    coordinator = _coordinator(mock_hass)
    coordinator.data = {
        "summary": {
            "current_window": None,
            "next_window": {"event_start": "2026-06-18T18:00:00"},
        }
    }
    sensor = LISANextEventStartSensor(coordinator, _config_entry())

    value = sensor.native_value

    assert isinstance(value, datetime)
    assert value.tzinfo is not None


def test_timestamp_sensor_localizes_naive_schedule_time(mock_hass):
    coordinator = _coordinator(mock_hass, timezone="UTC")
    coordinator.data = {
        "summary": {
            "current_window": None,
            "next_window": {"event_start": "2026-01-01T12:00:00"},
        }
    }
    sensor = LISANextEventStartSensor(coordinator, _config_entry())

    value = sensor.native_value

    assert value.tzinfo is not None
    assert value.astimezone(coordinator.schedule_timezone).hour == 12


def test_last_update_sensor_exposes_stale_error_attributes(mock_hass):
    coordinator = _coordinator(mock_hass)
    coordinator.data = {
        "last_schedule_update": "2026-06-18T10:00:00",
        "last_refresh_attempt": "2026-06-18T11:00:00",
        "last_error": "Schedule refresh failed: boom",
        "last_refresh_failed": True,
        "schedule_stale": True,
        "timezone": "Europe/Amsterdam",
        "events": [{"title": "Training"}],
        "event_windows": [{"event_count": 1}],
    }
    sensor = LISALastUpdateSensor(coordinator, _config_entry())

    attrs = sensor.extra_state_attributes

    assert attrs["last_error"] == "Schedule refresh failed: boom"
    assert attrs["last_refresh_failed"] is True
    assert attrs["schedule_stale"] is True
    assert attrs["timezone"] == "Europe/Amsterdam"
    assert attrs["scraped_event_count"] == 1
    assert attrs["event_window_count"] == 1
