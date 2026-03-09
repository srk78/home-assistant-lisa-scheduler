---
title: Configuring the Scraper (No Code Required)
tags: [scraper, configuration, advanced]
---

# Configuring the Scraper (No Code Required)

LISA Scheduler supports **configurable scrapers** — you can adapt it to any website using just configuration, without writing any Python code.

## Overview

The configurable scraper system allows you to:

- Scrape multiple URLs (e.g. training schedule + match schedule)
- Use CSS selectors to find schedule data in arbitrary HTML
- Configure date and time formats to match the site
- Support different source methods: HTML, JSON API, and iCal
- Share configurations with other users
- Adjust when a website's structure changes

For background on how the scraper fits into the overall system, see [[overview|Scraper Overview]].

## Basic Configuration

### Via YAML

Add this to your `configuration.yaml`:

```yaml
lisa_scheduler:
  pre_event_minutes: 120

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

Use your browser's Developer Tools to find CSS selectors.

1. **Open the schedule webpage** in Chrome or Firefox.

2. **Open Developer Tools** — right-click on an event and choose **Inspect**, or press `F12`.

3. **Find the event container** — look for the HTML element that wraps each event. Common patterns:
   - `<div class="event">`
   - `<tr>` in a table
   - `<li class="schedule-item">`

4. **Note the CSS selector**:
   - Class: `.event-item` or `div.event`
   - ID: `#schedule-container`
   - Nested: `div.schedule > div.item`

5. **Find date, time, and title elements** inside the container and note their selectors (typically `span.date`, `div.time`, etc.).

## Configuration Options

### Source Configuration

Each source in `scraper_sources` can have:

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `url` | string | Yes | The webpage or API URL to scrape |
| `type` | string | No | Event type: `training`, `match`, or `unknown` |
| `method` | string | No | Scraping method: `html`, `api`, or `ical` |
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

### Date and Time Formats

Configure how dates and times are parsed:

| Option | Description | Example |
|--------|-------------|---------|
| `date_format` | strptime format for dates | `"%d-%m-%Y"` → 31-12-2024 |
| `time_format` | strptime format for times | `"%H:%M"` → 14:30 |
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

### Example 3: JSON API Source

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

### Dry Run Mode

1. Enable `dry_run: true` in the integration configuration.
2. Force a schedule refresh using the `lisa_scheduler.refresh_schedule` service.
3. Check the Home Assistant logs for lines from `lisa_scheduler` — you will see "Found X events" and details of what transitions would fire without them actually being sent.

### Manual Selector Testing

Test selectors directly in the browser console before adding them to the config:

```js
document.querySelectorAll("div.event-item")
```

If this returns the right elements, the selector is correct.

### Python Date Format Testing

Verify your `date_format` string in a Python shell:

```python
from datetime import datetime
datetime.strptime("31-12-2024", "%d-%m-%Y")
```

## Troubleshooting

### No Events Found

**Check the selectors:**
1. Open the webpage in a browser.
2. Inspect an event element.
3. Verify your selectors match the actual HTML.
4. Test in browser console: `document.querySelectorAll("div.event")`

**Check the date/time format:**
1. Look at the actual date/time text on the page.
2. Make sure `date_format` matches exactly.
3. Test in Python as shown above.

### Wrong Event Times

**Timezone issues:**
- Make sure `timezone` matches your local timezone.
- Check whether the website publishes times in a different timezone.

**Date format mismatch:**
- European dates are typically day-first: `"%d-%m-%Y"`
- US dates are typically month-first: `"%m-%d-%Y"`

### Selectors Do Not Find Elements

**CSS selector tips:**
- Use `.classname` for class attributes.
- Use `#idname` for ID attributes.
- Use `tag.classname` to be more specific.
- Use a space for descendant: `div.parent span.child`
- Test in the browser console before adding to config.

## Advanced: Multiple Event Types from the Same URL

If one URL has both training and matches, configure two sources pointing to the same URL with different container selectors:

```yaml
scraper_sources:
  - url: "https://club.com/all-events"
    type: training
    selectors:
      container: "div.event.training"
      date: "span.date"
      time: "span.time"

  - url: "https://club.com/all-events"
    type: match
    selectors:
      container: "div.event.match"
      date: "span.date"
      time: "span.time"
```

## Getting Help

If you cannot figure out the right selectors:

1. Save the webpage HTML (Right-click → Save Page As).
2. Open a [GitHub issue](https://github.com/stefan/lisa-scheduler/issues) and attach the HTML.
3. Include the URL of the schedule page if it is publicly accessible.

The user agent sent by the scraper is `HomeAssistant-LISA-Scheduler/1.0`. Some websites block requests without a recognized user agent — if the scraper returns no content, check whether the page loads correctly with that user agent using a tool like `curl -A "HomeAssistant-LISA-Scheduler/1.0" <url>`.

## Next Steps

- [[overview|Scraper Overview]]
- [[testing|Test Your Scraper]]
- [[troubleshooting|Troubleshooting Scraper Issues]]
- [[../configuration/examples|Configuration Examples]]

---

**Difficulty**: Intermediate
**Time needed**: 15–30 minutes
**Prerequisites**: Basic understanding of HTML and CSS selectors
