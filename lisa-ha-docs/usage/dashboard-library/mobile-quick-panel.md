---
title: Mobile Quick Panel
tags: [usage, dashboards, panels, mobile]
---

# Mobile Quick Panel

Use this for operators who need a compact phone view. It focuses on current state, the next event, and quick actions.

## Native HA Version

```yaml
type: vertical-stack
cards:
  - type: glance
    title: LISA Quick View
    columns: 2
    entities:
      - entity: binary_sensor.lisa_scheduler_window_active
        name: Window
      - entity: binary_sensor.lisa_scheduler_event_active
        name: Event
      - entity: binary_sensor.lisa_scheduler_enabled
        name: Enabled
      - entity: binary_sensor.lisa_scheduler_manual_override_active
        name: Override
  - type: entities
    show_header_toggle: false
    entities:
      - entity: sensor.lisa_scheduler_current_event
        name: Current or next
      - entity: sensor.lisa_scheduler_next_event_start
        name: Next event
        format: datetime
      - entity: sensor.lisa_scheduler_last_schedule_update
        name: Last update
  - type: horizontal-stack
    cards:
      - type: button
        name: Refresh
        icon: mdi:refresh
        tap_action:
          action: call-service
          service: lisa_scheduler.refresh_schedule
      - type: button
        name: Enable
        icon: mdi:play
        tap_action:
          action: call-service
          service: lisa_scheduler.enable
      - type: button
        name: Pause
        icon: mdi:pause
        tap_action:
          action: call-service
          service: lisa_scheduler.disable
```

## Enhanced Version

Prerequisites: Bubble Card.

```yaml
type: vertical-stack
cards:
  - type: custom:bubble-card
    card_type: button
    button_type: state
    entity: sensor.lisa_scheduler_current_event
    name: Current event
    icon: mdi:calendar-star
    sub_button:
      - entity: binary_sensor.lisa_scheduler_window_active
        name: Window
        show_state: true
      - entity: binary_sensor.lisa_scheduler_event_active
        name: Event
        show_state: true
  - type: custom:bubble-card
    card_type: button
    button_type: state
    entity: sensor.lisa_scheduler_next_event_start
    name: Next event
    icon: mdi:calendar-clock
  - type: custom:bubble-card
    card_type: sub-buttons
    hide_main_background: true
    sub_button:
      main: []
      bottom:
        - name: Refresh
          icon: mdi:refresh
          tap_action:
            action: call-service
            service: lisa_scheduler.refresh_schedule
        - name: Enable
          icon: mdi:play
          tap_action:
            action: call-service
            service: lisa_scheduler.enable
        - name: Pause
          icon: mdi:pause
          tap_action:
            action: call-service
            service: lisa_scheduler.disable
        - name: Clear
          icon: mdi:calendar-remove
          tap_action:
            action: call-service
            service: lisa_scheduler.clear_override
```

## Operator Notes

- Keep this as its own dashboard view for phones.
- Avoid long attribute lists; use the Diagnostics Panel when detail is needed.
