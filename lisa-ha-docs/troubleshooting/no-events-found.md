---
title: No Events Found
tags: [troubleshooting, scraper, events]
---

# No Events Found

Troubleshooting guide when the scheduler can't find events in your schedule.

## Symptoms

- `sensor.lisa_current_event` shows "No events" or "No upcoming events"
- `sensor.lisa_total_event_windows` is 0
- Logs show "Found 0 events"
- No HA bus events are ever fired

## Quick Diagnosis

### Step 1: Verify the Website Works

1. Open the schedule URL in your browser
2. Confirm events are visible
3. Note the date/time format used
4. Check whether JavaScript is needed to load the schedule

### Step 2: Check Logs

Settings → System → Logs, search for `lisa_scheduler`.

Look for:
- "Fetching schedule from..."
- "Found X events"
- Any error messages

### Step 3: Test Manual Refresh

In **Developer Tools** → **Services**, call:

```yaml
service: lisa_scheduler.refresh_schedule
```

Check logs immediately after.

## Common Causes & Solutions

### Cause 1: Website Uses JavaScript

**Symptom**: Events are visible in the browser but not found by the scraper

**Why**: The default scraper only parses static HTML, not JavaScript-loaded content

**Solution**: Configure a custom scraper with an API or iCal source, or use CSS selectors targeting the pre-rendered HTML if available

See [[../scraper/configuring-scraper|Scraper Configuration Guide]]

### Cause 2: Wrong CSS Selectors

**Symptom**: Scraper is configured but still finds no events

**Solution**: Find the correct CSS selectors

1. Open the website in your browser
2. Right-click on an event entry → Inspect
3. Note the HTML structure
4. Update selectors in the integration configuration

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

**Solution**: Match the date format to the website

Check what format the website uses:
- `31-12-2024` → `date_format: "%d-%m-%Y"`
- `2024-12-31` → `date_format: "%Y-%m-%d"`
- `12/31/2024` → `date_format: "%m/%d/%Y"`

```yaml
lisa_scheduler:
  date_format: "%d-%m-%Y"  # Adjust to match
  time_format: "%H:%M"
```

### Cause 4: Events Outside Date Range

**Symptom**: Events exist on the website but are not returned

**Solution**: The scraper only fetches events within the next 14 days by default. Check whether your next event falls within that window.

### Cause 5: Website Blocking Requests

**Symptom**: Logs show connection errors or timeouts

**Solution**:
1. Confirm the website is accessible from your HA host (not just your local machine)
2. Verify no firewall is blocking outbound requests
3. Check whether the website requires authentication
4. Try a different user agent string

### Cause 6: Wrong Event Type Selector

**Symptom**: Some events are found but not all

**Solution**: Check whether training sessions and matches use different HTML classes

```yaml
scraper_sources:
  - url: "https://club.com/schedule"
    type: training
    selectors:
      container: "div.training-event"
  - url: "https://club.com/schedule"
    type: match
    selectors:
      container: "div.match-event"
```

## Step-by-Step Troubleshooting

### Step 1: Enable Debug Logging

```yaml
logger:
  logs:
    custom_components.lisa_scheduler: debug
    custom_components.lisa_scheduler.scraper: debug
```

Restart Home Assistant.

### Step 2: Analyze HTML Structure

1. Open the schedule URL in your browser
2. Right-click → "Save Page As" and save as HTML
3. Open the file in a text editor
4. Search for the date or time of a known upcoming event
5. Note the HTML structure surrounding it

### Step 3: Configure the Scraper

Based on the HTML structure, configure the scraper.

See [[../scraper/configuring-scraper|Full Scraper Configuration Guide]]

### Step 4: Test the Configuration

Call `lisa_scheduler.refresh_schedule` and check the logs for improvement.

### Step 5: Iterate

Adjust selectors until events are found. Use the browser console to test selectors before editing the configuration.

## Testing Your Selectors

### Use Browser Console

Test CSS selectors directly in the browser before editing config:

```javascript
// Test container selector — should return a non-empty NodeList
document.querySelectorAll("div.event-item")

// Test whether a selector matches anything
document.querySelector("div.event-item") !== null
```

## Advanced Solutions

### Option 1: API Instead of HTML

If the club has an API endpoint:

```yaml
scraper_sources:
  - url: "https://api.club.com/events"
    method: api
    type: training
```

### Option 2: iCal Feed

If the club publishes an iCal feed:

```yaml
scraper_sources:
  - url: "https://club.com/calendar.ics"
    method: ical
    type: training
```

### Option 3: Browser Automation

For complex JavaScript-heavy sites (advanced):

Requires Playwright installation — see developer docs.

## Getting Help

### Information to Provide

When asking for help, provide:

1. Schedule URL (if public)
2. Screenshot of the schedule page
3. Saved HTML of the schedule page
4. Current scraper configuration
5. Relevant log entries (with debug logging enabled)
6. Home Assistant version

### Where to Ask

- [GitHub Issues](https://github.com/stefan/lisa-scheduler/issues)
- [Home Assistant Forum](https://community.home-assistant.io/)

## Checklist

- [ ] Website loads in browser and shows upcoming events
- [ ] Debug logging enabled
- [ ] Manual refresh tested and logs reviewed
- [ ] HTML structure analyzed
- [ ] Scraper configured (if needed)
- [ ] CSS selectors tested in browser console
- [ ] Date format matches website
- [ ] Time format matches website
- [ ] Events are within the next 14 days

## See Also

- [[../scraper/configuring-scraper|Scraper Configuration]]
- [[../scraper/testing|Test Your Scraper]]
- [[debugging|Debug Logging]]
- [[common-issues|Common Issues]]

---

**Difficulty**: Intermediate
**Time needed**: 30–60 minutes
**Next**: [[../scraper/configuring-scraper|Configure Scraper]]
