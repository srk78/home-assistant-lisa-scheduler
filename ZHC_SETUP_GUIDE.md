# ZHC-Specific Setup Guide

This guide is specifically for the Zandvoortsche Hockey Club (ZHC) integration.

## Overview

The ZHC website uses the LISA sports management system, which loads schedule data dynamically via JavaScript. A custom scraper has been created to handle this.

## Quick Start

### 1. Test the Scraper First

Before setting up in Home Assistant, test that the scraper can fetch data:

```bash
cd /path/to/zhc-heating-scheduler
python test_zhc_scraper.py
```

This will:
- Attempt to fetch training and match schedules
- Show any events found
- Provide debugging information
- Save HTML files for inspection if needed

### 2. Analyze Results

#### If Events Are Found ✅

Great! The scraper is working. Proceed to step 3.

#### If No Events Are Found ⚠️

The website likely uses JavaScript to load content. You need to find the API endpoint:

1. **Open the schedule pages in your browser:**
   - Training: https://www.zandvoortschehockeyclub.nl/trainingsschema
   - Matches: https://www.zandvoortschehockeyclub.nl/wedstrijdschema

2. **Open Developer Tools (F12)**

3. **Go to Network tab**

4. **Reload the page**

5. **Look for XHR/Fetch requests** that load schedule data
   - Look for requests with names like:
     - `schedule`, `events`, `wedstrijd`, `training`
     - API endpoints, JSON files

6. **Click on the request** and examine:
   - Request URL (this is what we need!)
   - Response (should contain schedule data in JSON format)

7. **Update the scraper** with the API endpoint you found (see below)

### 3. Update the Scraper (If Needed)

If you found API endpoints, update `zhc_custom_scraper.py`:

```python
async def _fetch_training_schedule(self, days_ahead: int) -> list[Event]:
    """Fetch training schedule from ZHC."""
    # Replace with actual API endpoint
    api_url = "https://www.zandvoortschehockeyclub.nl/api/training"
    
    return await self._fetch_from_api(api_url, EVENT_TYPE_TRAINING)

async def _fetch_match_schedule(self, days_ahead: int) -> list[Event]:
    """Fetch match schedule from ZHC."""
    # Replace with actual API endpoint
    api_url = "https://www.zandvoortschehockeyclub.nl/api/wedstrijden"
    
    return await self._fetch_from_api(api_url, EVENT_TYPE_MATCH)
```

### 4. Integrate with Coordinator

Update `coordinator.py` to use the custom scraper:

```python
# At the top of coordinator.py, add:
from .zhc_custom_scraper import ZHCCustomScraper

# In ZHCHeatingCoordinator.__init__, replace the scraper initialization:
# Change from:
self.scraper = ScheduleScraper(schedule_url, self._session)

# To:
self.scraper = ZHCCustomScraper(
    training_url=schedule_url,  # or specify both URLs
    match_url="https://www.zandvoortschehockeyclub.nl/wedstrijdschema",
    session=self._session
)
```

### 5. Install in Home Assistant

```bash
# Copy to Home Assistant
cp -r custom_components/zhc_heating_scheduler ~/.homeassistant/custom_components/

# Restart Home Assistant
```

### 6. Configure the Integration

1. Go to Settings → Devices & Services
2. Add Integration → "ZHC Heating Scheduler"
3. Configure:
   - **Schedule URL**: `https://www.zandvoortschehockeyclub.nl/trainingsschema`
   - **Climate Entity**: Your Plugwise thermostat (e.g., `climate.plugwise_sa`)
   - **Pre-heat hours**: 2 (adjust based on building)
   - **Cool-down minutes**: 30
   - **Target temperature**: 20°C
   - **Enable dry run**: ✅ (for initial testing)

4. Click Submit

### 7. Verify It's Working

1. **Check sensors:**
   - Go to Developer Tools → States
   - Search for `sensor.zhc_current_event`
   - Should show upcoming events

2. **Check logs:**
   - Settings → System → Logs
   - Look for "ZHC Heating Scheduler" entries
   - Should see: "Found X training events" and "Found Y match events"

3. **Force refresh:**
   ```yaml
   service: zhc_heating_scheduler.refresh_schedule
   ```
   Check logs for results

4. **If working, disable dry run:**
   - Settings → Devices & Services → ZHC Heating Scheduler → Configure
   - Uncheck "Dry run mode"
   - Now it will actually control your heating!

## Troubleshooting

### Problem: No events found

**Solution 1: Check the test script output**
```bash
python test_zhc_scraper.py
```
Look for error messages in the debug output.

**Solution 2: Find API endpoints**
1. Open browser Developer Tools (F12)
2. Go to Network tab
3. Load the schedule page
4. Look for XHR/Fetch requests
5. Find the one that loads schedule data
6. Update the scraper with that URL

**Solution 3: Check if there are actually events**
- Visit the website manually
- Verify events are visible
- Note the date range

### Problem: Events have wrong times

Check if the times are in UTC vs local time:

```python
# In zhc_custom_scraper.py, when parsing dates:
from datetime import timezone
import pytz

# Convert to local timezone
local_tz = pytz.timezone('Europe/Amsterdam')
start_time = start_time.replace(tzinfo=timezone.utc).astimezone(local_tz)
```

### Problem: Only training OR matches work

One of the URLs might be different. Check:
1. Are both pages loading correctly?
2. Do they use different API endpoints?
3. Update the scraper accordingly

### Problem: Heating not starting

Check:
1. Is `binary_sensor.zhc_scheduler_enabled` ON?
2. Does `sensor.zhc_current_event` show events?
3. Is `sensor.zhc_next_heating_start` in the future?
4. Is dry run mode disabled?

## Alternative: Browser Automation

If the API approach doesn't work, you can use browser automation:

### Install Playwright

```bash
pip install playwright
playwright install chromium
```

### Update scraper to use browser

```python
from playwright.async_api import async_playwright

async def _fetch_with_browser(self, url: str) -> str:
    """Fetch page using headless browser."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        
        # Wait for schedule to load
        await page.wait_for_selector('.schedule-item', timeout=10000)
        
        # Get the rendered HTML
        html = await page.content()
        
        await browser.close()
        return html
```

**Note**: Browser automation is slower and uses more resources, so only use if the API approach fails.

## Configuration Examples

### Small Club (Mostly Training)
```yaml
zhc_heating_scheduler:
  schedule_url: "https://www.zandvoortschehockeyclub.nl/trainingsschema"
  climate_entity: "climate.plugwise_sa"
  pre_heat_hours: 1.5  # Smaller building heats faster
  cool_down_minutes: 20
  target_temperature: 19.0
```

### Large Club (Many Matches)
```yaml
zhc_heating_scheduler:
  schedule_url: "https://www.zandvoortschehockeyclub.nl/trainingsschema"
  climate_entity: "climate.plugwise_sa"
  pre_heat_hours: 3  # Larger building needs more time
  cool_down_minutes: 45
  target_temperature: 20.5
```

## Dashboard Card for ZHC

```yaml
type: vertical-stack
cards:
  - type: entities
    title: ZHC Verwarming
    entities:
      - entity: binary_sensor.zhc_heating_active
        name: Verwarming Status
      - entity: sensor.zhc_current_event
        name: Volgende Event
      - entity: sensor.zhc_next_heating_start
        name: Verwarming Start
      - entity: sensor.zhc_heating_minutes_today
        name: Minuten Vandaag
  
  - type: button
    name: Ververs Schema
    icon: mdi:refresh
    tap_action:
      action: call-service
      service: zhc_heating_scheduler.refresh_schedule
  
  - type: button
    name: Noodverwarming (2 uur)
    icon: mdi:fire
    tap_action:
      action: call-service
      service: zhc_heating_scheduler.set_override
      service_data:
        start_time: "{{ now().isoformat() }}"
        end_time: "{{ (now() + timedelta(hours=2)).isoformat() }}"
```

## Support

If you need help:
1. Run the test script and save the HTML files
2. Check the logs for error messages
3. Create an issue on GitHub with:
   - Test script output
   - Log excerpts
   - Screenshots of Developer Tools Network tab

## Success Checklist

- [ ] Test script shows events
- [ ] Integration installed in Home Assistant
- [ ] Sensors show schedule data
- [ ] Logs show successful schedule refresh
- [ ] Dry run mode logs show correct heating decisions
- [ ] Disabled dry run mode
- [ ] Heating turns on before events
- [ ] Heating turns off after events
- [ ] Dashboard card created
- [ ] Notification automation created (optional)

---

**Good luck with your ZHC heating automation!** 🏑🔥

