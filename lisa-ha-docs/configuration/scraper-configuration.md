---
title: Scraper Configuration
tags: [configuration, scraper]
---

# Scraper Configuration

Configure the scraper system for fetching schedule data.

## Overview

The configurable scraper allows you to:
- Fetch from multiple URLs
- Use CSS selectors
- Support HTML, API, and iCal sources
- Customize date/time parsing

## Quick Link

For complete scraper configuration guide, see:

[[../scraper/configuring-scraper|Configuring the Scraper (No Code Required)]]

## Basic Scraper Configuration

```yaml
zhc_heating_scheduler:
  climate_entity: "climate.plugwise_sa"
  
  scraper_sources:
    - url: "https://club.com/schedule"
      type: training
      method: html
      selectors:
        container: "div.event"
        date: "span.date"
        time: "span.time"
```

## Multiple Sources

```yaml
scraper_sources:
  - url: "https://club.com/training"
    type: training
  - url: "https://club.com/matches"
    type: match
```

## See Also

- [[../scraper/configuring-scraper|Full Scraper Guide]]
- [[../scraper/testing|Testing Your Scraper]]
- [[examples|Configuration Examples]]

---

**Next**: [[../scraper/configuring-scraper|Full Scraper Configuration Guide]]

