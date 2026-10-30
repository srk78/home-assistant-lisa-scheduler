---
title: Debug Logging
tags: [troubleshooting, logging, api]
---

# Debug Logging

Enable integration logging in `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.lisa_scheduler: debug
```

Restart Home Assistant, reproduce the issue, and inspect **Settings -> System -> Logs**.

## Useful Messages

Look for:

- API request failures and HTTP status codes;
- forbidden access mentioning `ALLOWED_CIDRS`;
- response validation or timezone errors;
- event and window counts after an API update;
- dry-run transition messages;
- bus-event firing messages.

## Entity Diagnostics

The **Last Schedule Update** entity exposes both sides of the data path:

| Attribute | Meaning |
|-----------|---------|
| `last_refresh_attempt` | Latest Home Assistant request attempt |
| `last_api_fetch_success` | Latest valid API response or 304 |
| `last_error` | Local request or validation error |
| `last_refresh_failed` | Whether the latest local request failed |
| `api_generated_at` | When the API generated the snapshot response |
| `upstream_last_attempt` | Latest source synchronization attempt |
| `upstream_error_category` | Sanitized upstream failure category |
| `upstream_stale` | API freshness flag |
| `upstream_partial` | Only one upstream source is healthy |
| `upstream_sources` | Per-source health details |
| `schedule_stale` | Combined Home Assistant and API freshness state |

## API-Side Checks

Inspect the API service and synchronization timer separately. From an allowed host:

```bash
curl -i https://schedule.example.com/healthz
curl -i https://schedule.example.com/readyz
curl -i https://schedule.example.com/v1/sync-status
curl -i "https://schedule.example.com/v1/events?atClubVenue=true"
```

The health endpoints do not prove that Home Assistant is allowed to call protected endpoints. A successful `/v1/events` request from the Home Assistant network location is the relevant check.

Remove debug logging after diagnosis to reduce log volume.
