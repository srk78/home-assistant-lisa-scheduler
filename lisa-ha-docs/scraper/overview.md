---
title: Scraper Overview
tags: [scraper, architecture]
---

# Scraper Overview

## What Scraping Means Here

LISA Scheduler needs to know when events are scheduled so it can fire Home Assistant bus events at the right times. Because most sports clubs publish their schedules on a website rather than via an API, the integration fetches that schedule automatically.

"Scraping" in this context means: periodically fetching a URL (HTML page, JSON API response, or iCal feed), parsing the content to extract event dates and times, and storing the results internally. No browser is involved — it is a direct HTTP request, similar to what `curl` does.

The scraper runs on a configurable interval (default: every 6 hours). Between fetches, the coordinator uses the cached schedule to determine whether to fire transition events.

## The Scraper Hierarchy

The integration ships with two scraper classes, each building on the one below it.

### ScheduleScraper (base)

`ScheduleScraper` is the generic base class. It accepts a single `schedule_url` and attempts to parse the response using a sequence of fallback strategies:

1. HTML table parsing
2. HTML list parsing
3. HTML calendar/grid parsing

It uses `python-dateutil` for flexible date parsing, so it handles a wide range of date formats without explicit configuration. This scraper is the right choice when your club's website has a straightforward HTML schedule page.

**When to use**: Set `schedule_url` in the integration config and leave `scraper_sources` unset. The coordinator will use `ScheduleScraper` automatically.

### ConfigurableScraper

`ConfigurableScraper` extends `ScheduleScraper` and adds support for multiple sources and explicit CSS selectors. It supports three fetch methods:

- **`html`** — fetches an HTML page and uses CSS selectors you define to locate event containers, dates, times, and titles.
- **`api`** — fetches a JSON API endpoint, with optional custom headers and query parameters.
- **`ical`** — fetches an iCal (`.ics`) feed and parses it using the `icalendar` library.

For `api` and `ical` sources, any timezone-aware datetimes from the source are normalised: they are converted to the configured timezone and then stripped of timezone info, so all datetimes throughout the system are naive local datetimes.

**When to use**: Set `scraper_sources` in the integration config. The coordinator detects this key and switches to `ConfigurableScraper` automatically.

### Custom subclasses

If `ConfigurableScraper` cannot handle your site's structure, create a custom subclass of `ScheduleScraper` outside the shipped integration and override `_parse_html()`. The packaged integration intentionally keeps only the generic and configurable scraper paths so runtime scraper selection stays explicit and predictable.

## Choosing a Scraper

```
Does your site have a simple HTML schedule table or list?
  Yes → Use schedule_url (ScheduleScraper, no extra config)
  No  → Does your site have a CSS-selectable structure, API, or iCal feed?
          Yes → Use scraper_sources (ConfigurableScraper)
          No  → Write and maintain a custom subclass of ScheduleScraper outside the integration
```

## How Scraped Events Become HA Events

Once the scraper returns a list of raw events, the coordinator processes them as follows:

1. **EventWindow creation** — each event is converted to an `EventWindow`:
   - `window_start = event_start − pre_event_minutes`
   - `window_end = event_end`

2. **Merging** — overlapping windows are merged into a single window. This prevents redundant transition events when two events are close together.

3. **Transition detection** — every 60 seconds the coordinator checks whether `is_window_active` or `is_event_active` has changed since the last check. On a transition, it fires the appropriate HA bus event:
   - `lisa_scheduler_window_started` — the pre-event window just opened
   - `lisa_scheduler_event_started` — the actual event just began
   - `lisa_scheduler_event_ended` — the event just ended
   - `lisa_scheduler_window_ended` — the window just closed
   - `lisa_scheduler_pre_event_trigger` — a configured pre-event trigger time was reached

4. **State exposure** — the current coordinator data is read by sensors and binary sensors and reflected in entity states.

## Further Reading

- [[configuring-scraper|Configuring the Scraper (No Code Required)]] — full reference for `scraper_sources`, CSS selectors, API, and iCal options
- [[../usage/automations|Automation Examples]] — how to respond to the HA events the coordinator fires
- [[../configuration/basic-settings|Basic Settings]] — `pre_event_minutes`, `scan_interval`, and other top-level options
