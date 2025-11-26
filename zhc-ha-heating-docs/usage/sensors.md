---
title: Available Sensors
tags: [usage, sensors]
---

# Available Sensors

The ZHC Heating Scheduler provides multiple sensors to monitor schedule and heating status.

## Regular Sensors

### sensor.zhc_next_heating_start

**Description**: When heating will next start

**State**: DateTime (timestamp)  
**Device Class**: `timestamp`  

**Attributes**:
- `event_count`: Number of events in next window
- `duration_minutes`: Duration of heating window

**Use cases**:
- Display on dashboard
- Trigger automations before heating starts
- Calculate time until heating

### sensor.zhc_next_heating_stop

**Description**: When heating will next stop

**State**: DateTime (timestamp)  
**Device Class**: `timestamp`  

**Use cases**:
- Know when heating ends
- Plan maintenance windows
- Energy monitoring

### sensor.zhc_current_event

**Description**: Details of current or next event

**State**: String (event name)  

**Attributes**:
- `event_count`: Number of events in window
- `events`: List of event details
- `window_start`: Window start time
- `window_end`: Window end time

### sensor.zhc_events_today

**Description**: Number of heating windows today

**State**: Integer  
**Unit**: count  

### sensor.zhc_heating_minutes_today

**Description**: Total heating minutes today

**State**: Integer  
**Unit**: minutes  

**Use cases**:
- Track daily energy use
- Cost estimation
- Usage statistics

### sensor.zhc_total_heating_windows

**Description**: Total scheduled heating windows

**State**: Integer  

**Attributes**:
- `heating_windows`: List of all windows

### sensor.zhc_last_schedule_update

**Description**: Last time schedule was refreshed

**State**: DateTime (timestamp)  
**Device Class**: `timestamp`  

**Attributes**:
- `last_error`: Any error from last update
- `event_count`: Number of events in schedule

## Binary Sensors

### binary_sensor.zhc_heating_active

**Description**: Whether heating should be active now

**State**: `on` / `off`  
**Device Class**: `heat`  

**Attributes**:
- `next_state_change`: When state will next change
- `next_state_heating`: What the next state will be
- `current_window_end`: End of current window (if active)

### binary_sensor.zhc_scheduler_enabled

**Description**: Whether the scheduler is enabled

**State**: `on` / `off`  

### binary_sensor.zhc_manual_override

**Description**: Whether manual override is active

**State**: `on` / `off`  

**Attributes**:
- `override_start`: Override start time
- `override_end`: Override end time

## Using Sensors in Automations

### Notify Before Heating Starts

```yaml
automation:
  - alias: "Heating starts soon"
    trigger:
      - platform: template
        value_template: >
          {{ (as_timestamp(states('sensor.zhc_next_heating_start')) - 
              as_timestamp(now())) < 3600 }}
    action:
      - service: notify.mobile_app
        data:
          message: "Club heating starts in 1 hour"
```

### Track Daily Usage

```yaml
automation:
  - alias: "Daily heating report"
    trigger:
      - platform: time
        at: "23:55:00"
    action:
      - service: notify.mobile_app
        data:
          message: >
            Today's heating: {{ states('sensor.zhc_heating_minutes_today') }} minutes
```

## Using Sensors in Templates

### Time Until Heating

```yaml
{% set start = as_timestamp(states('sensor.zhc_next_heating_start')) %}
{% set now = as_timestamp(now()) %}
{% set hours = ((start - now) / 3600) | round(1) %}
Heating starts in {{ hours }} hours
```

### Events Today

```yaml
{{ states('sensor.zhc_events_today') }} heating windows today
```

## Dashboard Examples

### Simple Card

```yaml
type: entities
entities:
  - sensor.zhc_current_event
  - sensor.zhc_next_heating_start
  - sensor.zhc_heating_minutes_today
```

### Detailed Card

```yaml
type: glance
entities:
  - entity: binary_sensor.zhc_heating_active
    name: Active
  - entity: sensor.zhc_events_today
    name: Today
  - entity: sensor.zhc_heating_minutes_today
    name: Minutes
```

## See Also

- [[services|Available Services]]
- [[dashboard-cards|Dashboard Cards]]
- [[automations|Automation Examples]]

---

**Related**: [[services|Services]], [[dashboard-cards|Dashboard Cards]]

