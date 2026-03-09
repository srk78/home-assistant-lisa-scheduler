---
title: Available Sensors
tags: [usage, sensors]
---

# Available Sensors

LISA Scheduler provides sensors and binary sensors to monitor schedule state. They are useful for dashboards and for building conditions in automations. For triggering automations on schedule transitions, prefer the HA bus events over polling sensor states — see [[automations|Automation Examples]].

## Regular Sensors

### sensor.lisa_next_window_start

**Description**: When the next pre-event window will open (i.e. `event_start - pre_event_minutes`)

**State**: DateTime (timestamp)
**Device Class**: `timestamp`

**Attributes**:
- `event_count`: Number of events in the next window
- `duration_minutes`: Duration of the window in minutes

**Use cases**:
- Display time-until countdown on a dashboard
- Condition checks in automations ("is the next window today?")

---

### sensor.lisa_next_window_end

**Description**: When the next window will close (equal to the event end time)

**State**: DateTime (timestamp)
**Device Class**: `timestamp`

**Use cases**:
- Know when the full window ends
- Plan maintenance windows around activity

---

### sensor.lisa_next_event_start

**Description**: When the actual event (not the pre-event window) begins

**State**: DateTime (timestamp)
**Device Class**: `timestamp`

**Use cases**:
- Display "event starts at" on a dashboard
- Differentiate pre-event prep time from the event itself

---

### sensor.lisa_current_event

**Description**: The name and details of the currently active event, or the next upcoming event when none is active

**State**: String (event name or description)

**Attributes**:
- `event_count`: Number of events grouped into this window
- `events`: List of individual event details
- `window_start`: Window start datetime
- `window_end`: Window end datetime

**Use cases**:
- Show what is happening (or coming up) on a dashboard card
- Use event name in notification messages via `state_attr('sensor.lisa_current_event', 'events')`

---

### sensor.lisa_events_today

**Description**: Number of event windows scheduled for today

**State**: Integer
**Unit**: count

---

### sensor.lisa_window_minutes_today

**Description**: Total number of scheduled window minutes for today across all windows

**State**: Integer
**Unit**: minutes

**Use cases**:
- Energy monitoring and cost estimation
- Daily usage statistics

---

### sensor.lisa_total_event_windows

**Description**: Total number of event windows in the loaded schedule

**State**: Integer

**Attributes**:
- `heating_windows`: List of all windows in the schedule

---

### sensor.lisa_last_schedule_update

**Description**: Timestamp of the most recent successful schedule fetch

**State**: DateTime (timestamp)
**Device Class**: `timestamp`

**Attributes**:
- `last_error`: Error message from the last failed update, if any
- `event_count`: Number of events parsed from the last fetch

**Use cases**:
- Alert when the schedule has not refreshed in too long
- Debug scraper issues

---

## Binary Sensors

### binary_sensor.lisa_window_active

**Description**: `on` when the current time falls inside a scheduled event window (including the pre-event period). `off` at all other times.

**State**: `on` / `off`

**Attributes**:
- `next_state_change`: When the state will next change
- `current_window_end`: End time of the active window (when `on`)

---

### binary_sensor.lisa_event_active

**Description**: `on` only during the actual event (after the pre-event window period ends). `off` during the lead-in and at all other times.

**State**: `on` / `off`

---

### binary_sensor.lisa_scheduler_enabled

**Description**: `on` when the scheduler is enabled and actively firing events. `off` when disabled via `lisa_scheduler.disable`.

**State**: `on` / `off`

---

### binary_sensor.lisa_manual_override_active

**Description**: `on` when a manual override window is active (set via `lisa_scheduler.set_override`).

**State**: `on` / `off`

**Attributes**:
- `override_start`: Override window start time
- `override_end`: Override window end time

---

## Using Sensors in Automations

For most use cases, listen to bus events instead of polling sensors. See [[automations|Automation Examples]] for event-based automation patterns.

Sensors are most useful as conditions — for example, skip an action if no events are scheduled today:

```yaml
automation:
  - alias: "Morning report"
    trigger:
      - platform: time
        at: "08:00:00"
    condition:
      - condition: numeric_state
        entity_id: sensor.lisa_events_today
        above: 0
    action:
      - service: notify.mobile_app
        data:
          message: >
            {{ states('sensor.lisa_events_today') }} event(s) today.
            First window opens at {{ states('sensor.lisa_next_window_start') }}.
```

### Daily Usage Report

```yaml
automation:
  - alias: "Daily schedule summary"
    trigger:
      - platform: time
        at: "23:55:00"
    action:
      - service: notify.mobile_app
        data:
          message: >
            Today had {{ states('sensor.lisa_events_today') }} event(s)
            with {{ states('sensor.lisa_window_minutes_today') }} scheduled window minutes.
```

---

## Using Sensors in Templates

### Time Until Next Window

```yaml
{% set start = as_timestamp(states('sensor.lisa_next_window_start')) %}
{% set diff = (start - as_timestamp(now())) / 3600 %}
Next window opens in {{ diff | round(1) }} hours
```

### Current Event Name

```yaml
{{ states('sensor.lisa_current_event') }}
```

---

## Dashboard Examples

### Simple Entities Card

```yaml
type: entities
entities:
  - sensor.lisa_current_event
  - sensor.lisa_next_window_start
  - sensor.lisa_window_minutes_today
  - binary_sensor.lisa_window_active
```

### Glance Card

```yaml
type: glance
entities:
  - entity: binary_sensor.lisa_window_active
    name: Window Active
  - entity: binary_sensor.lisa_event_active
    name: Event Active
  - entity: sensor.lisa_events_today
    name: Today
  - entity: sensor.lisa_window_minutes_today
    name: Minutes
```

### Entity Picture (Logo)

If you have configured `logo_url` in the integration settings, all entities will automatically display the club logo as their entity picture. This appears in entity cards, the more-info dialog, and the entity list.

No extra dashboard configuration is needed — the picture is set at the entity level and HA displays it automatically wherever entity pictures are shown.

---

## See Also

- [[automations|Automation Examples]]
- [[services|Available Services]]

---

**Related**: [[services|Services]], [[automations|Automations]]
