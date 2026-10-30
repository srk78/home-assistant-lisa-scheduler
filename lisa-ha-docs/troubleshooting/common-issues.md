---
title: Common Issues
tags: [troubleshooting, faq]
---

# Common Issues

## Cannot Connect

Verify the URL from the Home Assistant runtime. A base URL is accepted, but it must ultimately expose `/v1/events`. Check DNS, routing, TLS certificates, proxy configuration, and the API service.

## Forbidden

The API is reachable but the request address is not allowed. Configure `ALLOWED_CIDRS` with the Home Assistant host or container address. Reverse proxies must preserve a trustworthy client address configuration.

## Invalid API Response

The integration rejects incomplete JSON, unknown event types, cancelled or unschedulable records, naive timestamps, end times before starts, and truncated snapshots. Check the API version and logs.

## Unexpected Timezone

The API timezone is captured during setup. Reconfigure the integration after an intentional API timezone change. This prevents a silent shift in active windows.

## Schedule Is Stale

Inspect whether the problem is local or upstream:

- `last_refresh_failed: true` means Home Assistant could not fetch or validate the API;
- `upstream_stale: true` means the API's successful source data is too old;
- `upstream_partial: true` means exactly one API source is healthy;
- `upstream_error_category` identifies the upstream failure class.

Cached windows remain available during transient failures.

## Refresh Did Not Change Anything

The refresh service only rereads the API's persisted snapshot. Wait for or manually run the API synchronization job if upstream data has not changed. An ETag may produce `304 Not Modified`, which is still a successful refresh.

## Wrong Events Included

Keep **Include events at external venues** disabled for club-only operation. If a venue is misclassified, fix the venue matchers in `lisa-schedule-api`; Home Assistant trusts the API's `atClubVenue` field.

## Automations Do Not Fire

Confirm the scheduler is enabled, dry run is off, event names are exact, and the automation is listening before the transition occurs. See [[actions-not-triggering|Actions Not Triggering]].

## More Help

- [[../configuration/api-connection|API Connection]]
- [[no-events-found|No Events Found]]
- [[debugging|Debug Logging]]
