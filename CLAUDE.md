# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LISA Scheduler is a Home Assistant custom integration that reads normalized events from `lisa-schedule-api` and fires HA bus events on transitions. It does not crawl websites or control devices directly.

## Development Commands

```bash
# Install dependencies
pip install -r requirements_dev.txt

# Run all tests
pytest

# Run a single test file
pytest tests/test_scheduler.py

# Run a single test function
pytest tests/test_scheduler.py::test_function_name

# Run tests with coverage
pytest --cov=custom_components/lisa_scheduler

# Lint
flake8 custom_components/
mypy custom_components/

# Format
black custom_components/ tests/
```

## Architecture

The integration follows the standard Home Assistant custom component pattern:

**Entry point** (`__init__.py`): Registers `CONFIG_SCHEMA` for optional YAML setup, sets up `LISASchedulerCoordinator`, forwards to `sensor` and `binary_sensor` platforms, and registers 5 services (`refresh_schedule`, `enable`, `disable`, `set_override`, `clear_override`).

**Data flow**:
1. `LISASchedulerCoordinator` (extends `DataUpdateCoordinator`) polls every 60 seconds
2. Every `scan_interval` seconds (default 10m), it reads the API's persisted event snapshot
3. `EventScheduler` converts events into `EventWindow` objects: `window_start = event_start − pre_event_minutes`, `window_end = event_end`
4. Overlapping windows are merged
5. On each poll the coordinator compares new vs. previous `is_window_active` / `is_event_active` state and fires HA bus events on transitions
6. State is exposed via sensors and binary sensors that read from `coordinator.data`

**HA events fired** (listen to these in automations):
- `lisa_scheduler_window_started` — fires when the pre-event window opens; payload contains the full `EventWindow` dict
- `lisa_scheduler_window_ended` — fires when the window closes (after event ends)
- `lisa_scheduler_event_started` — fires when the actual event begins (after lead time)
- `lisa_scheduler_event_ended` — fires when the event ends

**Schedule source**:
- `LisaScheduleApiClient` is the only source implementation.
- It consumes `GET /v1/events`, validates the complete response, converts UTC timestamps to naive schedule-local datetimes, and retains API freshness metadata.
- There is no direct website fallback; crawling and persistence belong to `lisa-schedule-api`.

**Entities created**:
- Binary sensors: `Window Active` (true during entire window), `Event Active` (true only during actual event), `Scheduler Enabled`, `Manual Override Active`
- Sensors: `Next Window Start`, `Next Window End`, `Next Event Start`, `Current Event`, `Events Today`, `Window Minutes Today`, `Total Event Windows`, `Last Schedule Update`

## Key Configuration

- `api_url` — API base URL or full `/v1/events` endpoint.
- `include_external_events` — include events outside the club venue (default: false).
- `pre_event_triggers` — minutes before event start; the largest value opens the window (default: `[120]`). Range 0–1440.
- `dry_run: true` — logs what transitions would fire without actually firing HA events. Use for testing.
- `scan_interval` — seconds between API snapshot reads (default: 600, range 600–86400)
- Default timezone: `Europe/Amsterdam` (Dutch sports club context)

Internal event/window datetimes remain naive schedule-local values. The API client converts aware API timestamps using `meta.timezone`; timestamp sensors return aware values at the Home Assistant boundary.

## Changing Schedule Data

Add website adapters, venue rules, or normalization behavior to `lisa-schedule-api`. Keep this integration focused on the unified API contract and Home Assistant scheduling behavior.
