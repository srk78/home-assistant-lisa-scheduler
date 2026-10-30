---
title: Configuration Examples
tags: [configuration, examples]
---

# Configuration Examples

## Club-Venue Operator Setup

```yaml
lisa_scheduler:
  api_url: "https://schedule.example.com"
  include_external_events: false
  pre_event_triggers: [120, 30]
  scan_interval: 600
  dry_run: false
```

## Include External Events

```yaml
lisa_scheduler:
  api_url: "https://schedule.example.com/v1/events"
  include_external_events: true
  pre_event_triggers: [90, 15]
  scan_interval: 600
```

## Day-Boundary Operations

```yaml
lisa_scheduler:
  api_url: "https://schedule.example.com"
  pre_event_triggers: [120]
  pre_first_event_triggers: [60, 15]
  pre_last_event_end_triggers: [30]
  post_last_event_triggers: [15]
```

These settings add bus events around the first and last event of each day; they do not imply a particular device action.

## Safe Commissioning

```yaml
lisa_scheduler:
  api_url: "http://192.168.1.20:3000"
  scan_interval: 600
  dry_run: true
```

Use HTTP only on a trusted private network. Prefer the Caddy HTTPS endpoint for normal operation.

## Example Automation

```yaml
automation:
  - alias: "LISA: prepare clubhouse"
    trigger:
      - platform: event
        event_type: lisa_scheduler_window_started
    condition:
      - condition: state
        entity_id: binary_sensor.lisa_scheduler_enabled
        state: "on"
    action:
      - service: light.turn_on
        target:
          entity_id: light.clubhouse
```

Heating, lighting, displays, and notifications are examples of automation actions. They are not integration configuration.

See [[api-connection|API Connection]], [[basic-settings|Basic Settings]], and [[../usage/automations|Automations]].
