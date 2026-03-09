---
title: Configuration Examples
tags: [configuration, examples]
---

# Configuration Examples

Real-world configuration examples for common scenarios. All examples use the `lisa_scheduler` domain and current configuration field names.

---

## 1. Basic Single URL Setup

The minimal setup: one schedule URL, one trigger 120 minutes before each event.

```yaml
lisa_scheduler:
  schedule_url: "https://www.yourclub.nl/schedule"
  pre_event_triggers: "120"
```

Automation that listens to the window opening:

```yaml
automation:
  - alias: "Prepare for event"
    trigger:
      - platform: event
        event_type: lisa_scheduler_window_started
    action:
      - service: notify.mobile_app
        data:
          message: "Event window opened: {{ trigger.event.data.title }}"
```

---

## 2. Multiple Trigger Times with Different Automations

Fire separate automations at 120, 60, and 15 minutes before each event.

```yaml
lisa_scheduler:
  schedule_url: "https://www.yourclub.nl/schedule"
  pre_event_triggers: "120, 60, 15"
  scan_interval: 21600
```

Three automations, each filtering on `minutes_before`:

```yaml
automation:
  - alias: "Start heating 120 min before event"
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

  - alias: "Notify staff 60 min before event"
    trigger:
      - platform: event
        event_type: lisa_scheduler_pre_event_trigger
    condition:
      - condition: template
        value_template: "{{ trigger.event.data.minutes_before == 60 }}"
    action:
      - service: notify.staff_channel
        data:
          message: "Event starts in 1 hour."

  - alias: "Turn on lights 15 min before event"
    trigger:
      - platform: event
        event_type: lisa_scheduler_pre_event_trigger
    condition:
      - condition: template
        value_template: "{{ trigger.event.data.minutes_before == 15 }}"
    action:
      - service: light.turn_on
        target:
          entity_id: light.sports_hall
        data:
          brightness_pct: 100
```

---

## 3. Heating, Lighting, and Notification from One Schedule

A complete setup for a sports facility that needs heating, lighting, and staff notifications — all driven by a single schedule.

```yaml
lisa_scheduler:
  schedule_url: "https://www.yourclub.nl/schedule"
  logo_url: "https://www.yourclub.nl/logo.png"
  pre_event_triggers: "120, 45, 10"
  scan_interval: 21600
  timezone: "Europe/Amsterdam"
```

Automations:

```yaml
automation:
  # Heating: start 120 min before (large building needs time)
  - alias: "Heating on before event"
    trigger:
      - platform: event
        event_type: lisa_scheduler_pre_event_trigger
    condition:
      - condition: template
        value_template: "{{ trigger.event.data.minutes_before == 120 }}"
    action:
      - service: climate.set_hvac_mode
        target:
          entity_id: climate.sports_hall
        data:
          hvac_mode: heat
      - service: climate.set_temperature
        target:
          entity_id: climate.sports_hall
        data:
          temperature: 20

  # Staff notification: 45 min before
  - alias: "Staff notification before event"
    trigger:
      - platform: event
        event_type: lisa_scheduler_pre_event_trigger
    condition:
      - condition: template
        value_template: "{{ trigger.event.data.minutes_before == 45 }}"
    action:
      - service: notify.staff_group
        data:
          title: "Upcoming event"
          message: "{{ trigger.event.data.title }} starts in 45 minutes."

  # Lights: 10 min before
  - alias: "Lights on before event"
    trigger:
      - platform: event
        event_type: lisa_scheduler_pre_event_trigger
    condition:
      - condition: template
        value_template: "{{ trigger.event.data.minutes_before == 10 }}"
    action:
      - service: light.turn_on
        target:
          area_id: sports_hall

  # When the event ends: lights off, heating to setback
  - alias: "Event ended"
    trigger:
      - platform: event
        event_type: lisa_scheduler_event_ended
    action:
      - service: light.turn_off
        target:
          area_id: sports_hall
      - service: climate.set_temperature
        target:
          entity_id: climate.sports_hall
        data:
          temperature: 15
```

---

## 4. Multiple Scraper Sources (Training + Match Schedule)

When training and match schedules are on different pages, use `scraper_sources` in YAML to pull both.

```yaml
lisa_scheduler:
  pre_event_triggers: "120, 30"
  scan_interval: 21600
  timezone: "Europe/Amsterdam"
  date_format: "%d-%m-%Y"
  time_format: "%H:%M"

  scraper_sources:
    - url: "https://www.yourclub.nl/training"
      type: training
      method: html
      selectors:
        container: "div.training-item"
        date: "span.date"
        time: "span.time"
        title: "span.title"

    - url: "https://www.yourclub.nl/matches"
      type: match
      method: html
      selectors:
        container: "div.match-item"
        date: "span.match-date"
        time: "span.match-time"
        title: "span.match-title"
```

When `scraper_sources` is present, `schedule_url` is not required — the scraper uses the sources list instead.

You can also mix methods (HTML, API, iCal) across sources:

```yaml
lisa_scheduler:
  pre_event_triggers: "120, 30"

  scraper_sources:
    # HTML page for training
    - url: "https://www.yourclub.nl/training"
      type: training
      method: html
      selectors:
        container: "div.event"
        date: "span.date"
        time: "span.time"

    # iCal feed for matches
    - url: "https://calendar.yourclub.nl/matches.ics"
      type: match
      method: ical

    # JSON API for tournaments
    - url: "https://api.yourclub.nl/events"
      type: match
      method: api
      api_headers:
        Authorization: "Bearer YOUR_TOKEN"
        Accept: "application/json"
```

---

## 5. Dry Run Testing Configuration

Use `dry_run: true` when setting up the integration for the first time. The scheduler fetches the schedule and logs what events it would fire, without actually firing them on the HA bus. This lets you verify timing before connecting real automations.

```yaml
lisa_scheduler:
  schedule_url: "https://www.yourclub.nl/schedule"
  pre_event_triggers: "120, 30"
  dry_run: true
  scan_interval: 600  # poll every 10 minutes during testing
```

Check the Home Assistant log (Settings → System → Logs) for lines prefixed with `[DRY RUN]` to see which events would have fired and when.

Once you are satisfied with the timing, set `dry_run: false` (or remove the line) and reload the integration.

---

## Date Format Reference

If the scraper cannot parse dates automatically, add explicit format strings:

```yaml
# European: 31-12-2024
date_format: "%d-%m-%Y"
time_format: "%H:%M"

# US: 12-31-2024
date_format: "%m-%d-%Y"
time_format: "%I:%M %p"

# ISO: 2024-12-31
date_format: "%Y-%m-%d"
time_format: "%H:%M"
```

---

## See Also

- [Basic Settings](basic-settings)
- [Advanced Settings](advanced-settings)
- [Timing Optimization](timing-optimization)
- [Scraper Configuration](../scraper/configuring-scraper)
- [Troubleshooting](../troubleshooting/common-issues)

---

**Need help?** Check [Common Issues](../troubleshooting/common-issues) or ask on the [Home Assistant community forum](https://community.home-assistant.io/).
