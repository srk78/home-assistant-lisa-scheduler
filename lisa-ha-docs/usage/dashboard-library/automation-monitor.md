---
title: Automation Monitor Panel
tags: [usage, dashboards, panels, automations]
---

# Automation Monitor Panel

Use this panel to verify that scheduler state transitions happened when expected. It is useful during dry-run testing, commissioning, and after changing trigger lead times.

## Native HA Version

```yaml
type: vertical-stack
cards:
  - type: heading
    heading: Automation Monitor
    icon: mdi:chart-timeline-variant
  - type: history-graph
    title: Scheduler transitions
    hours_to_show: 24
    entities:
      - binary_sensor.lisa_scheduler_window_active
      - binary_sensor.lisa_scheduler_event_active
      - binary_sensor.lisa_scheduler_manual_override_active
  - type: entities
    title: Current timing
    show_header_toggle: false
    entities:
      - entity: sensor.lisa_scheduler_next_window_start
        name: Next window opens
        format: datetime
      - entity: sensor.lisa_scheduler_next_event_start
        name: Next event starts
        format: datetime
      - entity: sensor.lisa_scheduler_next_window_end
        name: Next window closes
        format: datetime
```

## Enhanced Version

Prerequisites: apexcharts-card.

```yaml
type: custom:apexcharts-card
header:
  show: true
  title: Scheduler Transition Monitor
  show_states: true
graph_span: 48h
now:
  show: true
  label: Now
yaxis:
  - min: 0
    max: 1
    decimals: 0
series:
  - entity: binary_sensor.lisa_scheduler_window_active
    name: Window active
    type: area
    transform: "return x === 'on' ? 1 : 0;"
    color: "#f59e0b"
  - entity: binary_sensor.lisa_scheduler_event_active
    name: Event active
    type: area
    transform: "return x === 'on' ? 1 : 0;"
    color: "#22c55e"
  - entity: binary_sensor.lisa_scheduler_manual_override_active
    name: Override
    type: line
    transform: "return x === 'on' ? 1 : 0;"
    color: "#ef4444"
```

## Event Listener Reminder

Use **Developer Tools -> Events** and listen for:

```yaml
lisa_scheduler_window_started
lisa_scheduler_window_ended
lisa_scheduler_event_started
lisa_scheduler_event_ended
lisa_scheduler_pre_event_trigger
```

## Operator Notes

- Use this panel while validating automations after changing `pre_event_triggers`.
- If history shows state changes but actions did not run, inspect the automation trigger rather than the scheduler.
