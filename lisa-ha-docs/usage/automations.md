---
title: Automation Examples
tags: [usage, automations, events]
---

# Automation Examples

## Overview

LISA Scheduler does not control any devices directly. Instead, it fires Home Assistant bus events when schedule transitions occur. Your automations listen to those events and decide what to do: turn on heating, switch on lights, send a notification, or anything else HA supports.

This separation means you can run any action — or multiple unrelated actions — from the same schedule, without touching the integration configuration.

## The 5 Events and When They Fire

```
Schedule timeline:

  window_start          event_start              event_end / window_end
       |                     |                          |
       v                     v                          v
───────●─────────────────────●──────────────────────────●───────
       │                     │                          │
  [window_started]     [event_started]           [event_ended]
                                                 [window_ended]

  ← pre_event_trigger(120) ── pre_event_trigger(30) →
       │                         │
       │ fires when window opens  │ fires 30 min before event_start
       │ (if 120 is configured)   │ (if 30 is configured)
```

| Event | When it fires |
|---|---|
| `lisa_scheduler_window_started` | The pre-event window opens (`event_start - pre_event_minutes`) |
| `lisa_scheduler_pre_event_trigger` | A configured number of minutes before `event_start` (once per configured value) |
| `lisa_scheduler_event_started` | The actual event begins |
| `lisa_scheduler_event_ended` | The event ends |
| `lisa_scheduler_window_ended` | The window closes (same time as event end, fired after `event_ended`) |

All events carry a payload with the full window details. See [Accessing Event Payload Data](#accessing-event-payload-data) below.

## Basic Automation for Each Event

### 1. Window Opened — Start Pre-Heating

```yaml
automation:
  - alias: "LISA: window opened — start heating"
    trigger:
      - platform: event
        event_type: lisa_scheduler_window_started
    action:
      - service: climate.set_temperature
        target:
          entity_id: climate.clubhouse
        data:
          temperature: 18
          hvac_mode: heat
```

### 2. Event Started — Bring Lights to Full

```yaml
automation:
  - alias: "LISA: event started — full lights"
    trigger:
      - platform: event
        event_type: lisa_scheduler_event_started
    action:
      - service: light.turn_on
        target:
          entity_id: light.sports_hall
        data:
          brightness_pct: 100
```

### 3. Event Ended — Begin Cool-Down

```yaml
automation:
  - alias: "LISA: event ended — reduce heating"
    trigger:
      - platform: event
        event_type: lisa_scheduler_event_ended
    action:
      - service: climate.set_temperature
        target:
          entity_id: climate.clubhouse
        data:
          temperature: 15
```

### 4. Window Closed — Heating Off

```yaml
automation:
  - alias: "LISA: window closed — heating off"
    trigger:
      - platform: event
        event_type: lisa_scheduler_window_ended
    action:
      - service: climate.turn_off
        target:
          entity_id: climate.clubhouse
```

### 5. Pre-Event Trigger — Conditional on Minutes Before

The `lisa_scheduler_pre_event_trigger` event fires once for each value listed in `pre_event_triggers`. The payload always includes `minutes_before` so you can branch on it.

```yaml
automation:
  - alias: "LISA: pre-event trigger"
    trigger:
      - platform: event
        event_type: lisa_scheduler_pre_event_trigger
    action:
      - choose:
          - conditions:
              - condition: template
                value_template: "{{ trigger.event.data.minutes_before == 120 }}"
            sequence:
              - service: climate.set_temperature
                target:
                  entity_id: climate.clubhouse
                data:
                  temperature: 16
                  hvac_mode: heat
          - conditions:
              - condition: template
                value_template: "{{ trigger.event.data.minutes_before == 30 }}"
            sequence:
              - service: light.turn_on
                target:
                  entity_id: light.sports_hall
                data:
                  brightness_pct: 50
```

To make this work, configure `pre_event_triggers` in the integration:

```yaml
lisa_scheduler:
  pre_event_triggers: "120, 30"
```

## Using Pre-Event Triggers with Conditions

Pre-event triggers let you stagger actions across the lead-up to an event. A typical pattern:

- **120 minutes before**: start low heating
- **60 minutes before**: raise to target temperature
- **30 minutes before**: turn on lights at low brightness
- **event_started**: full brightness, confirm everything is on

```yaml
automation:
  - alias: "LISA: staged pre-event preparation"
    trigger:
      - platform: event
        event_type: lisa_scheduler_pre_event_trigger
    action:
      - choose:
          - conditions:
              - condition: template
                value_template: "{{ trigger.event.data.minutes_before == 120 }}"
            sequence:
              - service: climate.set_temperature
                target:
                  entity_id: climate.clubhouse
                data:
                  temperature: 16
                  hvac_mode: heat
              - service: notify.mobile_app_phone
                data:
                  message: "Heating started — event in 2 hours"

          - conditions:
              - condition: template
                value_template: "{{ trigger.event.data.minutes_before == 60 }}"
            sequence:
              - service: climate.set_temperature
                target:
                  entity_id: climate.clubhouse
                data:
                  temperature: 19

          - conditions:
              - condition: template
                value_template: "{{ trigger.event.data.minutes_before == 30 }}"
            sequence:
              - service: light.turn_on
                target:
                  entity_id: light.sports_hall
                data:
                  brightness_pct: 60
```

## Using Device Triggers (UI-Based Automations)

If you prefer building automations in the Home Assistant UI instead of YAML, LISA Scheduler registers device triggers that appear in the automation editor.

1. Go to **Settings → Automations & Scenes → Create Automation**.
2. Add a trigger, choose **Device**, and select the LISA Scheduler device.
3. Available triggers:
   - `pre_event_window_opened`
   - `pre_event_window_closed`
   - `event_started`
   - `event_ended`
   - `pre_event_trigger`

Device triggers map directly to the bus events described above. The UI approach is equivalent to writing the YAML trigger manually.

## Accessing Event Payload Data

All LISA Scheduler events carry a payload you can read in automation actions and templates via `trigger.event.data`.

**Payload fields** (all events except `pre_event_trigger`):

| Field | Type | Description |
|---|---|---|
| `window_start` | string (ISO datetime) | When the pre-event window opens |
| `event_start` | string (ISO datetime) | When the actual event begins |
| `window_end` | string (ISO datetime) | When the window closes |
| `pre_event_minutes` | integer | Configured lead-in minutes |
| `duration_minutes` | integer | Total window duration in minutes |
| `event_count` | integer | Number of events merged into this window |
| `events` | list | List of individual event dicts |

**Additional field for `lisa_scheduler_pre_event_trigger`**:

| Field | Type | Description |
|---|---|---|
| `minutes_before` | integer | Minutes before event start at which this trigger fired |

### Example: Use Payload Data in a Notification

```yaml
automation:
  - alias: "LISA: notify on window start"
    trigger:
      - platform: event
        event_type: lisa_scheduler_window_started
    action:
      - service: notify.mobile_app_phone
        data:
          title: "Event window opening"
          message: >
            {{ trigger.event.data.event_count }} event(s) starting at
            {{ trigger.event.data.event_start }}.
            Window open until {{ trigger.event.data.window_end }}.
```

### Example: Use Event Name from Payload

```yaml
action:
  - service: notify.mobile_app_phone
    data:
      message: >
        {% set ev = trigger.event.data.events %}
        {% if ev %}
          First event: {{ ev[0].title }}
        {% else %}
          Event window started
        {% endif %}
```

## Complete Multi-Action Example

This example shows a single automation that handles heating, lighting, and a notification all at once when a window opens.

```yaml
automation:
  - alias: "LISA: full pre-event sequence"
    trigger:
      - platform: event
        event_type: lisa_scheduler_window_started
    action:
      # Start heating
      - service: climate.set_temperature
        target:
          entity_id: climate.clubhouse
        data:
          temperature: 18
          hvac_mode: heat

      # Lights to low level for arrival
      - service: light.turn_on
        target:
          entity_id: light.entrance
        data:
          brightness_pct: 30

      # Send notification
      - service: notify.mobile_app_phone
        data:
          title: "Club event starting"
          message: >
            Pre-event window opened.
            {{ trigger.event.data.event_count }} event(s),
            window until {{ trigger.event.data.window_end }}.

  - alias: "LISA: event started — full brightness"
    trigger:
      - platform: event
        event_type: lisa_scheduler_event_started
    action:
      - service: light.turn_on
        target:
          entity_id: light.sports_hall
        data:
          brightness_pct: 100

  - alias: "LISA: window closed — reset everything"
    trigger:
      - platform: event
        event_type: lisa_scheduler_window_ended
    action:
      - service: climate.turn_off
        target:
          entity_id: climate.clubhouse
      - service: light.turn_off
        target:
          entity_id:
            - light.sports_hall
            - light.entrance
```

## See Also

- [[sensors|Available Sensors]] — sensor reference and dashboard examples
- [[services|Available Services]] — how to trigger schedule refreshes, enable/disable the scheduler, and set manual overrides
- [[../scraper/overview|Scraper Overview]] — how the integration fetches schedule data
