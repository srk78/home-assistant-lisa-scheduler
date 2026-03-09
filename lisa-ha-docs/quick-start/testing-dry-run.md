---
title: Testing with Dry Run Mode
tags: [quickstart, testing, dry-run, safety]
---

# Testing with Dry Run Mode

Dry run mode lets you safely test LISA Scheduler without triggering any automations or affecting devices. All HA bus events are suppressed; the scheduler logs what it would fire instead.

## What is Dry Run Mode?

Dry run mode:

- Logs all decisions and state transitions
- Does not fire any HA bus events (`lisa_scheduler_*`)
- Allows full testing of schedule parsing, window calculations, and timing logic
- Can run safely alongside a live system

## Enabling Dry Run Mode

### Via UI

1. Go to **Settings** → **Devices & Services**
2. Find "LISA Scheduler"
3. Click **Configure**
4. Check **Dry run mode**
5. Click **Submit**

### Via YAML

```yaml
lisa_scheduler:
  dry_run: true
```

Restart Home Assistant after changing YAML.

## Testing Process

### Step 1: Enable Dry Run

Follow the steps above.

### Step 2: Force a Schedule Refresh

In **Developer Tools** → **Services**, call:

```yaml
service: lisa_scheduler.refresh_schedule
```

### Step 3: Check Logs

Go to **Settings** → **System** → **Logs** and search for `lisa_scheduler`. You should see:

```
INFO  [custom_components.lisa_scheduler] Fetching schedule from ...
INFO  [custom_components.lisa_scheduler] Found 12 events
INFO  [custom_components.lisa_scheduler] Calculated 7 event windows
```

### Step 4: Monitor Dry Run Messages

As window and event transitions would occur, the log will show lines like:

```
INFO  [custom_components.lisa_scheduler] DRY RUN: Would fire event lisa_scheduler_window_started
INFO  [custom_components.lisa_scheduler] DRY RUN: Would fire event lisa_scheduler_event_started
INFO  [custom_components.lisa_scheduler] DRY RUN: Would fire event lisa_scheduler_pre_event_trigger (minutes_before=30)
INFO  [custom_components.lisa_scheduler] DRY RUN: Would fire event lisa_scheduler_window_ended
```

No actual HA events are dispatched.

## What to Verify

### Schedule Parsing

- [ ] Events are found and count is non-zero
- [ ] Dates and times match the source website
- [ ] `sensor.lisa_next_event_start` shows a plausible upcoming time
- [ ] `sensor.lisa_current_event` updates correctly

### Event Windows

- [ ] `sensor.lisa_next_window_start` is `pre_event_minutes` before event start
- [ ] `sensor.lisa_next_window_end` matches event end
- [ ] Overlapping events are merged into a single window
- [ ] `sensor.lisa_total_event_windows` looks correct

### Timing Logic

- [ ] `binary_sensor.lisa_window_active` turns on at window start
- [ ] `binary_sensor.lisa_event_active` turns on at event start
- [ ] Both turn off at event end
- [ ] No unexpected state cycling

### Pre-Event Triggers

To test multiple pre-event triggers, set `pre_event_triggers` to `"120, 5"` in the config. In the dry run logs you should see two separate lines:

```
INFO  [custom_components.lisa_scheduler] DRY RUN: Would fire event lisa_scheduler_pre_event_trigger (minutes_before=120)
INFO  [custom_components.lisa_scheduler] DRY RUN: Would fire event lisa_scheduler_pre_event_trigger (minutes_before=5)
```

Verify both values appear and that the timestamps are correct relative to the event start.

## Example Test Scenarios

### Scenario 1: Single Event Window

Event: training at 18:00–20:00, `pre_event_minutes: 120`

**Expected behavior:**
- Window opens: 16:00 (fires `lisa_scheduler_window_started`)
- Event starts: 18:00 (fires `lisa_scheduler_event_started`)
- Event ends / window closes: 20:00 (fires `lisa_scheduler_event_ended`, then `lisa_scheduler_window_ended`)

In dry run, check that the log shows all four DRY RUN lines at the right times.

### Scenario 2: Overlapping Events

- Event 1: 14:00–16:00
- Event 2: 15:00–17:00

**Expected:** Windows merge into a single window. Only one `window_started` and one `window_ended` should appear in the logs.

### Scenario 3: Multiple Events Same Day

- Morning: 09:00–11:00
- Evening: 18:00–20:00

**Expected:** Two separate windows, with a gap between them. The log should show `window_started` and `window_ended` twice.

### Scenario 4: Testing Developer Tools → Events

You can listen for real events that would fire during normal (non-dry-run) operation:

1. **Developer Tools** → **Events**
2. Enter `lisa_scheduler_window_started` in the "Listen to events" field and click **Start listening**
3. Disable dry run temporarily, then call `lisa_scheduler.set_override` to trigger a simulated window
4. Confirm the event appears in the listener with the expected payload

## Interpreting Log Messages

**Healthy output:**

```
INFO  Found 15 events
INFO  Calculated 8 event windows
INFO  DRY RUN: Would fire event lisa_scheduler_window_started
```

**Warning signs:**

```
WARNING  No events found
WARNING  Schedule refresh failed
WARNING  Invalid event window (end before start)
```

**Error signs:**

```
ERROR  Failed to fetch schedule
ERROR  Invalid configuration
```

## Debugging Issues

### No Dry Run Messages Appear

Possible causes:
- Dry run mode is not actually enabled — verify in the integration options
- No events were found — check `sensor.lisa_events_today` and the scraper logs
- The transition time hasn't been reached yet — use `set_override` to simulate

### Wrong Window Timing

Possible causes:
- Incorrect `pre_event_minutes` value
- Timezone mismatch
- Date/time format on the source website

Check [[../troubleshooting/debugging|Debug Logging]] and [[../troubleshooting/no-events-found|No Events Found]].

### Events Not Found

See [[../troubleshooting/no-events-found|No Events Found Guide]].

## When to Disable Dry Run

Disable dry run only after:

- Schedule parsing works reliably
- Window timing looks correct for multiple events
- Pre-event triggers fire at the right offsets
- No errors in logs after 24+ hours
- Automations have been tested by listening to events in Developer Tools

## Disabling Dry Run Mode

### Via UI

1. Settings → Devices & Services → LISA Scheduler → **Configure**
2. Uncheck **Dry run mode**
3. Click **Submit**

### Via YAML

```yaml
lisa_scheduler:
  dry_run: false
```

Restart Home Assistant.

After disabling, monitor the first real event cycle and confirm your automations fire as expected.

## Re-enabling Dry Run

You can switch back to dry run at any time — after configuration changes, when troubleshooting, or before testing new automations. It is safe to toggle.

## See Also

- [[first-time-setup|First Time Setup]]
- [[../troubleshooting/debugging|Debug Logging]]
- [[../troubleshooting/common-issues|Common Issues]]
- [[../troubleshooting/actions-not-triggering|Actions Not Triggering]]

---

**Time needed**: 1–2 days (monitoring)
**Difficulty**: Easy
**Prerequisites**: Integration installed
**Next**: [[../configuration/basic-settings|Configure Settings]]
