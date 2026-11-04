---
title: Enhanced Custom Dashboard
tags: [usage, dashboards, panels, custom-cards]
---

# Enhanced Custom Dashboard

This is the polished club-operator dashboard assembled from the library panels. It assumes you want a custom-card rich experience.

## Prerequisites

Install these through HACS:

- Mushroom
- Bubble Card
- button-card
- apexcharts-card

Optional:

- layout-card, if you want more control than HA Sections provides.

## Sections View Recipe

Create a new dashboard view with **Sections** layout, then add these cards in order.

### 1. Header And Status

```yaml
type: vertical-stack
cards:
  - type: custom:mushroom-title-card
    title: Club Operations
    subtitle: LISA Scheduler
  - type: custom:mushroom-template-card
    entity: sensor.lisa_scheduler_current_event
    primary: "{{ states('sensor.lisa_scheduler_current_event') }}"
    secondary: "Next: {{ as_local(as_datetime(states('sensor.lisa_scheduler_next_event_start'))).strftime('%a %H:%M') if has_value('sensor.lisa_scheduler_next_event_start') else '–' }}"
    icon: mdi:calendar-star
    icon_color: >-
      {% if is_state('binary_sensor.lisa_scheduler_event_active', 'on') %}
        green
      {% elif is_state('binary_sensor.lisa_scheduler_window_active', 'on') %}
        amber
      {% else %}
        blue
      {% endif %}
    fill_container: true
```

### 2. Operator Chips

```yaml
type: custom:mushroom-chips-card
chips:
  - type: entity
    entity: binary_sensor.lisa_scheduler_window_active
    name: Window
    icon_color: amber
  - type: entity
    entity: binary_sensor.lisa_scheduler_event_active
    name: Event
    icon_color: green
  - type: entity
    entity: binary_sensor.lisa_scheduler_enabled
    name: Enabled
    icon_color: blue
  - type: action
    icon: mdi:refresh
    tap_action:
      action: call-service
      service: lisa_scheduler.refresh_schedule
```

### 3. Today Metrics

```yaml
type: grid
columns: 2
square: false
cards:
  - type: custom:mushroom-entity-card
    entity: sensor.lisa_scheduler_events_today
    name: Events today
    icon: mdi:calendar-today
  - type: custom:mushroom-entity-card
    entity: sensor.lisa_scheduler_window_minutes_today
    name: Window minutes
    icon: mdi:timer
  - type: custom:mushroom-template-card
    primary: Window opens
    secondary: "{{ as_local(as_datetime(states('sensor.lisa_scheduler_next_window_start'))).strftime('%a %H:%M') if has_value('sensor.lisa_scheduler_next_window_start') else '–' }}"
    icon: mdi:clock-start
  - type: custom:mushroom-template-card
    primary: Window closes
    secondary: "{{ as_local(as_datetime(states('sensor.lisa_scheduler_next_window_end'))).strftime('%a %H:%M') if has_value('sensor.lisa_scheduler_next_window_end') else '–' }}"
    icon: mdi:clock-end
```

### 4. Health And Actions

```yaml
type: grid
columns: 2
square: false
cards:
  - type: custom:button-card
    entity: sensor.lisa_scheduler_last_schedule_update
    name: Schedule health
    icon: mdi:heart-pulse
    show_state: true
    label: >
      [[[
        return entity.attributes.last_error || 'No error';
      ]]]
    show_label: true
    state:
      - operator: template
        value: >
          [[[
            return entity.attributes.schedule_stale === true;
          ]]]
        color: red
      - operator: default
        color: green
  - type: custom:bubble-card
    card_type: button
    button_type: state
    entity: binary_sensor.lisa_scheduler_manual_override_active
    name: Override
    icon: mdi:calendar-clock
    sub_button:
      - name: Clear
        icon: mdi:calendar-remove
        tap_action:
          action: call-service
          service: lisa_scheduler.clear_override
      - name: Pause
        icon: mdi:pause
        tap_action:
          action: call-service
          service: lisa_scheduler.disable
      - name: Enable
        icon: mdi:play
        tap_action:
          action: call-service
          service: lisa_scheduler.enable
```

### 5. Activity Graph

```yaml
type: custom:apexcharts-card
header:
  show: true
  title: Activity
graph_span: 24h
now:
  show: true
series:
  - entity: binary_sensor.lisa_scheduler_window_active
    name: Window
    type: area
    transform: "return x === 'on' ? 1 : 0;"
  - entity: binary_sensor.lisa_scheduler_event_active
    name: Event
    type: area
    transform: "return x === 'on' ? 1 : 0;"
```

## Operator Notes

- Use this as the main staff dashboard.
- Add [[diagnostics-panel|Diagnostics Panel]] below it for deeper API troubleshooting.
- Use [[kiosk-public-display|Kiosk/Public Display]] instead for public screens.
