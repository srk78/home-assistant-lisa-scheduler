---
title: Debug Logging
tags: [troubleshooting, debugging, logging]
---

# Debug Logging

Enable detailed logging to troubleshoot issues with LISA Scheduler.

## Enable Debug Logging

### Via configuration.yaml

Add this to your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.lisa_scheduler: debug
```

### Specific Components

Enable debug logging for specific parts of the integration:

```yaml
logger:
  default: info
  logs:
    # All components
    custom_components.lisa_scheduler: debug

    # Or specific components
    custom_components.lisa_scheduler.coordinator: debug
    custom_components.lisa_scheduler.scraper: debug
    custom_components.lisa_scheduler.scheduler: debug
```

### Apply Changes

After editing `configuration.yaml`:

1. Go to **Developer Tools** → **YAML**
2. Click **Reload Logger Configuration** (no restart required)
3. Or restart Home Assistant for a clean state

## Viewing Logs

### Via UI

1. Go to **Settings** → **System** → **Logs**
2. Search for `lisa_scheduler`
3. Filter by level if needed

### Via Command Line

```bash
tail -f /config/home-assistant.log | grep lisa_scheduler
```

## What to Look For

### Successful Operation

```
INFO  [custom_components.lisa_scheduler] Setting up LISA Scheduler
INFO  [custom_components.lisa_scheduler] Using configurable scraper with 2 sources
DEBUG [custom_components.lisa_scheduler.scraper] Fetching from source: https://...
INFO  [custom_components.lisa_scheduler] Found 15 events
INFO  [custom_components.lisa_scheduler] Calculated 8 event windows
DEBUG [custom_components.lisa_scheduler.coordinator] Next window start: 2026-03-10 16:00:00
DEBUG [custom_components.lisa_scheduler.coordinator] Firing event: lisa_scheduler_window_started
```

### Event Firing

When a transition occurs, you will see log lines like:

```
INFO  [custom_components.lisa_scheduler] Firing lisa_scheduler_window_started
INFO  [custom_components.lisa_scheduler] Firing lisa_scheduler_event_started
INFO  [custom_components.lisa_scheduler] Firing lisa_scheduler_pre_event_trigger (minutes_before=30)
INFO  [custom_components.lisa_scheduler] Firing lisa_scheduler_window_ended
```

In dry run mode, the same lines appear prefixed with `DRY RUN: Would fire event`.

### Common Errors

**Schedule Fetch Errors**:
```
ERROR [custom_components.lisa_scheduler] Error fetching schedule: ...
ERROR [custom_components.lisa_scheduler] HTTP error fetching schedule: ...
WARNING [custom_components.lisa_scheduler] No events found in HTML
```

**Configuration Errors**:
```
ERROR [custom_components.lisa_scheduler] Invalid configuration: ...
```

## Debug by Component

### Coordinator Debugging

```yaml
logger:
  logs:
    custom_components.lisa_scheduler.coordinator: debug
```

Shows:
- State updates and transition decisions
- HA event firing
- Schedule refreshes
- Override handling

### Scraper Debugging

```yaml
logger:
  logs:
    custom_components.lisa_scheduler.scraper: debug
    custom_components.lisa_scheduler.configurable_scraper: debug
```

Shows:
- HTTP requests and responses
- HTML parsing steps
- Event extraction
- Date/time parsing

### Scheduler Debugging

```yaml
logger:
  logs:
    custom_components.lisa_scheduler.scheduler: debug
```

Shows:
- Event window calculations
- Overlapping window merging
- Pre-event trigger offset calculations

## Debugging Pre-Event Trigger Timing

If `lisa_scheduler_pre_event_trigger` is not firing at the expected time, enable scheduler and coordinator debug logging and look for log lines containing `_fire_pre_event_triggers`:

```
DEBUG [custom_components.lisa_scheduler.coordinator] _fire_pre_event_triggers: checking offset 120 min — already fired: False
DEBUG [custom_components.lisa_scheduler.coordinator] _fire_pre_event_triggers: checking offset 30 min — already fired: True
```

- `already fired: False` means the trigger is eligible and will fire (or has just fired)
- `already fired: True` means it was already fired for this window and will not repeat

If the trigger time has already passed when the scheduler first evaluates a window (e.g. after a restart), the offset will be skipped. Check `sensor.lisa_next_event_start` and compare it to your configured `pre_event_triggers` values.

## Temporary Debug Logging (No Restart)

For quick debugging without restarting Home Assistant:

1. **Developer Tools** → **Services**
2. Service: `logger.set_level`
3. Data:
```yaml
custom_components.lisa_scheduler: debug
```

This change lasts until the next restart.

## Common Debug Scenarios

### Scenario 1: Events Not Found

Enable scraper debug:
```yaml
custom_components.lisa_scheduler.scraper: debug
```

Look for:
- Whether the HTTP fetch succeeds
- Parsing attempts and selector matches
- Date/time format issues

### Scenario 2: Automations Not Triggering

Enable coordinator debug:
```yaml
custom_components.lisa_scheduler.coordinator: debug
```

Look for:
- Lines showing `Firing lisa_scheduler_*` — if absent, no transition was detected
- State calculations comparing previous vs current window state
- Whether dry run mode is suppressing event firing

Also see [[actions-not-triggering|Actions Not Triggering]] for a complete diagnosis guide.

### Scenario 3: Wrong Timing

Enable scheduler debug:
```yaml
custom_components.lisa_scheduler.scheduler: debug
```

Look for:
- Window start/end calculations
- Pre-event offset application
- Event merging output

## Collecting Debug Information for Bug Reports

1. Enable debug logging
2. Reproduce the problem
3. Collect logs from the time the problem occurred
4. Remove any personal information (URLs with tokens, email addresses)
5. Include in a GitHub issue

### Information to Include

- Home Assistant version
- Integration version
- Relevant log entries
- Configuration (sanitized)
- Steps to reproduce

### Log Format Reference

```
2026-03-10 14:30:00 DEBUG (MainThread) [custom_components.lisa_scheduler] Message here
```

Fields: timestamp, log level, thread, component name, message.

## Performance Considerations

Debug logging generates significant output:
- It can fill disk space quickly on systems with limited storage
- It has a slight performance impact during high-frequency polling

Disable when you are done:

```yaml
logger:
  default: info
  logs:
    custom_components.lisa_scheduler: info
```

## See Also

- [[common-issues|Common Issues]]
- [[no-events-found|No Events Found]]
- [[actions-not-triggering|Actions Not Triggering]]

---

**Difficulty**: Easy
**Impact**: Useful for all troubleshooting scenarios
