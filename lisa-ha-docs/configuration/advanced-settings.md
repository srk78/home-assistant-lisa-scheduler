---
title: Advanced Settings
tags: [configuration, advanced]
---

# Advanced Settings

## External Events

The default club-only view is designed for on-site operator workflows. Turn on **Include events at external venues** when away fixtures or other locations must participate in windows and automations.

This option changes the API query and reloads the integration. API records still carry `at_club_venue` and `venue_id` in entity attributes and event payloads.

## API Timezone

The timezone is not entered manually. Setup reads `meta.timezone` from the API and stores it with the config entry.

API timestamps must include an offset. They are converted to naive schedule-local values for the existing scheduling engine, then returned as timezone-aware values by Home Assistant timestamp sensors. If the API timezone later changes, the integration preserves the previous schedule and requires reconfiguration instead of silently moving events.

## Freshness Policy

A schedule is marked stale when:

- the latest Home Assistant API request failed;
- no local request has succeeded, or the latest success is older than twice the polling interval;
- the API reports `stale` or `partial`; or
- the API has no successful upstream synchronization timestamp.

Stale and partial snapshots remain usable. Malformed or truncated snapshots do not replace cached data.

## ETags

The API client stores the latest ETag and sends `If-None-Match` on later requests. A `304 Not Modified` response is a successful refresh: local errors clear, cached events remain, and freshness is recalculated.

## Dry Run And Manual Override

Dry run affects HA event firing only; API polling and entities continue normally. Manual override creates a temporary active window and does not modify the API snapshot.

## Diagnostics

Use the attributes on **Last Schedule Update** to distinguish:

- `last_refresh_failed` and `last_error`: Home Assistant could not read or validate the API;
- `upstream_error_category`: the API could not synchronize one or more upstream sources;
- `upstream_stale` and `upstream_partial`: API snapshot health;
- `upstream_sources`: per-source status;
- `upstream_record_counts` and `upstream_unschedulable_counts`: API inventory.

See [[api-connection|API Connection]] and [[../usage/dashboard-library/diagnostics-panel|Diagnostics Panel]].
