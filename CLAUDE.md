# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LISA Scheduler is a Home Assistant custom integration that scrapes a sports club's event schedule and fires HA bus events on transitions, so automations can trigger any action (heating, lighting, screens, etc.). It does not control devices directly.

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
2. Every `scan_interval` seconds (default 6h), it fetches events via a scraper
3. `EventScheduler` converts events into `EventWindow` objects: `window_start = event_start − pre_event_minutes`, `window_end = event_end`
4. Overlapping windows are merged
5. On each poll the coordinator compares new vs. previous `is_window_active` / `is_event_active` state and fires HA bus events on transitions
6. State is exposed via sensors and binary sensors that read from `coordinator.data`

**HA events fired** (listen to these in automations):
- `lisa_scheduler_window_started` — fires when the pre-event window opens; payload contains the full `EventWindow` dict
- `lisa_scheduler_window_ended` — fires when the window closes (after event ends)
- `lisa_scheduler_event_started` — fires when the actual event begins (after lead time)
- `lisa_scheduler_event_ended` — fires when the event ends

**Scraper hierarchy** (all in `custom_components/lisa_scheduler/`):
- `ScheduleScraper` — generic base scraper with HTML table/list/calendar fallback strategies
- `ConfigurableScraper(ScheduleScraper)` — config-driven scraper supporting multiple sources; methods: `html`, `api`, `ical`; uses CSS selectors defined in `scraper_sources` config
- `LISACustomScraper(ScheduleScraper)` — site-specific scraper that fetches from training and match URLs, tries embedded JSON → API endpoint detection → HTML fallback

The coordinator picks the scraper based on config: if `scraper_sources` is set, it uses `ConfigurableScraper`; otherwise falls back to `ScheduleScraper` with the basic `schedule_url`.

**Entities created**:
- Binary sensors: `Window Active` (true during entire window), `Event Active` (true only during actual event), `Scheduler Enabled`, `Manual Override Active`
- Sensors: `Next Window Start`, `Next Window End`, `Next Event Start`, `Current Event`, `Events Today`, `Window Minutes Today`, `Total Event Windows`, `Last Schedule Update`

## Key Configuration

- `pre_event_minutes` — minutes before event start to open the window (default: 120). Range 0–1440.
- `dry_run: true` — logs what transitions would fire without actually firing HA events. Use for testing.
- `scan_interval` — seconds between schedule fetches (default: 21600, range 600–86400)
- Default timezone: `Europe/Amsterdam` (Dutch sports club context)

All datetimes are kept as naive local datetimes throughout the codebase. `ConfigurableScraper` normalises any tz-aware datetimes (from API/iCal sources) to naive by converting to the configured timezone then stripping tzinfo. The base `ScheduleScraper` uses `python-dateutil` flexible parsing and is already naive.

## Adding a New Scraper

To add support for a new website, subclass `ScheduleScraper` and override `_parse_html()`, or use `ConfigurableScraper` with CSS selectors in the integration config. `LISACustomScraper` in `lisa_custom_scraper.py` is an example of a site-specific subclass.
