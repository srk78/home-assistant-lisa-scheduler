---
title: Timing Optimization
tags: [configuration, timing, optimization]
---

# Timing Optimization

Plan your pre-event trigger times to match the lead time each automation actually needs.

## The Core Idea

LISA Scheduler fires a `lisa_scheduler_pre_event_trigger` event for each value in your `pre_event_triggers` list. Each automation listens to that event and filters on the `minutes_before` payload value to react only at the right moment.

This means one schedule can drive many different automations, each with its own timing requirement:

| Automation | Typical lead time | Reason |
|---|---|---|
| Heating (large building) | 90–120 min | Thermal inertia — the building needs time to warm up |
| Heating (small building) | 30–60 min | Shorter warm-up time |
| Staff notification | 30–60 min | Time to travel or prepare |
| Lighting / screens | 5–15 min | Near-instant response |

## Configuring Multiple Trigger Times

Set `pre_event_triggers` to a comma-separated list of all the lead times you need:

```yaml
lisa_scheduler:
  pre_event_triggers: "120, 60, 15"
```

This fires three separate `lisa_scheduler_pre_event_trigger` events per event:
- 120 minutes before — the window opens at this point
- 60 minutes before
- 15 minutes before

Each automation checks `trigger.event.data.minutes_before` to decide whether to act.

## Writing Automations per Trigger Time

### Heating automation (120 min before)

```yaml
automation:
  - alias: "Turn on heating before event"
    trigger:
      - platform: event
        event_type: lisa_scheduler_pre_event_trigger
    condition:
      - condition: template
        value_template: "{{ trigger.event.data.minutes_before == 120 }}"
    action:
      - service: climate.set_temperature
        target:
          entity_id: climate.sports_hall
        data:
          temperature: 20
```

### Notification automation (60 min before)

```yaml
automation:
  - alias: "Notify staff before event"
    trigger:
      - platform: event
        event_type: lisa_scheduler_pre_event_trigger
    condition:
      - condition: template
        value_template: "{{ trigger.event.data.minutes_before == 60 }}"
    action:
      - service: notify.staff_channel
        data:
          message: "Event starting in 1 hour — building is warming up."
```

### Lighting automation (15 min before)

```yaml
automation:
  - alias: "Turn on lights before event"
    trigger:
      - platform: event
        event_type: lisa_scheduler_pre_event_trigger
    condition:
      - condition: template
        value_template: "{{ trigger.event.data.minutes_before == 15 }}"
    action:
      - service: light.turn_on
        target:
          entity_id: light.sports_hall
```

## Planning Your Trigger Times

### Step 1: List your automations

Write down every action you want to trigger and how much lead time each one needs. Group similar lead times together — there is no need to fire a separate trigger for 118 min and 120 min.

### Step 2: Set pre_event_triggers

Use the lead times from step 1. The largest value becomes the window open time.

Example for heating + notification + lighting:

```yaml
pre_event_triggers: "120, 60, 15"
```

### Step 3: Enable dry run and verify timing

Set `dry_run: true` and check the Home Assistant logs after a schedule fetch. The log will show which trigger events would fire and when.

```yaml
lisa_scheduler:
  schedule_url: "https://www.yourclub.nl/schedule"
  pre_event_triggers: "120, 60, 15"
  dry_run: true
  scan_interval: 600  # poll every 10 min during testing
```

### Step 4: Test with real automations

Disable dry run and monitor a live event. Check:
- Did heating reach the target temperature before the event started?
- Did notifications arrive on time?
- Did lights turn on at the right moment?

### Step 5: Adjust and iterate

If heating is not ready in time, increase the heating trigger time (e.g. from 120 to 150). If lights come on too early, decrease the lighting trigger time. Adjust one value at a time and observe one full event per change.

## Back-to-back Events

When two events overlap (or the gap between them is smaller than the window), LISA Scheduler merges the windows automatically. You will not receive a `window_ended` event between them, only a single `window_started` at the beginning and a single `window_ended` at the end.

## Testing Methodology

### Week 1: Baseline

- Use a single trigger time that covers your most important automation
- Enable `dry_run: true` and verify events fire at the right times in the log
- Disable dry run and observe the first live event

### Week 2: Add remaining trigger times

- Add the remaining values to `pre_event_triggers`
- Write and enable the remaining automations
- Observe several events and check each automation fires correctly

### Week 3: Fine-tune

- Adjust individual trigger times based on observed results
- Tighten or loosen lead times based on actual system response

## Monitoring

Relevant sensors and binary sensors to watch during testing:

- `binary_sensor.lisa_window_active` — true during the full pre-event window
- `binary_sensor.lisa_event_active` — true only during the actual event
- `sensor.lisa_next_window_start` — when the next window opens
- `sensor.lisa_next_event_start` — when the next event starts

Example history graph card:

```yaml
type: history-graph
title: Event Window
entities:
  - binary_sensor.lisa_window_active
  - binary_sensor.lisa_event_active
hours_to_show: 24
```

## See Also

- [Basic Settings](basic-settings)
- [Advanced Settings](advanced-settings)
- [Configuration Examples](examples)
- [Available Sensors](../usage/sensors)

---

**Time needed**: 1–3 weeks (testing period)
**Difficulty**: Intermediate
**Prerequisites**: Integration installed and running
