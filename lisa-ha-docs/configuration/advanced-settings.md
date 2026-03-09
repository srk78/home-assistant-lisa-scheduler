---
title: Advanced Settings
tags: [configuration, settings, advanced]
---

# Advanced Settings

Advanced configuration options for the LISA Scheduler integration.

## Timezone

**Description**: The timezone used when parsing dates and times from the schedule source.

**YAML Key**: `timezone`
**Type**: String
**Default**: `"Europe/Amsterdam"`

```yaml
timezone: "Europe/Amsterdam"
```

Common values:
- Netherlands: `Europe/Amsterdam`
- Belgium: `Europe/Brussels`
- UK: `Europe/London`
- US East: `America/New_York`

All datetimes are normalised to naive local time in the configured timezone throughout the integration.

## Date and Time Formats

Use these settings to help the scraper parse dates and times from the schedule page when automatic detection does not produce correct results.

**Date Format**:
```yaml
date_format: "%d-%m-%Y"  # e.g. 31-12-2024
```

**Time Format**:
```yaml
time_format: "%H:%M"  # e.g. 14:30
```

Format strings follow Python `strftime` conventions. See [Scraper Configuration](../scraper/configuring-scraper) for details on when these are needed.

## Scraper Sources

For advanced users who need to pull schedules from multiple URLs or non-standard page structures, `scraper_sources` lets you define a list of sources in YAML. Each source specifies a URL, the fetch method (`html`, `api`, or `ical`), and optional CSS selectors or HTTP parameters.

```yaml
lisa_scheduler:
  scraper_sources:
    - url: "https://www.yourclub.nl/training"
      type: training
      method: html
      selectors:
        container: "div.event-item"
        date: "span.date"
        time: "span.time"
        title: "span.title"

    - url: "https://www.yourclub.nl/matches"
      type: match
      method: html
      selectors:
        container: "div.match-item"
        date: "span.match-date"
        time: "span.match-time"
```

When `scraper_sources` is present, it takes precedence over `schedule_url`. This setting is only available via YAML. See [Scraper Configuration](../scraper/configuring-scraper) for a full reference.

## Pre-event Triggers (list syntax in YAML)

In YAML you can also provide `pre_event_triggers` as a list instead of a comma-separated string:

```yaml
lisa_scheduler:
  pre_event_triggers: "120, 60, 15"
```

Both forms are equivalent. See [Basic Settings — Pre-event Triggers](basic-settings#pre-event-triggers) for a full explanation of how trigger times work.

## Complete Advanced Example

```yaml
lisa_scheduler:
  schedule_url: "https://www.yourclub.nl/schedule"
  logo_url: "https://www.yourclub.nl/logo.png"
  pre_event_triggers: "120, 30"

  scan_interval: 21600
  timezone: "Europe/Amsterdam"
  date_format: "%d-%m-%Y"
  time_format: "%H:%M"
  enabled: true
  dry_run: false
```

## See Also

- [Basic Settings](basic-settings)
- [Scraper Configuration](../scraper/configuring-scraper)
- [Configuration Examples](examples)

---

**Difficulty**: Intermediate
**Prerequisites**: Basic settings configured
