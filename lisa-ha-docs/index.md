---
title: LISA Scheduler Documentation
tags: [home, index]
---

# LISA Scheduler

LISA Scheduler reads normalized club events from `lisa-schedule-api` and fires Home Assistant bus events as schedule windows and events begin or end. The API is the sole schedule source. This integration does not crawl websites or control devices directly.

## Start Here

- [[quick-start/installation-ui|Installation via UI]]
- [[quick-start/installation-yaml|Installation via YAML]]
- [[configuration/api-connection|Schedule API Connection]]
- [[quick-start/first-time-setup|First Time Setup]]
- [[quick-start/testing-dry-run|Testing with Dry Run]]

## Configuration

- [[configuration/basic-settings|Basic Settings]]
- [[configuration/advanced-settings|Advanced Settings]]
- [[configuration/timing-optimization|Timing Optimization]]
- [[configuration/examples|Configuration Examples]]

## Usage

- [[usage/sensors|Sensors and Binary Sensors]]
- [[usage/services|Services]]
- [[usage/automations|Example Automations]]
- [[usage/dashboard-cards|Dashboard Cards and Panel Library]]

## Dashboard Library

- [[usage/dashboard-library/operator-overview|Operator Overview]]
- [[usage/dashboard-library/today-timeline|Today Timeline]]
- [[usage/dashboard-library/manual-override-control|Manual Override Control]]
- [[usage/dashboard-library/diagnostics-panel|Diagnostics Panel]]
- [[usage/dashboard-library/kiosk-public-display|Kiosk and Public Display]]
- [[usage/dashboard-library/mobile-quick-panel|Mobile Quick Panel]]
- [[usage/dashboard-library/automation-monitor|Automation Monitor]]
- [[usage/dashboard-library/enhanced-custom-dashboard|Enhanced Custom Dashboard]]

## Troubleshooting

- [[troubleshooting/common-issues|Common Issues]]
- [[troubleshooting/no-events-found|No Events Found]]
- [[troubleshooting/actions-not-triggering|Actions Not Triggering]]
- [[troubleshooting/debugging|Debug Logging]]

## How It Works

1. Every 10 minutes by default, Home Assistant requests the API snapshot for today through 14 days ahead.
2. Club-venue events are selected by default; external events can be enabled in options.
3. Each event becomes a window that starts at the largest configured pre-event trigger and ends when the event ends. Overlapping windows merge.
4. The coordinator checks state every minute and fires HA bus events on transitions and configured trigger times.
5. Upstream freshness and source health from the API are exposed through the Last Schedule Update sensor.

The API synchronizes its own upstream sources independently, normally every 30 minutes. A manual Home Assistant refresh rereads the snapshot and does not trigger that synchronization.

## Events

| Event | When it fires |
|-------|---------------|
| `lisa_scheduler_window_started` | The pre-event window opens |
| `lisa_scheduler_window_ended` | The event window closes |
| `lisa_scheduler_event_started` | An event begins |
| `lisa_scheduler_event_ended` | An event ends |
| `lisa_scheduler_pre_event_trigger` | A configured lead time is reached |
| `lisa_scheduler_first_event_started` | The first event of the day begins |
| `lisa_scheduler_last_event_ended` | The last event of the day ends |
| `lisa_scheduler_pre_first_event_trigger` | A configured time before the first event |
| `lisa_scheduler_pre_last_event_end_trigger` | A configured time before the last event ends |
| `lisa_scheduler_post_last_event_trigger` | A configured time after the last event ends |

Event payloads contain schedule-local event/window timestamps and API provenance fields such as source IDs, venue classification, and whether an end time was estimated.

## Services

| Service | Description |
|---------|-------------|
| `lisa_scheduler.refresh_schedule` | Reread the latest API snapshot |
| `lisa_scheduler.enable` | Enable event firing |
| `lisa_scheduler.disable` | Pause event firing |
| `lisa_scheduler.set_override` | Activate a manual window |
| `lisa_scheduler.clear_override` | Remove the manual override |

## Support

- [GitHub Issues](https://github.com/stefan/home-assistant-lisa-scheduler/issues)
- [Home Assistant Community](https://community.home-assistant.io/)

Start with [[quick-start/installation-ui|Installation via UI]] or open [[troubleshooting/common-issues|Common Issues]].
