---
title: Kiosk Public Display
tags: [usage, dashboards, panels, kiosk]
---

# Kiosk/Public Display

Use this for a clubhouse screen or wall tablet. It avoids controls and focuses on what visitors or staff need to see at a glance.

## Native HA Version

```yaml
type: vertical-stack
cards:
  - type: markdown
    title: Club Schedule
    content: |
      # {{ states('sensor.lisa_scheduler_current_event') }}

      **Next event:** {{ as_local(as_datetime(states('sensor.lisa_scheduler_next_event_start'))).strftime('%a %H:%M') if has_value('sensor.lisa_scheduler_next_event_start') else '–' }}

      **Window opens:** {{ as_local(as_datetime(states('sensor.lisa_scheduler_next_window_start'))).strftime('%a %H:%M') if has_value('sensor.lisa_scheduler_next_window_start') else '–' }}

      **Events today:** {{ states('sensor.lisa_scheduler_events_today') }}
  - type: glance
    show_name: true
    show_state: true
    entities:
      - entity: binary_sensor.lisa_scheduler_window_active
        name: Window
      - entity: binary_sensor.lisa_scheduler_event_active
        name: Event
      - entity: sensor.lisa_scheduler_window_minutes_today
        name: Minutes
```

## Enhanced Version

Prerequisites: Mushroom.

```yaml
type: vertical-stack
cards:
  - type: custom:mushroom-title-card
    title: "{{ states('sensor.lisa_scheduler_current_event') }}"
    subtitle: Club schedule
  - type: custom:mushroom-template-card
    primary: "Next event"
    secondary: "{{ as_local(as_datetime(states('sensor.lisa_scheduler_next_event_start'))).strftime('%a %H:%M') if has_value('sensor.lisa_scheduler_next_event_start') else '–' }}"
    icon: mdi:calendar-clock
    icon_color: blue
    layout: vertical
    fill_container: true
  - type: custom:mushroom-template-card
    primary: "Window status"
    secondary: >-
      {% if is_state('binary_sensor.lisa_scheduler_event_active', 'on') %}
        Event is active
      {% elif is_state('binary_sensor.lisa_scheduler_window_active', 'on') %}
        Preparation window is active
      {% else %}
        No active window
      {% endif %}
    icon: mdi:calendar-check
    icon_color: >-
      {% if is_state('binary_sensor.lisa_scheduler_event_active', 'on') %}
        green
      {% elif is_state('binary_sensor.lisa_scheduler_window_active', 'on') %}
        amber
      {% else %}
        grey
      {% endif %}
    layout: vertical
    fill_container: true
  - type: custom:mushroom-chips-card
    alignment: center
    chips:
      - type: entity
        entity: sensor.lisa_scheduler_events_today
        name: Events today
      - type: template
        icon: mdi:clock-start
        content: "Next window: {{ as_local(as_datetime(states('sensor.lisa_scheduler_next_window_start'))).strftime('%a %H:%M') if has_value('sensor.lisa_scheduler_next_window_start') else '–' }}"
```

## Operator Notes

- Use a separate HA dashboard with kiosk mode or browser restrictions if the display is public.
- Do not include enable, disable, refresh, or override controls on public screens.
