---
title: Installation via YAML Configuration
tags: [quickstart, installation, yaml, advanced]
---

# Installation via YAML Configuration

Install the integration through HACS or copy `custom_components/lisa_scheduler` into the Home Assistant configuration directory. Then add the integration configuration:

```yaml
lisa_scheduler:
  api_url: "https://schedule.example.com"
  include_external_events: false
  logo_url: "https://www.example.com/logo.png"
  pre_event_triggers: [120, 30]
  pre_first_event_triggers: [60]
  pre_last_event_end_triggers: [15]
  post_last_event_triggers: [10]
  scan_interval: 600
  enabled: true
  dry_run: true
```

`api_url` may be the API base URL or the full `/v1/events` URL. During import, Home Assistant connects to the API, validates its unified event contract, and stores the returned schedule timezone.

`include_external_events: false` sends `atClubVenue=true` and is the recommended operator default. Set it to `true` to include away and other events whose venue is not classified as a club venue.

The default polling interval is 600 seconds. This reads the API's persisted snapshot; the API's independent synchronization timer normally updates upstream data every 30 minutes.

## API Access

The API must allow requests from the Home Assistant address. For example:

```dotenv
ALLOWED_CIDRS=192.168.1.25/32
```

Use the API's Caddy HTTPS URL when it is available. `127.0.0.1` only reaches the API when it shares the Home Assistant network namespace. See [[../configuration/api-connection|API Connection]] for container and proxy guidance.

## Verify

1. Run **Developer Tools -> YAML -> Check Configuration**.
2. Restart Home Assistant.
3. Inspect the `lisa_scheduler` entities under **Developer Tools -> States**.
4. Call `lisa_scheduler.refresh_schedule` and inspect the Last Schedule Update attributes.

## Example Automation

```yaml
automation:
  - alias: "LISA: notify 30 minutes before an event"
    trigger:
      - platform: event
        event_type: lisa_scheduler_pre_event_trigger
        event_data:
          minutes_before: 30
    action:
      - service: notify.notify
        data:
          message: "A club event starts in 30 minutes."
```

The integration never controls a device by itself. Lighting, heating, displays, and notifications are optional automation actions.

## Next Steps

- [[../configuration/basic-settings|Basic Settings]]
- [[../configuration/api-connection|API Connection]]
- [[../usage/services|Services]]
- [[../usage/dashboard-cards|Dashboard Library]]
