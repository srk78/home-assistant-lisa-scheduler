---
title: Available Services
tags: [usage, services]
---

# Available Services

LISA Scheduler registers five Home Assistant services under the `lisa_scheduler` domain. You can call these from automations, scripts, the Developer Tools UI, or the action editor.

## lisa_scheduler.refresh_schedule

**Description**: Forces an immediate re-fetch of the schedule from the configured URL or scraper sources. Normally the schedule refreshes automatically on the configured `scan_interval` (default: every 6 hours). Use this service to pull in changes immediately — for example, after you update your scraper configuration, or when you know the website has just been updated.

**Parameters**: None

**Example**:

```yaml
service: lisa_scheduler.refresh_schedule
```

**When to use**:
- After changing `scraper_sources` in your configuration to verify it works
- When you know the club website has just published a new schedule
- During troubleshooting to force a fresh fetch and check the logs

---

## lisa_scheduler.enable

**Description**: Enables the scheduler. When enabled, the coordinator fires HA bus events on schedule transitions. The scheduler is enabled by default when the integration loads.

**Parameters**: None

**Example**:

```yaml
service: lisa_scheduler.enable
```

**When to use**:
- Re-enable after calling `lisa_scheduler.disable`
- In an automation that re-enables the scheduler at the start of a season
- After testing with `dry_run: true`, to switch back to live mode alongside enabling

---

## lisa_scheduler.disable

**Description**: Disables the scheduler. The coordinator continues polling and updating sensors, but no `lisa_scheduler_*` bus events are fired. Useful for maintenance periods, off-season, or testing when you do not want automations to trigger.

**Parameters**: None

**Example**:

```yaml
service: lisa_scheduler.disable
```

**When to use**:
- During maintenance work when you do not want heating or lights triggered
- At the end of a season when no more events are expected
- When testing schedule changes and you want to suppress actual automation triggers

---

## lisa_scheduler.set_override

**Description**: Manually activates a window for a specified time range. The coordinator treats this as if a scheduled window were active: it fires `lisa_scheduler_window_started` at `start_time`, `lisa_scheduler_event_started` at `start_time` (overrides have no pre-event lead-in), and the corresponding end events at `end_time`.

This is useful for one-off events that are not in the scraped schedule, or for testing your automations without waiting for a real event.

**Parameters**:

| Parameter | Type | Required | Description |
|---|---|---|---|
| `start_time` | string (ISO 8601 datetime) | Yes | When the override window should begin. Example: `"2024-12-31T14:00:00"` |
| `end_time` | string (ISO 8601 datetime) | Yes | When the override window should end. Example: `"2024-12-31T16:00:00"` |

Both times are interpreted as local time in the configured timezone (default: `Europe/Amsterdam`).

**Example**:

```yaml
service: lisa_scheduler.set_override
data:
  start_time: "2024-12-31T14:00:00"
  end_time: "2024-12-31T16:00:00"
```

**When to use**:
- A special event is not in the club's online schedule and you want the normal heating/lights sequence
- Testing your automation actions without waiting for a real scheduled event
- Running a one-off event during the off-season

---

## lisa_scheduler.clear_override

**Description**: Clears an active manual override and resumes normal schedule-based operation. If the override window was active at the time of clearing, the coordinator fires `lisa_scheduler_event_ended` and `lisa_scheduler_window_ended` to allow automations to clean up (e.g. turn off heating).

**Parameters**: None

**Example**:

```yaml
service: lisa_scheduler.clear_override
```

**When to use**:
- After an overridden event finishes earlier than planned
- To cancel a test override before its `end_time`
- In an automation that clears an override when the building is manually vacated

---

## Calling Services from Developer Tools

You can call any of these services interactively from the Home Assistant UI without writing YAML:

1. Go to **Developer Tools → Services** (in older HA versions: **Developer Tools → Actions**).
2. In the **Service** field, type `lisa_scheduler` to filter the list.
3. Select the service you want to call.
4. For `set_override`, fill in the `start_time` and `end_time` fields in the form.
5. Click **Call Service**.

This is the fastest way to test the integration manually — for example, set an override for the next 10 minutes and verify that your heating or lighting automations trigger as expected.

---

## Calling Services from Automations

Services are most useful when combined with conditions or other triggers. A few practical patterns:

### Re-enable on a fixed date

```yaml
automation:
  - alias: "LISA: re-enable at season start"
    trigger:
      - platform: time
        at: "00:00:00"
    condition:
      - condition: template
        value_template: "{{ now().month == 9 and now().day == 1 }}"
    action:
      - service: lisa_scheduler.enable
```

### Force refresh after midnight

```yaml
automation:
  - alias: "LISA: nightly schedule refresh"
    trigger:
      - platform: time
        at: "00:30:00"
    action:
      - service: lisa_scheduler.refresh_schedule
```

### Create a temporary override from a script

```yaml
script:
  emergency_override:
    alias: "Emergency 2-hour event override"
    sequence:
      - service: lisa_scheduler.set_override
        data:
          start_time: "{{ now().strftime('%Y-%m-%dT%H:%M:%S') }}"
          end_time: "{{ (now() + timedelta(hours=2)).strftime('%Y-%m-%dT%H:%M:%S') }}"
```

---

## See Also

- [[automations|Automation Examples]] — how to respond to the bus events these services interact with
- [[sensors|Available Sensors]] — binary sensors that reflect scheduler state (`lisa_scheduler_enabled`, `lisa_manual_override_active`)
