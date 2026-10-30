---
title: Services
tags: [usage, services]
---

# Services

## Refresh Schedule

`lisa_scheduler.refresh_schedule` immediately rereads the latest `lisa-schedule-api` snapshot. It does not start the API's upstream synchronization job.

Use it after an API sync completes, after restoring connectivity, or while validating stale/error recovery.

```yaml
service: lisa_scheduler.refresh_schedule
```

## Enable And Disable

```yaml
service: lisa_scheduler.enable
```

```yaml
service: lisa_scheduler.disable
```

Disabling pauses scheduler bus events. API polling and entity updates continue.

## Set Manual Override

```yaml
service: lisa_scheduler.set_override
data:
  start_time: "2026-10-30T18:00:00+01:00"
  end_time: "2026-10-30T20:00:00+01:00"
```

A manual override activates the window and event binary sensors for the supplied period. It does not alter API data.

## Clear Manual Override

```yaml
service: lisa_scheduler.clear_override
```

This removes an active override and resumes schedule-derived state immediately.

## Example Refresh Button

```yaml
type: button
name: Refresh schedule
icon: mdi:refresh
tap_action:
  action: call-service
  service: lisa_scheduler.refresh_schedule
```

The integration also exposes a Refresh Schedule button entity for dashboards.
