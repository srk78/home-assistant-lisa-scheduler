---
title: First Time Setup
tags: [quickstart, setup, configuration]
---

# First Time Setup

Complete these steps after installing the LISA Scheduler to confirm everything is working before you build automations on top of it.

## Prerequisites

- Integration installed (via [[installation-ui|UI]] or [[installation-yaml|YAML]])
- Schedule URL accessible from your Home Assistant host

## Step 1: Verify Integration Status

1. Go to **Settings** → **Devices & Services**
2. Find "LISA Scheduler" in the list
3. The status should show as "Configured"

## Step 2: Check Entities

Go to **Developer Tools** → **States** and search for `lisa_scheduler`. Confirm the following entities are present:

**Binary sensors:**
- `binary_sensor.lisa_scheduler_window_active` — true during the entire pre-event window
- `binary_sensor.lisa_scheduler_event_active` — true only while the actual event is running
- `binary_sensor.lisa_scheduler_enabled` — reflects the enabled/disabled toggle
- `binary_sensor.lisa_scheduler_manual_override_active` — true when a manual override is active

**Sensors:**
- `sensor.lisa_scheduler_next_window_start`
- `sensor.lisa_scheduler_next_window_end`
- `sensor.lisa_scheduler_next_event_start`
- `sensor.lisa_scheduler_current_event`
- `sensor.lisa_scheduler_events_today`
- `sensor.lisa_scheduler_window_minutes_today`
- `sensor.lisa_scheduler_total_event_windows`
- `sensor.lisa_scheduler_last_schedule_update`

If any entities are missing, restart Home Assistant and check the logs.

## Step 3: Fetch the Schedule

Trigger an immediate schedule refresh to confirm the scraper can reach the configured URL and parse events:

1. Go to **Developer Tools** → **Services**
2. Select `lisa_scheduler.refresh_schedule`
3. Click **Call Service**
4. Go to **Settings** → **System** → **Logs** and search for "lisa"
5. Look for a message like "Found X events"

If no events are found, see [[../troubleshooting/no-events-found|No Events Found Guide]].

## Step 4: Review Schedule Data

Check that the parsed data looks correct:

1. Go to **Developer Tools** → **States**
2. Find `sensor.lisa_scheduler_current_event` and inspect its state and attributes
3. Find `sensor.lisa_scheduler_next_window_start` and verify the time is reasonable given your `pre_event_triggers` configuration
4. Find `sensor.lisa_scheduler_events_today` to confirm event counts

## Step 5: Verify Events Fire on the Bus

The LISA Scheduler fires Home Assistant bus events on schedule transitions. Automations listen for these events to take action — the integration itself does not control any devices.

To confirm events reach the bus:

1. Go to **Developer Tools** → **Events**
2. In the **Listen to events** field, enter `lisa_scheduler_window_started`
3. Click **Start Listening**
4. Either wait for a transition to occur naturally, or simulate one immediately using the `set_override` service (see Step 6 below)
5. When the event fires, its full payload will appear in the panel — confirm the data looks correct

You can also listen to `lisa_scheduler_*` to capture all integration events at once.

The five events fired by the integration are:

| Event | When it fires |
|-------|---------------|
| `lisa_scheduler_window_started` | Pre-event window opens |
| `lisa_scheduler_window_ended` | Window closes (after event ends) |
| `lisa_scheduler_event_started` | Actual event begins |
| `lisa_scheduler_event_ended` | Actual event ends |
| `lisa_scheduler_pre_event_trigger` | Each configured pre-event trigger time; payload includes `minutes_before` |

## Step 6: Simulate a Transition with set_override

You do not need to wait for a real event to test your automations. Use `set_override` to open a window immediately:

1. Go to **Developer Tools** → **Services**
2. Select `lisa_scheduler.set_override`
3. Provide a start and end time that spans the current time, for example:

```yaml
service: lisa_scheduler.set_override
data:
  start_time: "{{ now().isoformat() }}"
  end_time: "{{ (now() + timedelta(hours=2)).isoformat() }}"
```

4. Click **Call Service**
5. Watch **Developer Tools** → **Events** (with the listener from Step 5 active) — `lisa_scheduler_window_started` should fire immediately
6. Check `binary_sensor.lisa_scheduler_window_active` — it should switch to ON
7. Check `binary_sensor.lisa_scheduler_manual_override_active` — it should also be ON

To end the simulation early:

```yaml
service: lisa_scheduler.clear_override
```

## Step 7: Create Your First Automation

Once you have confirmed events fire correctly, create an automation that reacts to them. The LISA Scheduler does not control devices directly — you decide what each event means for your setup.

**Minimal example — notification on window start:**

```yaml
automation:
  trigger:
    platform: event
    event_type: lisa_scheduler_window_started
  action:
    service: notify.notify
    data:
      message: "Pre-event window opened!"
```

**Example with event payload:**

```yaml
automation:
  alias: "Club schedule — window opened"
  trigger:
    platform: event
    event_type: lisa_scheduler_window_started
  action:
    service: notify.notify
    data:
      message: >
        Pre-event window opened.
        Event: {{ trigger.event.data.title | default('unknown') }}
```

**Example reacting to a specific pre-event trigger time:**

```yaml
automation:
  alias: "Club schedule — 30-minute warning"
  trigger:
    platform: event
    event_type: lisa_scheduler_pre_event_trigger
  condition:
    condition: template
    value_template: "{{ trigger.event.data.minutes_before == 30 }}"
  action:
    service: notify.notify
    data:
      message: "Event starts in 30 minutes."
```

See [[../usage/automations|Automations Guide]] for more examples.

## Step 8: Disable Dry Run Mode (When Ready)

With dry run mode enabled, the integration logs transitions but does not fire HA bus events. Once you are satisfied with the schedule parsing, disable dry run:

**Via UI:**
1. Settings → Devices & Services
2. Find LISA Scheduler → click **Configure**
3. Uncheck **Dry run mode**
4. Click **Submit**

**Via YAML:**
1. Change `dry_run: true` to `dry_run: false` in `configuration.yaml`
2. Reload or restart Home Assistant

The integration will now fire HA events on every real schedule transition.

## Setup Checklist

- [ ] Integration loaded, status shows "Configured"
- [ ] All entities present in Developer Tools → States
- [ ] Schedule refresh successful, events found
- [ ] Schedule data looks correct (correct times, event titles)
- [ ] Bus events confirmed via Developer Tools → Events listener
- [ ] Override simulation tested (set_override / clear_override)
- [ ] First automation created and tested
- [ ] Dry run disabled

## Troubleshooting

### No Entities Showing

Restart Home Assistant and check the logs for errors during startup.

### Events Not Found

See [[../troubleshooting/no-events-found|No Events Found Guide]].

### Bus Events Not Appearing

- Confirm dry run mode is disabled
- Confirm `binary_sensor.lisa_scheduler_enabled` is ON
- Verify there are upcoming events in the sensor states
- Check the event listener spelling in Developer Tools → Events

## Next Steps

1. **Fine-tune triggers** — adjust `pre_event_triggers` values in the integration configuration
2. **Add automations** — [[../usage/automations|Automation Examples]]
3. **Customize dashboard** — [[../usage/dashboard-cards|Dashboard Cards]]

## Getting Help

1. Check [[../troubleshooting/common-issues|Common Issues]]
2. Enable [[../troubleshooting/debugging|Debug Logging]]
3. Ask on the [Home Assistant Forum](https://community.home-assistant.io/)
4. Create a [GitHub Issue](https://github.com/stefan/lisa-scheduler/issues)

---

**Time needed**: 20–30 minutes
**Difficulty**: Easy
**Prerequisites**: Integration installed
**Next**: [[../usage/automations|Automations]]
