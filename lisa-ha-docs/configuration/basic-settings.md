---
title: Basic Settings
tags: [configuration, settings, basics]
---

# Basic Settings

Configure the essential settings for the LISA Scheduler integration.

## Overview

LISA Scheduler watches a sports club's schedule and fires Home Assistant bus events when schedule transitions occur. Your automations listen to those events and decide what to do — turn on heating, send a notification, dim the lights, or anything else.

Basic settings control:
- **Which schedule to fetch** — the URL of your club's schedule page
- **When to fire pre-event triggers** — how many minutes before each event to send alerts
- **How often to refresh** — how frequently to re-fetch the schedule

The integration does not control any devices directly. It only fires events.

## Configuration Methods

Settings can be configured via:
1. **UI** — Settings → Devices & Services → LISA Scheduler → Configure
2. **YAML** — `configuration.yaml` file

## Settings Reference

### Schedule URL

**Description**: The webpage containing your club's event schedule

**UI Field**: Schedule URL
**YAML Key**: `schedule_url`
**Type**: String (URL)
**Required**: Yes

```yaml
schedule_url: "https://www.yourclub.nl/schedule"
```

### Logo URL

**Description**: Optional URL to your club's logo image. Used for display in the Home Assistant device card.

**UI Field**: Logo URL
**YAML Key**: `logo_url`
**Type**: String (URL)
**Required**: No

```yaml
logo_url: "https://www.yourclub.nl/logo.png"
```

### Pre-event Triggers

**Description**: A comma-separated list of minutes before each event start at which to fire a `lisa_scheduler_pre_event_trigger` HA bus event. Each value in the list fires a separate event with a `minutes_before` payload indicating which trigger fired.

**UI Field**: Pre-event triggers (minutes, comma-separated)
**YAML Key**: `pre_event_triggers`
**Type**: String (comma-separated integers)
**Required**: No
**Default**: `"120"`

```yaml
pre_event_triggers: "120, 30"
```

#### How pre-event triggers work

When you provide `"120, 30"`, LISA Scheduler does two things:

1. **Opens the event window** 120 minutes before each event (the largest value). The `lisa_scheduler_window_started` event fires at this point.
2. **Fires `lisa_scheduler_pre_event_trigger`** at 120 minutes before the event, with `minutes_before: 120` in the event payload.
3. **Fires `lisa_scheduler_pre_event_trigger`** again at 30 minutes before the event, with `minutes_before: 30` in the event payload.

Your automations can listen to `lisa_scheduler_pre_event_trigger` and use the `minutes_before` value to decide what action to take:

```yaml
trigger:
  - platform: event
    event_type: lisa_scheduler_pre_event_trigger
condition:
  - condition: template
    value_template: "{{ trigger.event.data.minutes_before == 120 }}"
action:
  - service: climate.set_temperature
    target:
      entity_id: climate.sports_hall
    data:
      temperature: 20
```

This lets you use a single schedule to drive multiple independent automations — heating, lighting, notifications — each triggered at the right lead time.

#### Choosing trigger times

Different systems need different lead times:

| Use case | Suggested trigger time |
|---|---|
| Heating (large building) | 90–120 min |
| Heating (small building) | 30–60 min |
| Notifications to staff | 30–60 min |
| Lighting / screens | 5–15 min |

To cover all of these from one schedule: `pre_event_triggers: "120, 60, 15"`

### Scan Interval

**Description**: How often (in seconds) the scheduler fetches the schedule from the website.

**UI Field**: Scan interval (seconds)
**YAML Key**: `scan_interval`
**Type**: Integer (seconds)
**Default**: 21600 (6 hours)
**Range**: 600–86400

```yaml
scan_interval: 21600  # 6 hours
```

Recommendations:
- Static schedules: 43200 (12 hours)
- Normal club schedules: 21600 (6 hours)
- Frequently updated schedules: 3600 (1 hour)
- Testing: 600 (10 minutes)

### Enable / Disable

**Description**: Pause the scheduler without removing the integration.

**YAML Key**: `enabled`
**Type**: Boolean
**Default**: `true`

```yaml
enabled: true
```

You can also toggle the scheduler from the UI or using the `lisa_scheduler.enable` and `lisa_scheduler.disable` services.

### Dry Run Mode

**Description**: When enabled, the scheduler logs what events it would fire but does not actually fire them on the HA bus. Use this when setting up for the first time or when troubleshooting.

**YAML Key**: `dry_run`
**Type**: Boolean
**Default**: `false`

```yaml
dry_run: true
```

See [Testing with Dry Run](../quick-start/testing-dry-run) for details.

## Complete Examples

### UI Configuration

1. Settings → Devices & Services
2. LISA Scheduler → Configure
3. Fill in Schedule URL and Pre-event triggers
4. Click Submit

### YAML Configuration

Minimal setup:

```yaml
lisa_scheduler:
  schedule_url: "https://www.yourclub.nl/schedule"
  pre_event_triggers: "120"
```

Full setup with multiple trigger times:

```yaml
lisa_scheduler:
  schedule_url: "https://www.yourclub.nl/schedule"
  logo_url: "https://www.yourclub.nl/logo.png"
  pre_event_triggers: "120, 30"
  scan_interval: 21600
  enabled: true
  dry_run: false
```

## See Also

- [Advanced Settings](advanced-settings)
- [Timing Optimization](timing-optimization)
- [Configuration Examples](examples)
- [First Time Setup](../quick-start/first-time-setup)

---

**Difficulty**: Easy
**Next**: [Advanced Settings](advanced-settings)
