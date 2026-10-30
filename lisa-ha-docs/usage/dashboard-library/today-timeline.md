---
title: Today Timeline Panel
tags: [usage, dashboards, panels]
---

# Today Timeline Panel

Use this panel to show the shape of the day: how many event windows exist, when the next one starts, and how much scheduled activity remains visible to operators.

## Native HA Version

```yaml
type: vertical-stack
cards:
  - type: heading
    heading: Today Timeline
    icon: mdi:timeline-clock
  - type: entities
    show_header_toggle: false
    entities:
      - entity: sensor.lisa_scheduler_events_today
        name: Events today
      - entity: sensor.lisa_scheduler_window_minutes_today
        name: Scheduled window minutes
      - entity: sensor.lisa_scheduler_total_event_windows
        name: Loaded windows
      - entity: sensor.lisa_scheduler_next_window_start
        name: Next window opens
      - entity: sensor.lisa_scheduler_next_window_end
        name: Next window closes
  - type: history-graph
    title: Active state history
    hours_to_show: 12
    entities:
      - binary_sensor.lisa_scheduler_window_active
      - binary_sensor.lisa_scheduler_event_active
```

## Enhanced Version

Prerequisites: apexcharts-card.

```yaml
type: custom:apexcharts-card
header:
  show: true
  title: Scheduler Activity Today
  show_states: true
graph_span: 24h
span:
  start: day
now:
  show: true
  label: Now
series:
  - entity: binary_sensor.lisa_scheduler_window_active
    name: Window active
    type: column
    transform: "return x === 'on' ? 1 : 0;"
    color: "#f59e0b"
  - entity: binary_sensor.lisa_scheduler_event_active
    name: Event active
    type: column
    transform: "return x === 'on' ? 1 : 0;"
    color: "#22c55e"
```

## Attribute Inspection Card

Use this native card when an operator needs to inspect loaded window data without opening Developer Tools:

```yaml
type: entities
title: Loaded Schedule
show_header_toggle: false
entities:
  - entity: sensor.lisa_scheduler_total_event_windows
    name: Total windows
  - entity: sensor.lisa_scheduler_current_event
    type: attribute
    attribute: event_count
    name: Events in current/next window
  - entity: sensor.lisa_scheduler_last_schedule_update
    type: attribute
    attribute: schedule_stale
    name: Schedule stale
  - entity: sensor.lisa_scheduler_last_schedule_update
    type: attribute
    attribute: last_refresh_failed
    name: Last refresh failed
```

## Operator Notes

- Use this next to the overview panel for a tablet dashboard.
- For detailed historical analytics, use the Automation Monitor panel.
