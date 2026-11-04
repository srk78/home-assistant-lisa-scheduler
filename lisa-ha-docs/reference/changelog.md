---
title: Changelog
tags: [reference, changelog]
---

# Changelog

All notable changes to the LISA Scheduler integration.

## [Unreleased]

### Removed

- The optional LISA Matches, LISA Trainings and LISA Events sidebar panels and their `panel_matches`, `panel_trainings` and `panel_events` options (added in 0.9.0). The main **LISA Schedule** panel, with its All/Matches/Trainings/Events filters, covers the same ground.
- The `next_event_index` option and the `event_index` attribute of the **Next Event** sensor (added in 0.9.0). A single sensor can only show one event, so the option added nothing; the sensor always shows the next upcoming event. Remove these keys from YAML configuration if you set them.

### Fixed

- Reloading the integration (for example after changing options) no longer registers the panel's static files and websocket command a second time.

## [0.9.0] - 2026-11-04

### Added

- `next_event_index` option (default `0`): which upcoming event the **Next Event** sensor shows. `0` is the first upcoming event, `1` the second. The sensor also exposes `event_index`.
- Optional sidebar panels for a single type: **LISA Matches** (`panel_matches`), **LISA Trainings** (`panel_trainings`) and **LISA Events** (`panel_events`). All are off by default and can be switched on in the integration options.

## [0.8.2] - 2026-11-04

### Fixed

- **Events Today** counted merged scheduling windows, so back-to-back or overlapping events counted as one. It now counts every match, training and club event today, with `matches`, `trainings`, `club_events` and `events` attributes.

## [0.8.1] - 2026-11-04

### Changed

- Dashboard snippets show the exact time with minutes for Next Window Start, Next Window End and Next Event Start (entities cards use `format: datetime`; Mushroom, chip and Markdown cards use templates) instead of a relative time such as "in 3 hours" or a raw timestamp.

## [0.8.0] - 2026-11-04

### Added

- **Next Event** sensor: the title of the next event that has not started yet, or `None`.

### Fixed

- **Current Event** reported the next upcoming event (or one still in its lead time) when nothing was running. It now shows the event in progress and `None` otherwise; its attributes describe that event.

## [0.7.1] - 2026-11-03

### Added

- `include_club_events` option (default `true`). Set it to `false` to keep club events out of scheduling: they open no windows and fire no bus events, but are still listed in the sidebar panel.

## [0.7.0] - 2026-11-03

### Added

- Club events from the schedule API (`type: "event"`: clinics, team dinners, tournaments) are now scheduled like matches and trainings, and listed in the sidebar panel under a new **Events** filter. The `event_types` option of the `lisa_scheduler/upcoming_events` websocket command accepts `event`. Club events open event windows and fire the same bus events as matches and trainings; the `event_type` in the payload is `event`, so automations can tell them apart.

### Fixed

- A schedule API snapshot containing club events was rejected as a whole with `Unsupported event type: event`.

## [0.6.0] - 2026-10-31

### Added

- **LISA Schedule** sidebar panel listing all upcoming matches and training sessions, with All/Matches/Trainings filter tabs.
- `lisa_scheduler/upcoming_events` websocket command backing the panel.
- [[../usage/dashboard-library/upcoming-events|Upcoming Events]] dashboard card snippet.

## [0.5.0] - Unreleased

### Breaking Changes

- `lisa-schedule-api` is now the only schedule source. Direct HTML, configurable, and iCal source handling have been removed.
- `schedule_url` has been replaced by `api_url`; experimental v1 config entries are migrated to the normalized `/v1/events` URL.

### Added

- Club-venue filtering by default, with an option to include external events.
- ETag support, strict API contract validation, and API provenance in event payloads.
- Upstream stale, partial, error, record-count, and per-source health diagnostics.
- In-place API URL reconfiguration and a 10-minute default polling interval.

### Changed

- Cached schedules survive transient API failures and usable stale or partial snapshots remain available.
- The refresh service rereads the API snapshot and does not trigger upstream synchronization.
- Timestamp conversion uses the API-declared timezone.

## [0.4.0] - Unreleased

### Breaking Changes

- **Domain renamed** from `zhc_heating_scheduler` to `lisa_scheduler`. Any direct service calls (e.g. `zhc_heating_scheduler.refresh_schedule`) must be updated to use the new domain (e.g. `lisa_scheduler.refresh_schedule`).
- **`pre_event_minutes` removed** — replaced by `pre_event_triggers` (see below).

### Added

- **`pre_event_triggers` config field** — accepts a comma-separated list of lead times in minutes (e.g. `"120, 30"`), replacing the single `pre_event_minutes` field. Each value causes the integration to fire a `lisa_scheduler_pre_event_trigger` event at that many minutes before the event starts.
- **`lisa_scheduler_pre_event_trigger` HA event** — fires at each configured lead time. Payload includes `minutes_before: N` so automations can distinguish which trigger fired.
- **`logo_url` config field** — optional URL to a club logo image. When set, the image is shown as the entity picture on all integration entities.
- **Device triggers in HA UI** — the following device triggers are now available in the automation editor:
  - `pre_event_window_opened`
  - `pre_event_window_closed`
  - `event_started`
  - `event_ended`
  - `pre_event_trigger`

### Changed

- **Integration renamed** from "ZHC Heating Scheduler" to "LISA Scheduler" (domain: `lisa_scheduler`).
- **Architecture clarified** — the integration fires HA bus events and does not control any devices directly. Automations are responsible for all actions.

## [0.3.0] - Unreleased

### Added

- `lisa_scheduler_event_started` and `lisa_scheduler_event_ended` HA events — distinguish between the pre-event window and the actual event.
- **Event Active** binary sensor — true only while the actual event is in progress (as opposed to Window Active, which covers the full pre-event + event period).
- **Next Event Start** sensor — shows the start time of the next actual event.

### Changed

- Refactored from a heating-specific integration to a general-purpose event scheduler. The integration no longer references heating or climate control in any config or entity.
- HA event names updated to the `lisa_scheduler_*` prefix.

## [0.2.0] - 2024-11-26

### Added

- Configurable scraper — set up schedule sources via YAML or the UI without writing Python.
- Multiple source support — configure separate URLs for training and match schedules.
- CSS selector configuration — point the scraper at the right elements without code changes.
- API and iCal source types — built-in support alongside HTML scraping.
- Configuration validator — validates scraper config and surfaces helpful error messages.
- Documentation overhaul — reorganised into an Obsidian-style `lisa-ha-docs/` folder with a UI installation guide, scraper configuration guide, and cross-linked reference pages.

### Changed

- Coordinator updated to support the configurable scraper alongside the existing base scraper.
- Constants updated to include scraper configuration options.

### Technical

- New file: `configurable_scraper.py`
- New file: `scraper_config_validator.py`
- Updated: `coordinator.py`, `const.py`

## [0.1.0] - 2024-11-24

### Added — Initial Release

- Core Home Assistant custom component with config flow (UI) and YAML configuration support.
- Schedule scraping via generic HTML parser (BeautifulSoup4) with multiple parsing strategies.
- `EventScheduler` that converts scraped events into `EventWindow` objects and merges overlapping windows.
- Binary sensors: Window Active, Scheduler Enabled, Manual Override Active.
- Sensors: Next Window Start, Next Window End, Current Event, Events Today, Window Minutes Today, Total Event Windows, Last Schedule Update.
- Services: `refresh_schedule`, `enable`, `disable`, `set_override`, `clear_override`.
- Dry run mode for safe testing.
- Manual override capability.
- Unit tests for scraper, scheduler, and coordinator.

## Migration Guides

### Migrating from 0.3.0 to 0.4.0

**Domain change** — update any direct service calls in scripts or automations:

```yaml
# Before
service: zhc_heating_scheduler.refresh_schedule

# After
service: lisa_scheduler.refresh_schedule
```

**`pre_event_minutes` replaced by `pre_event_triggers`** — update your configuration:

```yaml
# Before
pre_event_minutes: 120

# After
pre_event_triggers: "120"

# Or with multiple lead times:
pre_event_triggers: "120, 30"
```

**Automation triggers** — if you are listening to `lisa_scheduler_pre_event_trigger`, add an `event_data` filter for `minutes_before` if you need to distinguish between lead times:

```yaml
trigger:
  - platform: event
    event_type: lisa_scheduler_pre_event_trigger
    event_data:
      minutes_before: 30
```

### Migrating from 0.2.0 to 0.3.0

**No breaking changes** to configuration or scraper setup. Add automations for the new `lisa_scheduler_event_started` and `lisa_scheduler_event_ended` events if you want finer-grained control over the actual event period.

### Migrating from pre-0.3.0 (ZHC Heating Scheduler) to 0.3.0+

If you were using event name triggers from versions before 0.3.0, update them to the `lisa_scheduler_*` prefix. Check [[../usage/automations|Example Automations]] for current event names.

## Version History

| Version | Date | Key Changes |
|---------|------|-------------|
| 0.9.0 | 2026-11-04 | Optional matches/trainings/events panels, `next_event_index` |
| 0.8.2 | 2026-11-04 | Events Today counts every event |
| 0.8.1 | 2026-11-04 | Dashboard snippets show exact times with minutes |
| 0.8.0 | 2026-11-04 | Current Event shows only the running event, Next Event sensor |
| 0.7.1 | 2026-11-03 | `include_club_events` option |
| 0.7.0 | 2026-11-03 | Club events from the schedule API |
| 0.6.0 | 2026-10-31 | Upcoming events sidebar panel |
| 0.5.0 | Unreleased | Sole schedule API source, health metadata, cached failure handling |
| 0.4.0 | Unreleased | Rename to LISA Scheduler, `pre_event_triggers`, `logo_url`, device triggers |
| 0.3.0 | Unreleased | General-purpose refactor, `event_started`/`event_ended` events, Event Active sensor |
| 0.2.0 | 2024-11-26 | Configurable scraper, documentation overhaul |
| 0.1.0 | 2024-11-24 | Initial release |

## Support

- **Issues:** [GitHub Issues](https://github.com/stefan/home-assistant-lisa-scheduler/issues)
- **Discussions:** [GitHub Discussions](https://github.com/stefan/home-assistant-lisa-scheduler/discussions)
- **Forum:** [Home Assistant Community](https://community.home-assistant.io/)

---

[[../index|Back to Documentation Home]]
