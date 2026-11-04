# LISA Scheduler

LISA Scheduler is a Home Assistant custom integration that reads normalized event data from [`lisa-schedule-api`](https://github.com/stefan/lisa-schedule-api) and fires Home Assistant bus events when schedule windows and events start or end. It does not crawl club websites or control devices directly; automations decide what happens next.

## Quick Start

**[Complete Documentation](lisa-ha-docs/index.md)**

1. Deploy `lisa-schedule-api` and make its HTTPS endpoint reachable from Home Assistant.
2. Allow the Home Assistant host in the API's `ALLOWED_CIDRS` setting.
3. Install this integration through HACS or manually and restart Home Assistant.
4. Go to **Settings -> Devices & Services -> Add Integration** and select **LISA Scheduler**.
5. Enter the API base URL or full `/v1/events` URL.
6. Create automations that listen to the `lisa_scheduler_*` events.

See the [UI installation guide](lisa-ha-docs/quick-start/installation-ui.md) and [API connection guide](lisa-ha-docs/configuration/api-connection.md).

## Features

- One authoritative schedule source: `lisa-schedule-api`
- Club-venue events by default, with an option to include external venues
- Configurable pre-event and day-boundary trigger times
- Sensors and binary sensors for dashboards and automation conditions
- Upstream stale, partial, error, and source-health diagnostics
- Manual override and dry-run modes
- Cached schedule preservation during transient API failures

## Basic YAML Example

```yaml
lisa_scheduler:
  api_url: "https://schedule.example.com"
  include_external_events: false
  next_event_index: 0  # 0 = first upcoming event, 1 = second, ...
  panel_events: false  # optional extra sidebar panels: panel_matches, panel_trainings, panel_events
  include_club_events: true  # false: club events never open windows or fire events
  pre_event_triggers: [120, 30]
  scan_interval: 600
  dry_run: false
```

The URL may be the API base URL or the full `https://schedule.example.com/v1/events` endpoint. The integration normalizes it to `/v1/events`.

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
| [API Connection](lisa-ha-docs/configuration/api-connection.md) | Endpoint, access policy, and networking |
| [Configuration](lisa-ha-docs/configuration/basic-settings.md) | Settings and options |
| [Usage](lisa-ha-docs/usage/sensors.md) | Sensors, services, automations, and dashboards |
| [Troubleshooting](lisa-ha-docs/troubleshooting/common-issues.md) | Fix common problems |

## Runtime Model

Home Assistant polls the API snapshot every 10 minutes by default. The API synchronizes its upstream sources independently, normally every 30 minutes. Calling `lisa_scheduler.refresh_schedule` rereads the API snapshot; it does not start an upstream crawl.

Stale or partial API snapshots remain available and are marked in the Last Schedule Update sensor. Invalid or truncated responses never replace the last usable Home Assistant schedule.

## Requirements

- Home Assistant 2024.1.0+
- A reachable `lisa-schedule-api` instance

## License

MIT License - See [LICENSE](LICENSE) for details.
