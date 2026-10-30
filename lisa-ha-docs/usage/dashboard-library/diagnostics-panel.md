---
title: Diagnostics Panel
tags: [usage, dashboards, panels]
---

# Diagnostics Panel

Use this panel when the schedule looks wrong, automations did not fire, or operators need to know whether the API snapshot is healthy.

## Native HA Version

```yaml
type: entities
title: LISA Scheduler Diagnostics
show_header_toggle: false
entities:
  - entity: sensor.lisa_scheduler_last_schedule_update
    name: Last successful update
  - entity: sensor.lisa_scheduler_last_schedule_update
    type: attribute
    attribute: last_refresh_attempt
    name: Last refresh attempt
  - entity: sensor.lisa_scheduler_last_schedule_update
    type: attribute
    attribute: last_refresh_failed
    name: Last refresh failed
  - entity: sensor.lisa_scheduler_last_schedule_update
    type: attribute
    attribute: schedule_stale
    name: Schedule stale
  - entity: sensor.lisa_scheduler_last_schedule_update
    type: attribute
    attribute: upstream_partial
    name: Upstream partial
  - entity: sensor.lisa_scheduler_last_schedule_update
    type: attribute
    attribute: upstream_error_category
    name: Upstream error
  - entity: sensor.lisa_scheduler_last_schedule_update
    type: attribute
    attribute: last_api_fetch_success
    name: Last API response
  - entity: sensor.lisa_scheduler_last_schedule_update
    type: attribute
    attribute: last_error
    name: Last error
  - entity: sensor.lisa_scheduler_total_event_windows
    name: Loaded windows
  - entity: sensor.lisa_scheduler_events_today
    name: Events today
```

## Enhanced Version

Prerequisites: button-card.

```yaml
type: grid
title: Scheduler Health
columns: 2
square: false
cards:
  - type: custom:button-card
    entity: sensor.lisa_scheduler_last_schedule_update
    name: Schedule stale
    icon: mdi:alert-circle
    show_state: false
    state:
      - operator: template
        value: >
          [[[
            return entity.attributes.schedule_stale === true;
          ]]]
        color: red
      - operator: default
        color: green
    label: >
      [[[
        return entity.attributes.schedule_stale ? 'Check API' : 'Fresh';
      ]]]
    show_label: true
  - type: custom:button-card
    entity: sensor.lisa_scheduler_last_schedule_update
    name: Last refresh
    icon: mdi:update
    show_state: true
    label: >
      [[[
        return entity.attributes.last_error || 'No error';
      ]]]
    show_label: true
  - type: custom:button-card
    entity: sensor.lisa_scheduler_total_event_windows
    name: Loaded windows
    icon: mdi:calendar-multiselect
    show_state: true
  - type: custom:button-card
    entity: sensor.lisa_scheduler_events_today
    name: Events today
    icon: mdi:calendar-today
    show_state: true
```

## Operator Notes

- Add this panel to a staff-only view.
- Use it with [[../services|Available Services]] when operators need to force a refresh.
- If `schedule_stale` is true, refresh once and then inspect logs if the error remains.
