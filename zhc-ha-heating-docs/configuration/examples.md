---
title: Configuration Examples
tags: [configuration, examples]
---

# Configuration Examples

Real-world configuration examples for different scenarios.

## Basic Setup

### Simple Single URL

```yaml
zhc_heating_scheduler:
  climate_entity: "climate.plugwise_sa"
  pre_heat_hours: 2
  cool_down_minutes: 30
  target_temperature: 20
  
  scraper_sources:
    - url: "https://www.club.com/schedule"
      type: training
      selectors:
        container: "div.event-item"
        date: "span.date"
        time: "span.time"
        title: "span.title"
```

## Multiple Sources

### Training + Matches

```yaml
zhc_heating_scheduler:
  climate_entity: "climate.plugwise_sa"
  pre_heat_hours: 2
  cool_down_minutes: 30
  
  scraper_sources:
    # Training schedule
    - url: "https://www.club.com/training"
      type: training
      selectors:
        container: "div.training-item"
        date: "span.date"
        time: "span.time"
    
    # Match schedule
    - url: "https://www.club.com/matches"
      type: match
      selectors:
        container: "div.match-item"
        date: "span.match-date"
        time: "span.match-time"
```

## Zandvoortsche Hockey Club (ZHC)

### ZHC Configuration

```yaml
zhc_heating_scheduler:
  climate_entity: "climate.plugwise_sa"
  pre_heat_hours: 2
  cool_down_minutes: 30
  target_temperature: 20
  
  scraper_sources:
    - url: "https://www.zandvoortschehockeyclub.nl/trainingsschema"
      type: training
      method: html
    
    - url: "https://www.zandvoortschehockeyclub.nl/wedstrijdschema"
      type: match
      method: html
  
  date_format: "%d-%m-%Y"
  time_format: "%H:%M"
  timezone: "Europe/Amsterdam"
```

## Advanced Configurations

### API Source

```yaml
zhc_heating_scheduler:
  climate_entity: "climate.thermostat"
  pre_heat_hours: 3
  cool_down_minutes: 45
  
  scraper_sources:
    - url: "https://api.club.com/events"
      type: training
      method: api
      api_headers:
        Authorization: "Bearer YOUR_TOKEN"
        Accept: "application/json"
      api_params:
        from: "2024-01-01"
        limit: "100"
```

### iCal Feed

```yaml
zhc_heating_scheduler:
  climate_entity: "climate.heating"
  pre_heat_hours: 2
  cool_down_minutes: 30
  
  scraper_sources:
    - url: "https://calendar.club.com/events.ics"
      type: training
      method: ical
```

### Mixed Sources

```yaml
zhc_heating_scheduler:
  climate_entity: "climate.plugwise"
  pre_heat_hours: 2
  cool_down_minutes: 30
  
  scraper_sources:
    # HTML for training
    - url: "https://club.com/training"
      type: training
      method: html
      selectors:
        container: "div.event"
        date: "span.date"
        time: "span.time"
    
    # API for matches  
    - url: "https://api.club.com/matches"
      type: match
      method: api
    
    # iCal for tournaments
    - url: "https://club.com/tournaments.ics"
      type: match
      method: ical
```

## Size-Based Configurations

### Small Club

```yaml
zhc_heating_scheduler:
  climate_entity: "climate.small_building"
  pre_heat_hours: 1  # Heats quickly
  cool_down_minutes: 20
  target_temperature: 19
  scan_interval: 43200  # 12 hours
```

### Large Club

```yaml
zhc_heating_scheduler:
  climate_entity: "climate.large_building"
  pre_heat_hours: 3  # Needs more time
  cool_down_minutes: 45
  target_temperature: 20.5
  scan_interval: 3600  # 1 hour
```

## Testing Configuration

### Dry Run Mode

```yaml
zhc_heating_scheduler:
  climate_entity: "climate.test"
  pre_heat_hours: 0.5  # 30 min for testing
  cool_down_minutes: 5
  dry_run: true  # Don't actually control heating
  scan_interval: 600  # 10 minutes
```

## Date Format Examples

### European Format (DD-MM-YYYY)

```yaml
zhc_heating_scheduler:
  date_format: "%d-%m-%Y"  # 31-12-2024
  time_format: "%H:%M"     # 14:30
  timezone: "Europe/Amsterdam"
```

### US Format (MM-DD-YYYY)

```yaml
zhc_heating_scheduler:
  date_format: "%m-%d-%Y"  # 12-31-2024
  time_format: "%H:%M"     # 2:30 PM
  timezone: "America/New_York"
```

### ISO Format (YYYY-MM-DD)

```yaml
zhc_heating_scheduler:
  date_format: "%Y-%m-%d"  # 2024-12-31
  time_format: "%H:%M"
  timezone: "UTC"
```

## Next Steps

- [[basic-settings|Configure Basic Settings]]
- [[scraper-configuration|Configure Scraper]]
- [[../scraper/configuring-scraper|Scraper Setup Guide]]
- [[../troubleshooting/common-issues|Troubleshooting]]

---

**Need help?** Check [[../troubleshooting/common-issues|Common Issues]] or ask on the [forum](https://community.home-assistant.io/).

