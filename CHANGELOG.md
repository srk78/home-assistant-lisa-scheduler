# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-03-06

### Changed
- Integration is now a **general-purpose event scheduler**. It no longer controls any device directly. Instead it fires Home Assistant bus events on schedule transitions so automations can trigger any action (heating, lighting, screens, etc.).
- `pre_heat_hours` (hours) replaced by `pre_event_minutes` (minutes, 0–1440, default 120)
- `HeatingWindow` / `HeatingScheduler` renamed to `EventWindow` / `EventScheduler`
- Config entry title changed from "LISA Scheduler" to "LISA Scheduler"

### Added
- Four HA bus events fired on transitions:
  - `lisa_scheduler_window_started` — pre-event window opens; payload contains full window/event data
  - `lisa_scheduler_window_ended` — window closes (after event ends)
  - `lisa_scheduler_event_started` — actual event begins (after lead time)
  - `lisa_scheduler_event_ended` — event ends
- New binary sensor `ZHC Event Active` — true only during actual event time, distinct from the pre-event lead time
- New sensor `ZHC Next Event Start` — timestamp when the next actual event begins
- `EventWindow.event_start` tracks the earliest event start within a merged window, enabling the `event_active` distinction

### Removed
- Direct climate device control (`climate.turn_on`, `climate.set_temperature`, `climate.turn_off`)
- `climate_entity` configuration field
- `target_temperature` configuration field
- `cool_down_minutes` configuration field
- Binary sensor `ZHC Heating Active` (replaced by `ZHC Window Active` and `ZHC Event Active`)
- Sensors `ZHC Next Heating Start` and `ZHC Next Heating Stop` (replaced by `ZHC Next Window Start`, `ZHC Next Window End`, `ZHC Next Event Start`)

### Fixed
- `manifest.json` `name` was not updated from "LISA Scheduler" to "LISA Scheduler"
- `manifest.json` `version` was not bumped from `0.1.0` to `0.2.0`
- `manifest.json` still declared `"dependencies": ["climate"]` after direct climate control was removed
- `ConfigurableScraper` produced timezone-aware datetimes while the rest of the codebase used naive datetimes, causing `TypeError` on comparison
- `aiohttp.ClientSession` was created in a synchronous `__init__`; integration now uses HA's shared session via `async_get_clientsession`
- YAML import flow made an HTTP request and checked entity state at HA startup, causing import to fail on slow-loading systems
- `async_step_import` called `async_set_unique_id` twice on the same flow instance
- `_parse_row_to_event` clobbered event type and title on every matching cell instead of first-match
- `icalendar` package was used but not declared in `manifest.json` or `requirements_dev.txt`
- `aiohttp` unpinned from `==3.9.1` to `>=3.9.1` to resolve conflicts with Python 3.14 and current `homeassistant` package
- Incorrect `aiohttp` context-manager mock in tests caused tests to pass without actually exercising the scraper

### Breaking Changes
Upgrading from 0.1.0 requires manual steps:
1. Delete existing config entry and re-add the integration (the `climate_entity` field no longer exists)
2. Delete orphaned unavailable entities from Settings → Entities (`zhc_heating_active`, `zhc_next_heating_start`, `zhc_next_heating_stop`, `zhc_heating_minutes_today`, `zhc_total_heating_windows`)
3. Update any automations to use the new HA bus events or binary sensor names

## [0.1.0] - 2024-11-24

### Added
- Initial release
- HTML schedule scraping with flexible parser
- Heating schedule calculation with pre-heat and cool-down times
- Automatic climate device control (Plugwise SA support)
- UI configuration flow
- YAML configuration support
- Multiple sensors for schedule information:
  - Next heating start/stop times
  - Current event details
  - Events today count
  - Heating minutes today
  - Total heating windows
  - Last schedule update
- Binary sensors:
  - Heating active status
  - Scheduler enabled status
  - Manual override status
- Services:
  - Refresh schedule
  - Enable/disable scheduler
  - Set/clear manual override
- Dry run mode for testing
- Manual override capability
- Comprehensive documentation
- Unit and integration tests

### Known Issues
- Generic HTML parser may not work with all websites (customization may be needed)
- No support for multiple climate zones in a single integration instance

## [0.3.0] - 2026-03-09

### Changed
- Integration renamed from **LISA Scheduler** to **LISA Scheduler**
- HA bus event names renamed from `zhc_scheduler_*` to `lisa_scheduler_*` (breaking: update existing automations)
- Entities are now grouped under a single **LISA Scheduler** device per config entry
- Entity names no longer carry a hardcoded "LISA " prefix; the device name provides context

### Added
- `device_trigger.py` exposes all four transition events as named device triggers in the automation editor:
  - "Pre-event window opened"
  - "Pre-event window closed"
  - "Event started"
  - "Event ended"

### Breaking Changes
Upgrading from 0.2.0 requires updating any automations that listen to the old `zhc_scheduler_*` event names.

## [Unreleased]

### Planned Features
- `async_migrate_entry` for seamless upgrade from 0.1.0 (auto-converts `pre_heat_hours` → `pre_event_minutes`, removes obsolete keys, renames stored config entry title to "LISA Scheduler")
- Calendar integration for viewing the event schedule
- Multiple scraper instances / zone support
- HACS integration

