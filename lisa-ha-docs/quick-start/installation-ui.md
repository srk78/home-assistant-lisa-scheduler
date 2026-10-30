---
title: Installation via Home Assistant UI
tags: [quickstart, installation, ui]
---

# Installation via Home Assistant UI

## Prerequisites

- Home Assistant 2024.1.0 or newer
- A running `lisa-schedule-api` instance
- An API URL reachable from the Home Assistant host
- The Home Assistant address allowed by the API's `ALLOWED_CIDRS`

See [[../configuration/api-connection|API Connection]] before setup if Home Assistant and the API run in different containers or machines.

## Install

1. In HACS, open **Integrations** and add `https://github.com/stefan/lisa-scheduler` as a custom integration repository.
2. Install **LISA Scheduler** and restart Home Assistant.
3. Go to **Settings -> Devices & Services -> Add Integration**.
4. Select **LISA Scheduler**.

Manual installation is also supported: place `custom_components/lisa_scheduler` under the Home Assistant configuration directory and restart.

## Configure

| Field | Description | Default |
|-------|-------------|---------|
| **Schedule API URL** | API base URL or full `/v1/events` endpoint | Required |
| **Include events at external venues** | Include away and other non-club events | Off |
| **Logo URL** | Optional entity picture | Empty |
| **Pre-event triggers** | Comma-separated lead times, such as `120, 30` | `120` |
| **Schedule refresh interval** | Seconds between API snapshot reads | `600` |
| **Dry run** | Log transitions without firing HA events | Off |

The setup request validates the API contract and stores the timezone returned by the API. An empty schedule is valid. A `403` error means the API received the request but its access policy did not allow the Home Assistant address.

## Verify

1. Open **Developer Tools -> States** and search for `lisa_scheduler`.
2. Check `sensor.lisa_scheduler_last_schedule_update` for `schedule_stale`, `upstream_partial`, and `upstream_error_category` attributes.
3. Call `lisa_scheduler.refresh_schedule` to reread the current API snapshot.
4. Use **Developer Tools -> Events** to listen for a specific event such as `lisa_scheduler_window_started`.

The refresh service does not start a website crawl. Upstream synchronization belongs to `lisa-schedule-api` and normally runs every 30 minutes.

## Change The API URL

Open the integration entry and choose **Reconfigure**. The replacement endpoint is validated before the entry reloads. Venue scope, trigger values, polling interval, enabled state, and dry-run mode remain under **Configure**.

## Next Steps

- [[first-time-setup|First Time Setup]]
- [[../configuration/api-connection|API Connection and Networking]]
- [[../usage/automations|Create Automations]]
- [[../usage/dashboard-cards|Build an Operator Dashboard]]

For a club operator tablet, start with [[../usage/dashboard-library/operator-overview|Operator Overview]].
