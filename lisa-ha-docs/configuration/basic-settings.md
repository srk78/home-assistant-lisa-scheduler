---
title: Basic Settings
tags: [configuration, basic]
---

# Basic Settings

## Schedule API URL

**YAML key:** `api_url`

Enter either the API base URL or its full `/v1/events` endpoint:

```yaml
lisa_scheduler:
  api_url: "https://schedule.example.com"
```

The URL is validated during setup. It must use HTTP or HTTPS, must not include embedded credentials, a query, or a fragment, and must return the unified `lisa-schedule-api` contract.

## Venue Scope

**YAML key:** `include_external_events`
**Default:** `false`

When disabled, the integration requests `atClubVenue=true`. Enable it to include external and away events as well.

## Club Events

**YAML key:** `include_club_events`
**Default:** `true`

Club events (clinics, team dinners, tournaments) are scheduled like matches and trainings. Set this to `false` to keep them out of scheduling: they open no windows and fire no bus events, but still appear in the sidebar panel. Also available in the integration options.

## Pre-Event Triggers

**YAML key:** `pre_event_triggers`
**Default:** `[120]`

Values are minutes before each event. They are deduplicated and sorted, and each value must be between 0 and 1440. The largest value also opens the event window.

```yaml
pre_event_triggers: [120, 30]
```

Optional day-boundary lists use the same range:

```yaml
pre_first_event_triggers: [60]
pre_last_event_end_triggers: [15]
post_last_event_triggers: [10]
```

## Polling Interval

**YAML key:** `scan_interval`
**Default/minimum:** `600` seconds
**Maximum:** `86400` seconds

This controls how often Home Assistant rereads the API snapshot. It does not control the API's upstream synchronization timer.

## Enabled And Dry Run

```yaml
enabled: true
dry_run: false
```

Disabling the scheduler pauses event firing while entities remain available. Dry run logs transitions without firing bus events.

## Logo

The UI options include an optional `logo_url`. It becomes the entity picture for scheduler entities.

## Complete Example

```yaml
lisa_scheduler:
  api_url: "https://schedule.example.com"
  include_external_events: false
  pre_event_triggers: [120, 30]
  pre_first_event_triggers: [60]
  pre_last_event_end_triggers: [15]
  post_last_event_triggers: [10]
  scan_interval: 600
  enabled: true
  dry_run: false
```

See [[api-connection|API Connection]] for networking and freshness behavior.
