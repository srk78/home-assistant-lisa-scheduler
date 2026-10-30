---
title: No Events Found
tags: [troubleshooting, api, events]
---

# No Events Found

An empty API schedule is valid, so first determine whether the API returned no matching records or Home Assistant failed to load the snapshot.

## Check The API

From a host allowed by the API:

```bash
curl -i "https://schedule.example.com/v1/events?atClubVenue=true"
```

Confirm:

- the response is HTTP 200;
- `data` contains expected events;
- `meta.timezone` is valid;
- `meta.truncated` is false;
- `startsAt` and `endsAt` are present for schedulable records.

If `data` is empty with `atClubVenue=true`, inspect venue classification in the API. Temporarily test without the venue filter or enable external events in the integration.

## Check Access

A `403` means the API rejected the source address. Add the exact Home Assistant host address to `ALLOWED_CIDRS` and restart the API.

Do not test only from a laptop browser. Home Assistant may run in another container, VM, or VLAN and present a different address.

## Check The Date Window

The integration requests today through 14 days ahead in the API timezone. Events outside that range are intentionally absent. Unschedulable and cancelled records are also excluded.

## Check Home Assistant Diagnostics

Inspect **Last Schedule Update**:

- `last_refresh_failed`: local API request or validation failure;
- `last_error`: the corresponding error text;
- `upstream_stale` and `upstream_partial`: retained API data is not fully fresh;
- `upstream_error_category`: upstream synchronization failure category;
- `upstream_record_counts`: records known by the API;
- `upstream_unschedulable_counts`: records without usable event times.

Call `lisa_scheduler.refresh_schedule` after the API has synchronized. This rereads the snapshot and does not initiate synchronization itself.

## Empty Schedule Versus Unavailable Integration

- **Entities load and event count is zero:** the API response was valid but no records matched.
- **Entities are unavailable on first setup:** the API was unreachable, forbidden, malformed, timezone-mismatched, or truncated.
- **Old events remain with stale attributes:** a prior snapshot loaded successfully and the latest refresh failed or upstream data is stale.

See [[../configuration/api-connection|API Connection]] and [[debugging|Debug Logging]].
