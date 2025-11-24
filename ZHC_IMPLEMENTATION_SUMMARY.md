# ZHC Custom Scraper Implementation Summary

## What Was Added

A custom scraper specifically for the Zandvoortsche Hockey Club (ZHC) website has been implemented.

### New Files Created

1. **`zhc_custom_scraper.py`** - Custom scraper for ZHC's LISA-powered website
   - Handles both training schedule and match schedule
   - Attempts multiple strategies to extract events:
     - API endpoint detection
     - Embedded JSON data extraction
     - HTML parsing fallback
   - Combines events from both sources

2. **`test_zhc_scraper.py`** - Test script to verify scraper functionality
   - Tests both training and match schedule fetching
   - Shows debugging information
   - Saves HTML files for manual inspection
   - Provides troubleshooting guidance

3. **`ZHC_SETUP_GUIDE.md`** - Complete setup guide for ZHC
   - Step-by-step instructions
   - Troubleshooting section
   - Configuration examples
   - Dashboard card example in Dutch

4. **`INTEGRATING_ZHC_SCRAPER.md`** - Technical integration guide
   - How to modify coordinator.py
   - Multiple integration options
   - Verification checklist
   - Complete code examples

### Updated Files

- **`README.md`** - Added ZHC-specific notes and links to guides

## Why a Custom Scraper Was Needed

The ZHC website (https://www.zandvoortschehockeyclub.nl) uses the LISA sports management system, which:

1. **Loads content dynamically** via JavaScript
2. **Does not include schedule data** in the initial HTML response
3. **Requires** either:
   - Finding the API endpoint that JavaScript calls
   - Using browser automation to render JavaScript
   - Extracting embedded data from script tags

The generic scraper cannot handle this because it only parses static HTML.

## How the ZHC Scraper Works

### Strategy 1: API Detection (Preferred)

1. Fetches the page HTML
2. Searches for API endpoints in JavaScript code
3. Makes direct API calls to fetch schedule data
4. Parses JSON responses

### Strategy 2: Embedded Data Extraction

1. Searches for JSON data embedded in `<script>` tags
2. Extracts and parses the JSON
3. Converts to Event objects

### Strategy 3: HTML Parsing (Fallback)

1. Parses any visible schedule elements in HTML
2. Extracts dates, times, and event details
3. Creates Event objects

### Dual Schedule Support

The scraper fetches from **two URLs**:

- **Training**: https://www.zandvoortschehockeyclub.nl/trainingsschema
- **Matches**: https://www.zandvoortschehockeyclub.nl/wedstrijdschema

Both schedules are combined into a single event list.

## Current Status

### ✅ Implemented

- [x] Custom scraper class with multiple strategies
- [x] Support for both training and match schedules
- [x] API endpoint detection logic
- [x] JSON data extraction
- [x] HTML parsing fallback
- [x] Test script with debugging
- [x] Complete documentation
- [x] Integration guides
- [x] Dutch language examples

### ⚠️ Needs Testing

- [ ] **Test with actual ZHC website** - The scraper needs to be tested with real data
- [ ] **Verify API endpoints** - May need to find actual API URLs
- [ ] **Check date/time parsing** - Ensure Dutch date formats work correctly
- [ ] **Validate event types** - Confirm training vs match detection

### 🔧 May Need Adjustment

The scraper is **designed to be flexible**, but you may need to:

1. **Add specific API endpoints** if found
2. **Adjust date/time parsing** for Dutch formats
3. **Update selectors** if HTML structure is specific
4. **Handle authentication** if required

## Next Steps

### Step 1: Test the Scraper (REQUIRED)

```bash
cd /path/to/zhc-heating-scheduler
python test_zhc_scraper.py
```

**Expected outcomes:**

#### Best Case: Events Found ✅
```
Found 25 events from ZHC (next 14 days)
📅 Training events: 18
🏑 Match events: 7
```
→ Scraper works! Proceed to Step 2.

#### Likely Case: No Events, Need API ⚠️
```
WARNING: No events found!
The page may use JavaScript to load content dynamically
```

→ You need to find the API endpoint:

1. Open https://www.zandvoortschehockeyclub.nl/trainingsschema in browser
2. Open Developer Tools (F12) → Network tab
3. Reload the page
4. Look for XHR/Fetch requests containing schedule data
5. Note the URL (e.g., `https://api.lisa.nl/schedule/...`)
6. Update `zhc_custom_scraper.py` with that URL

See detailed instructions in [ZHC_SETUP_GUIDE.md](ZHC_SETUP_GUIDE.md).

### Step 2: Update Coordinator (if scraper works)

Follow the guide in [INTEGRATING_ZHC_SCRAPER.md](INTEGRATING_ZHC_SCRAPER.md):

Quick version:
```python
# In coordinator.py, add import:
from .zhc_custom_scraper import ZHCCustomScraper

# Replace scraper initialization:
self.scraper = ZHCCustomScraper(
    training_url=schedule_url,
    match_url="https://www.zandvoortschehockeyclub.nl/wedstrijdschema",
    session=self._session
)
```

### Step 3: Install in Home Assistant

```bash
cp -r custom_components/zhc_heating_scheduler ~/.homeassistant/custom_components/
```

Restart Home Assistant.

### Step 4: Configure

1. Add Integration: "ZHC Heating Scheduler"
2. Schedule URL: `https://www.zandvoortschehockeyclub.nl/trainingsschema`
3. Climate Entity: Your Plugwise thermostat
4. Enable dry run mode for testing

### Step 5: Verify

```yaml
# Call this service
service: zhc_heating_scheduler.refresh_schedule
```

Check logs for:
```
INFO: Found X training events
INFO: Found Y match events
INFO: Total: Z events from ZHC
```

### Step 6: Fine-tune

1. Adjust pre-heat time (test with dry run)
2. Adjust cool-down time
3. Set target temperature
4. Disable dry run when ready

## Troubleshooting Guides

Comprehensive troubleshooting in:

- **ZHC_SETUP_GUIDE.md** - User-focused troubleshooting
- **INTEGRATING_ZHC_SCRAPER.md** - Technical troubleshooting
- **test_zhc_scraper.py** - Provides debugging output

Common issues and solutions are documented in each guide.

## Alternative: Browser Automation

If the API approach doesn't work at all, you can use Playwright for browser automation:

```bash
pip install playwright
playwright install chromium
```

Then modify the scraper to use a headless browser. Example code is in [ZHC_SETUP_GUIDE.md](ZHC_SETUP_GUIDE.md).

⚠️ **Note**: Browser automation is slower and more resource-intensive. Only use as a last resort.

## Key Files Reference

| File | Purpose |
|------|---------|
| `zhc_custom_scraper.py` | The custom scraper implementation |
| `test_zhc_scraper.py` | Test and debug the scraper |
| `ZHC_SETUP_GUIDE.md` | Complete user guide for ZHC |
| `INTEGRATING_ZHC_SCRAPER.md` | How to integrate with coordinator |
| `coordinator.py` | Needs modification to use custom scraper |

## Example Dashboard Card (Dutch)

```yaml
type: vertical-stack
cards:
  - type: entities
    title: ZHC Clubhuis Verwarming
    entities:
      - entity: binary_sensor.zhc_heating_active
        name: Verwarming
      - entity: sensor.zhc_current_event
        name: Volgende Event
      - entity: sensor.zhc_next_heating_start
        name: Start Verwarming
      - entity: sensor.zhc_heating_minutes_today
        name: Vandaag (minuten)
```

## Questions to Answer

Before going live, verify:

1. **Does the test script find events?**
   - If yes → Proceed with integration
   - If no → Find API endpoints first

2. **Are the dates/times correct?**
   - Check timezone (should be Europe/Amsterdam)
   - Verify date format parsing

3. **Are both training and matches found?**
   - If only one works, check the other URL
   - May have different API endpoints

4. **How far ahead are events available?**
   - Adjust `days_ahead` parameter if needed
   - Default is 14 days

## Success Criteria

The implementation is successful when:

- [x] ✅ Custom scraper code written
- [x] ✅ Test script created
- [x] ✅ Documentation written
- [ ] ⏳ Test script shows events from ZHC website
- [ ] ⏳ Coordinator integrated with custom scraper
- [ ] ⏳ Integration loads in Home Assistant
- [ ] ⏳ Sensors show schedule data
- [ ] ⏳ Heating control works correctly

## Getting Help

If you encounter issues:

1. **Run the test script first**: `python test_zhc_scraper.py`
2. **Check the output**: Follow the troubleshooting suggestions
3. **Save HTML files**: Use the script's save option
4. **Check browser DevTools**: Network tab for API calls
5. **Read the guides**: ZHC_SETUP_GUIDE.md has detailed steps
6. **Create an issue**: Include test script output and logs

## Summary

A complete, flexible custom scraper has been implemented for the ZHC website. It's ready to use once you:

1. **Test it** with the real website
2. **Find API endpoints** (if needed)
3. **Integrate** with the coordinator
4. **Configure** in Home Assistant

The scraper is designed to handle the dynamic content loading of the LISA system and provides multiple fallback strategies.

**Next immediate action**: Run `python test_zhc_scraper.py` to see if it works with the current implementation or if you need to add specific API endpoints.

Good luck! 🏑🔥

