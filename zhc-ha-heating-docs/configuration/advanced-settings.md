---
title: Advanced Settings
tags: [configuration, settings, advanced]
---

# Advanced Settings

Advanced configuration options for the ZHC Heating Scheduler.

## Scan Interval

**Description**: How often to refresh the schedule from the website

**YAML Key**: `scan_interval`  
**Type**: Integer (seconds)  
**Default**: 21600 (6 hours)  
**Range**: 600-86400  

```yaml
scan_interval: 21600  # 6 hours
```

**Recommendations**:
- Static schedules: 43200 (12 hours)
- Normal schedules: 21600 (6 hours)  
- Frequently updated: 3600 (1 hour)
- Testing: 600 (10 minutes)

## Timezone

**Description**: Timezone for date/time parsing

**YAML Key**: `timezone`  
**Type**: String  
**Default**: "Europe/Amsterdam"  

```yaml
timezone: "Europe/Amsterdam"
```

**Common timezones**:
- Netherlands: `Europe/Amsterdam`
- Belgium: `Europe/Brussels`
- UK: `Europe/London`
- US East: `America/New_York`

## Date/Time Formats

**Date Format**:
```yaml
date_format: "%d-%m-%Y"  # 31-12-2024
```

**Time Format**:
```yaml
time_format: "%H:%M"  # 14:30
```

See [[../scraper/configuring-scraper|Scraper Configuration]] for details.

## Enable/Disable

**Description**: Turn scheduler on/off

**YAML Key**: `enabled`  
**Type**: Boolean  
**Default**: true  

```yaml
enabled: true
```

## Dry Run Mode

**Description**: Test mode without controlling heating

**YAML Key**: `dry_run`  
**Type**: Boolean  
**Default**: false  

```yaml
dry_run: true
```

See [[../quick-start/testing-dry-run|Testing with Dry Run]] for details.

## Complete Advanced Example

```yaml
zhc_heating_scheduler:
  # Basic settings
  schedule_url: "https://club.com/schedule"
  climate_entity: "climate.heating"
  pre_heat_hours: 2
  cool_down_minutes: 30
  target_temperature: 20.0
  
  # Advanced settings
  scan_interval: 21600
  timezone: "Europe/Amsterdam"
  date_format: "%d-%m-%Y"
  time_format: "%H:%M"
  enabled: true
  dry_run: false
```

## See Also

- [[basic-settings|Basic Settings]]
- [[scraper-configuration|Scraper Configuration]]
- [[examples|Configuration Examples]]

---

**Difficulty**: Intermediate  
**Prerequisites**: Basic settings configured

