---
title: Operator Overview Panel
tags: [usage, dashboards, panels]
---

# Operator Overview Panel

Use this as the first panel on a facility manager or club-operator dashboard. It answers: what is active now, what happens next, and is the schedule healthy?

## Native HA Version

Works with built-in Home Assistant cards only.

```yaml
type: grid
title: Operator Overview
columns: 2
square: false
cards:
  - type: entity
    entity: sensor.lisa_scheduler_current_event
    name: Current or next event
    icon: mdi:calendar-star
  - type: glance
    title: State
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
    title: Next
    show_header_toggle: false
    entities:
      - entity: sensor.lisa_scheduler_next_window_start
        name: Window opens
        format: datetime
      - entity: sensor.lisa_scheduler_next_event_start
        name: Event starts
        format: datetime
      - entity: sensor.lisa_scheduler_next_window_end
        name: Window closes
        format: datetime
  - type: entities
    title: Today
    show_header_toggle: false
    entities:
      - entity: sensor.lisa_scheduler_events_today
        name: Events
      - entity: sensor.lisa_scheduler_window_minutes_today
        name: Window minutes
      - entity: sensor.lisa_scheduler_last_schedule_update
        name: Last update
```

## Enhanced Version

Prerequisites: Mushroom.

```yaml
type: vertical-stack
cards:
  - type: custom:mushroom-title-card
    title: Club Schedule
    subtitle: Operator overview
  - type: custom:mushroom-template-card
    primary: "{{ states('sensor.lisa_scheduler_current_event') }}"
    secondary: "Next event: {{ as_local(as_datetime(states('sensor.lisa_scheduler_next_event_start'))).strftime('%a %H:%M') if has_value('sensor.lisa_scheduler_next_event_start') else '–' }}"
    icon: mdi:calendar-star
    icon_color: >-
      {% if is_state('binary_sensor.lisa_scheduler_event_active', 'on') %}
        green
      {% elif is_state('binary_sensor.lisa_scheduler_window_active', 'on') %}
        amber
      {% else %}
        blue
      {% endif %}
    tap_action:
      action: more-info
    entity: sensor.lisa_scheduler_current_event
  - type: custom:mushroom-chips-card
    chips:
      - type: entity
        entity: binary_sensor.lisa_scheduler_window_active
        icon_color: amber
        content_info: name
        name: Window
      - type: entity
        entity: binary_sensor.lisa_scheduler_event_active
        icon_color: green
        content_info: name
        name: Event
      - type: entity
        entity: binary_sensor.lisa_scheduler_enabled
        icon_color: blue
        content_info: name
        name: Enabled
      - type: entity
        entity: binary_sensor.lisa_scheduler_manual_override_active
        icon_color: red
        content_info: name
        name: Override
  - type: grid
    columns: 2
    square: false
    cards:
      - type: custom:mushroom-template-card
        primary: Window opens
        secondary: "{{ as_local(as_datetime(states('sensor.lisa_scheduler_next_window_start'))).strftime('%a %H:%M') if has_value('sensor.lisa_scheduler_next_window_start') else '–' }}"
        icon: mdi:clock-start
      - type: custom:mushroom-template-card
        primary: Event starts
        secondary: "{{ as_local(as_datetime(states('sensor.lisa_scheduler_next_event_start'))).strftime('%a %H:%M') if has_value('sensor.lisa_scheduler_next_event_start') else '–' }}"
        icon: mdi:calendar-clock
      - type: custom:mushroom-entity-card
        entity: sensor.lisa_scheduler_events_today
        name: Events today
        icon: mdi:calendar-today
      - type: custom:mushroom-entity-card
        entity: sensor.lisa_scheduler_last_schedule_update
        name: Schedule health
        icon: mdi:update
```

## Operator Notes

- Put this panel at the top-left of a Sections dashboard.
- Add the diagnostics panel below it if schedule freshness matters during event days.
- Use the Kiosk/Public Display panel instead when controls should be hidden.
