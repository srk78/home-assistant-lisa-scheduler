---
title: Schedule API Connection
tags: [configuration, api, networking]
---

# Schedule API Connection

LISA Scheduler consumes the unified `GET /v1/events` endpoint from `lisa-schedule-api`. The API owns website synchronization, normalization, venue classification, duration estimates, persistence, and source health. This integration does not contain a crawler or a direct-website fallback.

## URL

Both forms are accepted:

```text
https://schedule.example.com
https://schedule.example.com/v1/events
```

The integration stores the normalized `/v1/events` endpoint. HTTP is allowed for trusted local networks, but HTTPS through Caddy is recommended.

## Requests

By default, Home Assistant requests today through 14 days ahead with:

```text
cancelled=false&atClubVenue=true
```

Cancelled and unschedulable records are never scheduled. Enabling **Include events at external venues** removes the `atClubVenue` filter. Responses use ETags, so an unchanged snapshot can return `304 Not Modified`.

## Access Policy

Requests without an `Origin` header must come from an address allowed by the API. Prefer the exact Home Assistant address:

```dotenv
ALLOWED_CIDRS=192.168.1.25/32
```

After changing the API environment, restart its service. A `403` setup error normally means the API is reachable but sees an address outside this allowlist. Check reverse-proxy forwarding and the address shown in API logs.

Origin allowlisting is not API authentication. Use firewall rules, a private network, or proxy authentication if the network boundary is not sufficient.

## Containers And Localhost

`127.0.0.1` refers to the current process or container. It only works when Home Assistant and `lisa-schedule-api` share a network namespace. Otherwise use:

- the API container's resolvable service name on a shared container network;
- the host's LAN address and published API port; or
- the Caddy HTTPS hostname.

Confirm reachability from the Home Assistant runtime, not only from a laptop browser.

## Polling And Synchronization

- Home Assistant rereads the API snapshot every 10 minutes by default.
- `lisa-schedule-api` normally synchronizes its upstream sources every 30 minutes.
- `lisa_scheduler.refresh_schedule` forces a snapshot read but never starts upstream synchronization.
- The API's default upstream stale threshold is two hours.

These are separate clocks. Faster Home Assistant polling makes a completed API synchronization visible sooner, but does not make the API crawl more often.

## Freshness And Failures

Usable stale or partial snapshots are retained and exposed with `schedule_stale: true`. The Last Schedule Update sensor reports:

- local API request attempt and success times;
- upstream attempt and successful synchronization times;
- `upstream_stale`, `upstream_partial`, and `upstream_error_category`;
- per-source health and record counts;
- unschedulable counts and the active venue-scope option.

Malformed, timezone-mismatched, or truncated responses do not replace the previous Home Assistant schedule. On the first load, such a response leaves the integration unavailable until the API recovers or is reconfigured.

## Troubleshooting Checklist

1. Open `/healthz` and `/readyz` from the API host.
2. Request `/v1/events` from the Home Assistant network location.
3. Check `ALLOWED_CIDRS` after any container or host-address change.
4. Confirm the API response includes `data`, `meta`, and timezone-aware `startsAt` and `endsAt` values.
5. Inspect the Last Schedule Update attributes and API service logs.

See [[../troubleshooting/no-events-found|No Events Found]] and [[../troubleshooting/debugging|Debug Logging]] for the Home Assistant side.
