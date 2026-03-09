---
title: Changelog
tags: [reference, changelog]
---

# Changelog

All notable changes to the LISA Scheduler integration.

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
- Documentation overhaul — reorganised into an Obsidian-style `docs/` folder with a UI installation guide, scraper configuration guide, and cross-linked reference pages.

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
- Schedule scraping via generic HTML parser (BeautifulSoup4) with multiple parsing strategies and a ZHC custom scraper example.
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
