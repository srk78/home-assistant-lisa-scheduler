---
title: Manual Override Control Panel
tags: [usage, dashboards, panels]
---

# Manual Override Control Panel

Use this panel for quick operator actions: refresh the schedule, pause event firing, resume event firing, and inspect manual override state.

## Native HA Version

```yaml
type: vertical-stack
cards:
  - type: heading
    heading: Scheduler Controls
    icon: mdi:tune
  - type: entities
    show_header_toggle: false
    entities:
      - entity: binary_sensor.lisa_scheduler_enabled
        name: Scheduler enabled
      - entity: binary_sensor.lisa_scheduler_manual_override_active
        name: Manual override active
      - entity: button.lisa_scheduler_refresh_schedule
        name: Refresh schedule now
  - type: grid
    columns: 2
    square: false
    cards:
      - type: button
        name: Enable scheduler
        icon: mdi:play-circle
        tap_action:
          action: call-service
          service: lisa_scheduler.enable
      - type: button
        name: Disable scheduler
        icon: mdi:pause-circle
        tap_action:
          action: call-service
          service: lisa_scheduler.disable
      - type: button
        name: Clear override
        icon: mdi:calendar-remove
        tap_action:
          action: call-service
          service: lisa_scheduler.clear_override
      - type: button
        name: Refresh schedule
        icon: mdi:refresh
        tap_action:
          action: call-service
          service: lisa_scheduler.refresh_schedule
```

## Manual Override Script Helper

Home Assistant dashboards cannot prompt for datetime fields directly from a simple button. Create a script like this, then add it to the panel as a button:

```yaml
script:
  lisa_scheduler_override_2h:
    alias: LISA Scheduler Override - 2 hours
    sequence:
      - service: lisa_scheduler.set_override
        data:
          start_time: "{{ now().isoformat() }}"
          end_time: "{{ (now() + timedelta(hours=2)).isoformat() }}"
```

Dashboard button for that script:

```yaml
type: button
name: Override for 2 hours
icon: mdi:calendar-clock
tap_action:
  action: call-service
  service: script.lisa_scheduler_override_2h
```

## Enhanced Version

Prerequisites: Mushroom, Bubble Card.

```yaml
type: vertical-stack
cards:
  - type: custom:mushroom-title-card
    title: Scheduler Controls
    subtitle: Refresh, pause, and override
  - type: custom:mushroom-chips-card
    chips:
      - type: entity
        entity: binary_sensor.lisa_scheduler_enabled
        name: Enabled
        icon_color: green
      - type: entity
        entity: binary_sensor.lisa_scheduler_manual_override_active
        name: Override
        icon_color: red
      - type: action
        icon: mdi:refresh
        tap_action:
          action: call-service
          service: lisa_scheduler.refresh_schedule
  - type: custom:bubble-card
    card_type: button
    button_type: switch
    entity: binary_sensor.lisa_scheduler_enabled
    name: Scheduler enabled
    icon: mdi:calendar-check
    sub_button:
      - name: Enable
        icon: mdi:play
        tap_action:
          action: call-service
          service: lisa_scheduler.enable
      - name: Disable
        icon: mdi:pause
        tap_action:
          action: call-service
          service: lisa_scheduler.disable
      - name: Clear override
        icon: mdi:calendar-remove
        tap_action:
          action: call-service
          service: lisa_scheduler.clear_override
```

## Operator Notes

- Put destructive or disruptive controls lower on the dashboard than status cards.
- Use a script helper for common fixed override durations such as 30 minutes, 2 hours, or all evening.
