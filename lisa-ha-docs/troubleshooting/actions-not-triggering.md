---
title: Actions Not Triggering
tags: [troubleshooting, automations, events]
---

# Actions Not Triggering

Use this guide when LISA Scheduler appears to be working (sensors update, binary sensors change state) but your automations or other actions are not running.

LISA Scheduler fires HA bus events — it does not control devices directly. Your automations are responsible for listening to those events and taking action. This guide walks through every layer of that chain.

---

## 1. Quick Checks

Before diving deep, verify these basics:

- **Is the scheduler enabled?** Check `binary_sensor.lisa_scheduler_enabled`. If it is `off`, call `lisa_scheduler.enable`.
- **Is dry run mode off?** Go to Settings → Devices & Services → LISA Scheduler → Configure and confirm "Dry run mode" is unchecked. When dry run is on, no HA events are fired.
- **Is there an active or upcoming event window?** Check `binary_sensor.lisa_window_active` and `sensor.lisa_next_window_start`. If there are no upcoming events, the scheduler has nothing to fire.
- **Is there a manual override active?** Check `binary_sensor.lisa_manual_override_active`. An active override may suppress normal transitions depending on your automation logic.

---

## 2. Verify Events Are Firing

Confirm that LISA Scheduler is actually dispatching HA bus events:

1. Go to **Developer Tools** → **Events**
2. In the "Listen to events" field, enter `lisa_scheduler_window_started` and click **Start listening**
3. Simulate a window start by calling the override service:
   - Go to **Developer Tools** → **Services**
   - Service: `lisa_scheduler.set_override`
   - Call it (this forces a window active state)
4. Watch the Events panel — you should see a `lisa_scheduler_window_started` event appear with a payload containing the event window details

If the event does not appear, the problem is in the scheduler itself. Enable debug logging (see [Section 6](#6-debug-checklist)) and look for errors.

If the event does appear, the scheduler is working. Continue to the next section to debug the automation.

---

## 3. Automation Not Triggering

If events are firing but your automation does not run:

### Check the trigger event_type

The automation trigger must match the event name exactly. Common mistakes:

```yaml
# Correct
trigger:
  - platform: event
    event_type: lisa_scheduler_window_started

# Wrong — old domain name
trigger:
  - platform: event
    event_type: zhc_scheduler_window_started

# Wrong — typo
trigger:
  - platform: event
    event_type: lisa_scheduler_window_start
```

Available event names:
- `lisa_scheduler_window_started`
- `lisa_scheduler_window_ended`
- `lisa_scheduler_event_started`
- `lisa_scheduler_event_ended`
- `lisa_scheduler_pre_event_trigger`

### Check the automation is enabled

In **Settings** → **Automations**, find your automation and confirm it is enabled (toggle is on).

### Check conditions

If the automation has conditions, they may be preventing it from running even when the trigger fires. Temporarily remove or bypass conditions to test the trigger in isolation.

### Check automation traces

1. Go to **Settings** → **Automations**
2. Click on your automation
3. Click **Traces** (top right)
4. Find the most recent trace and expand it

The trace shows exactly which trigger fired, whether conditions passed, and which actions ran. This is the fastest way to pinpoint where the chain breaks.

---

## 4. Pre-Event Trigger Not Firing

The `lisa_scheduler_pre_event_trigger` event includes a `minutes_before` value in its payload (e.g. `{"minutes_before": 30}`). If this event is not firing or your automation is not responding to it:

### Verify pre_event_triggers is configured

In the integration options, `pre_event_triggers` must be set. Example: `"120, 30"`. If this field is empty, no pre-event trigger events will ever fire.

### Check the automation uses minutes_before correctly

If you have one automation for all pre-event triggers, use a condition to distinguish them:

```yaml
trigger:
  - platform: event
    event_type: lisa_scheduler_pre_event_trigger
condition:
  - condition: template
    value_template: "{{ trigger.event.data.minutes_before == 30 }}"
action:
  - ...
```

### Verify the trigger time hasn't already passed

Pre-event triggers fire once per window, at the calculated offset before event start. If the scheduler starts (or restarts) after the trigger time has already passed, the trigger will not fire for that event. Check `sensor.lisa_next_event_start` and compare it to the configured offsets.

### Check _fired_triggers in dry run logs

Enable dry run mode temporarily and enable debug logging. Look for log lines containing `_fire_pre_event_triggers`. These will show which trigger offsets were evaluated and whether they were already considered fired.

---

## 5. Service Call Issues

To manually simulate events from Developer Tools:

### Simulate a window using set_override

1. **Developer Tools** → **Services**
2. Service: `lisa_scheduler.set_override`
3. Click **Call Service**

This forces the scheduler into an active window state and fires `lisa_scheduler_window_started`. Use this to test automations without waiting for a real event.

### Clear the override

Service: `lisa_scheduler.clear_override`

This returns the scheduler to its normal state and fires `lisa_scheduler_window_ended` if a window was active.

### Other useful services

| Service | Purpose |
|---|---|
| `lisa_scheduler.refresh_schedule` | Force a schedule fetch immediately |
| `lisa_scheduler.enable` | Re-enable the scheduler if disabled |
| `lisa_scheduler.disable` | Disable the scheduler (suppresses all events) |

---

## 6. Debug Checklist

Work through these steps in order:

1. Confirm `binary_sensor.lisa_scheduler_enabled` is `on`
2. Confirm dry run mode is **off** in integration options
3. Confirm `sensor.lisa_next_window_start` shows an upcoming window
4. Open Developer Tools → Events, listen for `lisa_scheduler_window_started`
5. Call `lisa_scheduler.set_override` and confirm the event appears in the listener
6. If the event appears: open your automation trace and identify where it stops
7. If the event does not appear: enable debug logging and check for errors
8. For pre-event triggers specifically: confirm `pre_event_triggers` is non-empty in config and check that the `minutes_before` payload value matches your automation condition

### Enable debug logging

```yaml
logger:
  logs:
    custom_components.lisa_scheduler: debug
```

Apply via Developer Tools → YAML → Reload Logger Configuration, or restart Home Assistant.

---

## See Also

- [[common-issues|Common Issues]]
- [[debugging|Debug Logging]]
- [[no-events-found|No Events Found]]

---

**Difficulty**: Intermediate
**Time needed**: 15–30 minutes
