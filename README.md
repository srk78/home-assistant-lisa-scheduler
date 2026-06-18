# LISA Scheduler

LISA Scheduler is a Home Assistant custom integration that scrapes a sports club's event schedule and fires Home Assistant bus events on schedule transitions. It does not control devices directly; your automations decide what to do, such as heating, lighting, notifications, screens, or scripts.

## Quick Start

**-> [Complete Documentation](lisa-ha-docs/index.md) <-**

1. Install via HACS or manually.
2. Restart Home Assistant.
3. Go to Settings -> Devices & Services -> Add Integration.
4. Search for "LISA Scheduler".
5. Configure a schedule URL and trigger lead times.
6. Create automations that listen to the `lisa_scheduler_*` events.

**Detailed guide:** [Installation via UI](lisa-ha-docs/quick-start/installation-ui.md)

## Features

- Event-driven Home Assistant automations
- Configurable pre-event trigger times, such as `120, 30`
- Multiple schedule sources through CSS selectors, APIs, or iCal feeds
- Sensors and binary sensors for dashboards and conditions
- Manual override service for ad hoc activity windows
- Dry run mode for testing without firing HA events

## Basic YAML Example

```yaml
lisa_scheduler:
  schedule_url: "https://www.club.com/schedule"
  pre_event_triggers: [120, 30]
  scan_interval: 21600
  dry_run: false
```

Example automation:

```yaml
automation:
  - alias: "LISA: prepare clubhouse before event"
    trigger:
      - platform: event
        event_type: lisa_scheduler_pre_event_trigger
        event_data:
          minutes_before: 120
    action:
      - service: light.turn_on
        target:
          entity_id: light.clubhouse
```

## Documentation

| Section | Description |
|---------|-------------|
| [Getting Started](lisa-ha-docs/quick-start/installation-ui.md) | Installation and setup |
| [Configuration](lisa-ha-docs/configuration/basic-settings.md) | Settings and options |
| [Scraper Setup](lisa-ha-docs/scraper/configuring-scraper.md) | Configure schedule scraping |
| [Usage](lisa-ha-docs/usage/sensors.md) | Sensors, services, automations |
| [Troubleshooting](lisa-ha-docs/troubleshooting/common-issues.md) | Fix common problems |

## Requirements

- Home Assistant 2024.1.0+
- Python 3.11+

## License

MIT License - See [LICENSE](LICENSE) for details.
