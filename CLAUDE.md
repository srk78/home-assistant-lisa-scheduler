# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ZHC Heating Scheduler is a Home Assistant custom integration that automatically controls a heating device based on a sports club's schedule. It scrapes event schedules (training sessions, matches) and pre-heats the venue before events start.

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
pytest --cov=custom_components/zhc_heating_scheduler

# Lint
flake8 custom_components/
mypy custom_components/

# Format
black custom_components/ tests/
```

## Architecture

The integration follows the standard Home Assistant custom component pattern:

**Entry point** (`__init__.py`): Registers `CONFIG_SCHEMA` for optional YAML setup, sets up `ZHCHeatingCoordinator`, forwards to `sensor` and `binary_sensor` platforms, and registers 5 services (`refresh_schedule`, `enable`, `disable`, `set_override`, `clear_override`).

**Data flow**:
1. `ZHCHeatingCoordinator` (extends `DataUpdateCoordinator`) polls every 60 seconds
2. Every `scan_interval` seconds (default 6h), it fetches events via a scraper
3. `HeatingScheduler` converts events into `HeatingWindow` objects (pre-heat start = event start − `pre_heat_hours`, heating end = event end − `cool_down_minutes`)
4. Overlapping windows are merged
5. Coordinator calls HA climate services (`turn_on`, `set_temperature`, `turn_off`) when heating state changes
6. State is exposed via sensors and binary sensors that read from `coordinator.data`

**Scraper hierarchy** (all in `custom_components/zhc_heating_scheduler/`):
- `ScheduleScraper` — generic base scraper with HTML table/list/calendar fallback strategies
- `ConfigurableScraper(ScheduleScraper)` — config-driven scraper supporting multiple sources; methods: `html`, `api`, `ical`; uses CSS selectors defined in `scraper_sources` config
- `ZHCCustomScraper(ScheduleScraper)` — ZHC-specific scraper that fetches from training and match URLs, tries embedded JSON → API endpoint detection → HTML fallback

The coordinator picks the scraper based on config: if `scraper_sources` is set, it uses `ConfigurableScraper`; otherwise falls back to `ScheduleScraper` with the basic `schedule_url`.

**Entities created**:
- Binary sensors: `ZHC Heating Active`, `ZHC Scheduler Enabled`, `ZHC Manual Override Active`
- Sensors: `ZHC Next Heating Start`, `ZHC Next Heating Stop`, `ZHC Current Event`, `ZHC Events Today`, `ZHC Heating Minutes Today`, `ZHC Total Heating Windows`, `ZHC Last Schedule Update`

## Key Configuration

- `dry_run: true` — logs what heating actions would be taken without actually calling climate services. Use this for testing.
- `pre_heat_hours` — hours before event start to begin heating (default: 2)
- `cool_down_minutes` — minutes before event end to stop heating (default: 30)
- Default timezone: `Europe/Amsterdam` (Dutch sports club context)

The `ConfigurableScraper` uses `date_format` (`%d-%m-%Y`) and `time_format` (`%H:%M`) with `pytz` timezone localization. The base `ScheduleScraper` uses `python-dateutil` flexible parsing without timezone awareness — be mindful of this difference when events produce inconsistent datetime types.

## Adding a New Scraper

To add support for a new website, subclass `ScheduleScraper` and override `_parse_html()`, or use `ConfigurableScraper` with CSS selectors in the integration config. `ZHCCustomScraper` in `zhc_custom_scraper.py` is an example of a site-specific subclass.
