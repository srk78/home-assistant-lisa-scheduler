---
title: No Events Found
tags: [troubleshooting, scraper, events]
---

# No Events Found

Troubleshooting guide when the scheduler can't find events in your schedule.

## Symptoms

- `sensor.zhc_current_event` shows "No events" or "No upcoming events"
- `sensor.zhc_total_heating_windows` is 0
- Logs show "Found 0 events"
- Heating never starts

## Quick Diagnosis

### Step 1: Verify Website Works

1. Open the schedule URL in your browser
2. Confirm events are visible
3. Note the date/time format used
4. Check if JavaScript loads the schedule

### Step 2: Check Logs

Settings → System → Logs, search for "zhc"

Look for:
- "Fetching schedule from..."
- "Found X events"
- Any error messages

### Step 3: Test Manual Refresh

```yaml
service: zhc_heating_scheduler.refresh_schedule
```

Check logs immediately after.

## Common Causes & Solutions

### Cause 1: Website Uses JavaScript

**Symptom**: Events visible in browser but not found by scraper

**Why**: Default scraper only parses static HTML, not JavaScript-loaded content

**Solution**: Configure custom scraper

See [[../scraper/configuring-scraper|Scraper Configuration Guide]]

### Cause 2: Wrong CSS Selectors

**Symptom**: Using scraper configuration but still no events

**Solution**: Find correct CSS selectors

1. Open website in browser
2. Right-click event → Inspect
3. Note the HTML structure
4. Update selectors in configuration

Example:
```yaml
scraper_sources:
  - url: "https://club.com/schedule"
    selectors:
      container: "div.event-item"  # Update this
      date: "span.date-text"        # And this
      time: "span.time-text"        # And this
```

### Cause 3: Date Format Mismatch

**Symptom**: Logs show "Could not parse datetime"

**Solution**: Match date format to website

Check what format website uses:
- `31-12-2024` → `date_format: "%d-%m-%Y"`
- `2024-12-31` → `date_format: "%Y-%m-%d"`
- `12/31/2024` → `date_format: "%m/%d/%Y"`

```yaml
zhc_heating_scheduler:
  date_format: "%d-%m-%Y"  # Adjust to match
  time_format: "%H:%M"
```

### Cause 4: Events Outside Date Range

**Symptom**: Events exist but are too far in future

**Solution**: Scraper only fetches events within next 14 days by default

Check if your next event is within 14 days.

### Cause 5: Website Blocking Requests

**Symptom**: Logs show connection errors or timeouts

**Solution**:
1. Check website is accessible
2. Verify no firewall blocking
3. Check if website requires authentication
4. Try different user agent

### Cause 6: Wrong Event Type Selector

**Symptom**: Some events found but not all

**Solution**: Check if training vs matches use different selectors

```yaml
scraper_sources:
  - url: "https://club.com/schedule"
    type: training
    selectors:
      container: "div.training-event"  # Different class
  - url: "https://club.com/schedule"
    type: match
    selectors:
      container: "div.match-event"     # Different class
```

## Step-by-Step Troubleshooting

### Step 1: Enable Debug Logging

```yaml
logger:
  logs:
    custom_components.zhc_heating_scheduler: debug
    custom_components.zhc_heating_scheduler.scraper: debug
```

Restart Home Assistant.

### Step 2: Analyze HTML Structure

Save the webpage:
1. Open schedule URL in browser
2. Right-click → "Save Page As"
3. Save as HTML file
4. Open in text editor
5. Search for date/time of known event
6. Note the HTML structure around it

### Step 3: Configure Scraper

Based on HTML structure, configure scraper.

See [[../scraper/configuring-scraper|Full Scraper Configuration Guide]]

### Step 4: Test Configuration

```yaml
service: zhc_heating_scheduler.refresh_schedule
```

Check logs for improvement.

### Step 5: Iterate

Adjust selectors until events are found.

## Testing Your Scraper

### Use Browser Console

Test CSS selectors in browser:

```javascript
// Test container selector
document.querySelectorAll("div.event-item")

// Should return array of elements
```

### Check Selector Matches

```javascript
// Test if selector finds anything
document.querySelector("div.event-item") !== null
```

## ZHC-Specific Solution

For Zandvoortsche Hockey Club, see [[../scraper/zhc-specific|ZHC-Specific Setup]]

## Advanced Solutions

### Option 1: API Instead of HTML

If club has an API:

```yaml
scraper_sources:
  - url: "https://api.club.com/events"
    method: api
    type: training
```

### Option 2: iCal Feed

If club publishes iCal:

```yaml
scraper_sources:
  - url: "https://club.com/calendar.ics"
    method: ical
    type: training
```

### Option 3: Browser Automation

For complex JavaScript sites (advanced):

Requires Playwright installation - see developer docs.

## Getting Help

### Information to Provide

When asking for help, provide:

1. Schedule URL (if public)
2. Screenshot of schedule page
3. Saved HTML of schedule page
4. Current scraper configuration
5. Relevant log entries
6. Home Assistant version

### Where to Ask

- [GitHub Issues](https://github.com/stefan/zhc-heating-scheduler/issues)
- [Home Assistant Forum](https://community.home-assistant.io/)

## Checklist

- [ ] Website loads in browser and shows events
- [ ] Debug logging enabled
- [ ] Manual refresh tested
- [ ] Logs checked for errors
- [ ] HTML structure analyzed
- [ ] Scraper configured (if needed)
- [ ] CSS selectors tested in browser
- [ ] Date format matches website
- [ ] Time format matches website
- [ ] Events are within 14 days

## See Also

- [[../scraper/configuring-scraper|Scraper Configuration]]
- [[../scraper/testing|Test Your Scraper]]
- [[debugging|Debug Logging]]
- [[common-issues|Common Issues]]

---

**Difficulty**: Intermediate  
**Time needed**: 30-60 minutes  
**Next**: [[../scraper/configuring-scraper|Configure Scraper]]

