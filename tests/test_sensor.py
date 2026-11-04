"""Tests for LISA Scheduler sensors."""

from datetime import datetime
from unittest.mock import MagicMock

from custom_components.lisa_scheduler.coordinator import LISASchedulerCoordinator
from custom_components.lisa_scheduler.sensor import (
    LISACurrentEventSensor,
    LISALastUpdateSensor,
    LISANextEventSensor,
    LISANextEventStartSensor,
)


def _config_entry():
    entry = MagicMock()
    entry.entry_id = "test-entry"
    return entry


def _coordinator(mock_hass, timezone="Europe/Amsterdam"):
    return LISASchedulerCoordinator(
        hass=mock_hass,
        api_url="http://example.com/v1/events",
        timezone=timezone,
        session=MagicMock(),
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
        "last_api_fetch_success": "2026-06-18T11:00:00",
        "last_error": "Schedule refresh failed: boom",
        "last_refresh_failed": True,
        "schedule_stale": True,
        "timezone": "Europe/Amsterdam",
        "api_url": "http://example.com/v1/events",
        "include_external_events": False,
        "api_generated_at": "2026-06-18T11:00:00+00:00",
        "upstream_last_attempt": "2026-06-18T10:55:00+00:00",
        "upstream_error_category": "games_timeout",
        "upstream_stale": True,
        "upstream_partial": True,
        "upstream_record_counts": {"games": 1, "trainings": 0},
        "upstream_unschedulable_counts": {"games": 2, "trainings": 0},
        "upstream_sources": {"games": {"stale": True}},
        "events": [{"title": "Training"}],
        "event_windows": [{"event_count": 1}],
    }
    sensor = LISALastUpdateSensor(coordinator, _config_entry())

    attrs = sensor.extra_state_attributes

    assert attrs["last_error"] == "Schedule refresh failed: boom"
    assert attrs["last_refresh_failed"] is True
    assert attrs["schedule_stale"] is True
    assert attrs["timezone"] == "Europe/Amsterdam"
    assert attrs["api_url"] == "http://example.com/v1/events"
    assert attrs["api_event_count"] == 1
    assert attrs["upstream_error_category"] == "games_timeout"
    assert attrs["upstream_partial"] is True
    assert attrs["scraped_event_count"] == 1
    assert attrs["event_window_count"] == 1


def test_current_and_next_event_sensors(mock_hass):
    coordinator = _coordinator(mock_hass)
    running = {"title": "Training", "event_type": "training", "start_time": "a"}
    upcoming = {"title": "Match", "event_type": "match", "end_time": "b"}
    coordinator.data = {"summary": {"current_event": running, "next_event": upcoming}}
    current = LISACurrentEventSensor(coordinator, _config_entry())
    upcoming_sensor = LISANextEventSensor(coordinator, _config_entry())

    assert current.native_value == "Training"
    assert current.extra_state_attributes["type"] == "training"
    assert upcoming_sensor.native_value == "Match"
    assert upcoming_sensor.extra_state_attributes["type"] == "match"


def test_current_and_next_event_sensors_report_none(mock_hass):
    coordinator = _coordinator(mock_hass)
    coordinator.data = {"summary": {"current_event": None, "next_event": None}}
    current = LISACurrentEventSensor(coordinator, _config_entry())
    upcoming_sensor = LISANextEventSensor(coordinator, _config_entry())

    assert current.native_value == "None"
    assert current.extra_state_attributes == {}
    assert upcoming_sensor.native_value == "None"

    coordinator.data = None
    assert current.native_value == "None"
