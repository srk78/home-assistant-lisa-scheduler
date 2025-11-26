---
title: Configuring the Scraper (No Code Required)
tags: [scraper, configuration, advanced]
---

# Configuring the Scraper (No Code Required)

The ZHC Heating Scheduler now supports **configurable scrapers** - you can adapt it to any website using just configuration, without writing any Python code!

## Overview

The configurable scraper system allows you to:

- ✅ Scrape multiple URLs (training + matches)
- ✅ Use CSS selectors to find schedule data
- ✅ Configure date/time formats
- ✅ Support different methods (HTML, API, iCal)
- ✅ Share configurations with other users
- ✅ Adjust when website structure changes

## Basic Configuration

### Via YAML

Add this to your `configuration.yaml`:

```yaml
zhc_heating_scheduler:
  # Basic settings
  climate_entity: "climate.plugwise_sa"
  pre_heat_hours: 2
  cool_down_minutes: 30
  
  # Scraper configuration
  scraper_sources:
    - url: "https://www.example.com/training"
      type: training
      method: html
      selectors:
        container: "div.event-item"
        date: "span.date"
        time: "span.time"
        title: "span.title"
    
    - url: "https://www.example.com/matches"
      type: match
      method: html
      selectors:
        container: "div.match-item"
        date: "span.match-date"
        time: "span.match-time"
  
  # Date/time parsing
  date_format: "%d-%m-%Y"
  time_format: "%H:%M"
  timezone: "Europe/Amsterdam"
```

### Finding CSS Selectors

> [!TIP]
> Use your browser's Developer Tools to find CSS selectors!

1. **Open the schedule webpage** in Chrome or Firefox

2. **Open Developer Tools**
   - Right-click on an event → **Inspect**
   - Or press `F12`

3. **Find the event container**
   - Look for the HTML element that wraps each event
   - Common patterns:
     - `<div class="event">`
     - `<tr>` in a table
     - `<li class="schedule-item">`

4. **Note the CSS selector**
   - Class: `.event-item` or `div.event`
   - ID: `#schedule-container`
   - Nested: `div.schedule > div.item`

5. **Find date/time/title elements**
   - Look inside the container for date, time, and title
   - Note their selectors (usually `span.date`, `div.time`, etc.)

## Configuration Options

### Source Configuration

Each source in `scraper_sources` can have:

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `url` | string | ✅ | The webpage or API URL to scrape |
| `type` | string | ❌ | Event type: `training`, `match`, or `unknown` |
| `method` | string | ❌ | Scraping method: `html`, `api`, or `ical` |
| `selectors` | dict | For HTML | CSS selectors for finding data |
| `api_endpoint` | string | For API | Alternative API endpoint |
| `api_headers` | dict | For API | HTTP headers to send |
| `api_params` | dict | For API | Query parameters |

### Selector Configuration

For HTML sources, configure these selectors:

| Selector | Description | Example |
|----------|-------------|---------|
| `container` | Element that wraps each event | `"div.event-item"` |
| `date` | Element containing the date | `"span.date"` |
| `time` | Element containing the time | `"span.time"` |
| `title` | Element containing event title | `"span.title"` |
| `location` | Element containing location (optional) | `"span.location"` |

### Date/Time Formats

Configure how dates and times are parsed:

| Option | Description | Example |
|--------|-------------|---------|
| `date_format` | strptime format for dates | `"%d-%m-%Y"` (31-12-2024) |
| `time_format` | strptime format for times | `"%H:%M"` (14:30) |
| `timezone` | Timezone name | `"Europe/Amsterdam"` |

Common date formats:
- `"%d-%m-%Y"` → 31-12-2024
- `"%Y-%m-%d"` → 2024-12-31
- `"%d/%m/%Y"` → 31/12/2024
- `"%d %B %Y"` → 31 December 2024

## Examples

### Example 1: Simple HTML Schedule

Website structure:
```html
<div class="schedule">
  <div class="event">
    <span class="date">24-11-2024</span>
    <span class="time">14:00-16:00</span>
    <span class="name">Training A1</span>
  </div>
</div>
```

Configuration:
```yaml
scraper_sources:
  - url: "https://club.com/schedule"
    type: training
    method: html
    selectors:
      container: "div.event"
      date: "span.date"
      time: "span.time"
      title: "span.name"

date_format: "%d-%m-%Y"
time_format: "%H:%M"
```

### Example 2: Multiple Sources

```yaml
scraper_sources:
  # Training schedule
  - url: "https://club.com/training"
    type: training
    selectors:
      container: ".training-item"
      date: ".training-date"
      time: ".training-time"
      title: ".training-name"
  
  # Match schedule
  - url: "https://club.com/matches"
    type: match
    selectors:
      container: ".match-row"
      date: ".match-date"
      time: ".match-time"
      title: ".match-title"
```

### Example 3: API Source

```yaml
scraper_sources:
  - url: "https://api.club.com/events"
    type: training
    method: api
    api_headers:
      Authorization: "Bearer YOUR_TOKEN_HERE"
    api_params:
      from: "2024-01-01"
      limit: "100"
```

### Example 4: iCal Feed

```yaml
scraper_sources:
  - url: "https://club.com/calendar.ics"
    type: training
    method: ical
```

## Testing Your Configuration

### Method 1: Dry Run Mode

1. Enable dry run mode in the integration
2. Force a schedule refresh
3. Check the logs for "Found X events"

### Method 2: YAML Validator

Create a test script:

```python
from custom_components.zhc_heating_scheduler.scraper_config_validator import ScraperConfigValidator
import asyncio

config = {
    "scraper_sources": [
        {
            "url": "https://www.example.com/schedule",
            "type": "training",
            "method": "html",
            "selectors": {
                "container": "div.event",
                "date": "span.date",
                "time": "span.time"
            }
        }
    ],
    "date_format": "%d-%m-%Y",
    "time_format": "%H:%M",
    "timezone": "Europe/Amsterdam"
}

# Validate configuration
try:
    validator = ScraperConfigValidator()
    validator.validate_config(config)
    print("✅ Configuration is valid!")
except Exception as e:
    print(f"❌ Configuration error: {e}")

# Test URL accessibility
async def test():
    result = await ScraperConfigValidator.test_url_accessible(
        "https://www.example.com/schedule"
    )
    print(f"URL test: {result}")

asyncio.run(test())
```

## Troubleshooting

### No Events Found

**Check the selectors:**
1. Open the webpage in a browser
2. Inspect an event element
3. Verify your selectors match the actual HTML
4. Test selectors in browser console: `document.querySelectorAll("div.event")`

**Check date/time format:**
1. Look at the actual date/time text on the page
2. Make sure your `date_format` matches exactly
3. Test in Python: `datetime.strptime("31-12-2024", "%d-%m-%Y")`

### Wrong Event Times

**Timezone issues:**
- Make sure `timezone` matches your location
- Check if times on website are in a different timezone

**Date format mismatch:**
- Verify the date format string is correct
- European dates are usually day-first: `"%d-%m-%Y"`
- US dates are usually month-first: `"%m-%d-%Y"`

### Selectors Don't Find Elements

**CSS Selector Tips:**
- Use `.classname` for classes
- Use `#idname` for IDs
- Use `tag.classname` to be more specific
- Use spaces for nested elements: `div.parent span.child`
- Test in browser console first

## Advanced: Multiple Event Types from Same URL

If one URL has both training and matches:

```yaml
scraper_sources:
  # Training events
  - url: "https://club.com/all-events"
    type: training
    selectors:
      container: "div.event.training"
      date: "span.date"
      time: "span.time"
  
  # Match events (same URL, different selector)
  - url: "https://club.com/all-events"
    type: match
    selectors:
      container: "div.event.match"
      date: "span.date"
      time: "span.time"
```

## ZHC-Specific Configuration

For the Zandvoortsche Hockey Club website, see [[zhc-specific|ZHC-Specific Setup]].

## Next Steps

- [[testing|Test Your Scraper]]
- [[troubleshooting|Troubleshooting Scraper Issues]]
- [[../configuration/examples|Configuration Examples]]

## Getting Help

If you can't figure out the selectors:

1. Save the webpage HTML (Right-click → Save Page As)
2. Share it in a [GitHub issue](https://github.com/stefan/zhc-heating-scheduler/issues)
3. We can help you find the right selectors!

---

**Difficulty**: Intermediate  
**Time needed**: 15-30 minutes  
**Prerequisites**: Basic understanding of HTML/CSS

