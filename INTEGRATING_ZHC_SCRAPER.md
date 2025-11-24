# Integrating the ZHC Custom Scraper

This document shows exactly how to modify the coordinator to use the ZHC custom scraper instead of the generic scraper.

## Option 1: Direct Integration (Recommended)

### Step 1: Modify `coordinator.py`

At the top of `custom_components/zhc_heating_scheduler/coordinator.py`, add this import:

```python
from .zhc_custom_scraper import ZHCCustomScraper
```

### Step 2: Update the scraper initialization

Find this line in the `ZHCHeatingCoordinator.__init__` method (around line 50):

```python
self.scraper = ScheduleScraper(schedule_url, self._session)
```

Replace it with:

```python
# Use ZHC custom scraper for both training and match schedules
self.scraper = ZHCCustomScraper(
    training_url=schedule_url,
    match_url="https://www.zandvoortschehockeyclub.nl/wedstrijdschema",
    session=self._session
)
```

### Step 3: Test

1. Copy the modified integration to Home Assistant:
   ```bash
   cp -r custom_components/zhc_heating_scheduler ~/.homeassistant/custom_components/
   ```

2. Restart Home Assistant

3. Configure the integration with:
   - Schedule URL: `https://www.zandvoortschehockeyclub.nl/trainingsschema`

4. Check logs for: "Found X training events" and "Found Y match events"

## Option 2: Configuration-Based Selection

If you want to keep both scrapers and select via config, follow these steps:

### Step 1: Add config option in `const.py`

```python
# Add to const.py
CONF_USE_ZHC_SCRAPER = "use_zhc_scraper"
DEFAULT_USE_ZHC_SCRAPER = True
```

### Step 2: Update `config_flow.py`

Add the option to the form:

```python
vol.Optional(
    CONF_USE_ZHC_SCRAPER,
    default=DEFAULT_USE_ZHC_SCRAPER,
): bool,
```

### Step 3: Modify `coordinator.py`

```python
# At the top
from .zhc_custom_scraper import ZHCCustomScraper

# In __init__, add parameter:
use_zhc_scraper: bool = True,

# Replace scraper initialization with:
if use_zhc_scraper:
    self.scraper = ZHCCustomScraper(
        training_url=schedule_url,
        match_url="https://www.zandvoortschehockeyclub.nl/wedstrijdschema",
        session=self._session
    )
else:
    self.scraper = ScheduleScraper(schedule_url, self._session)
```

### Step 4: Update `__init__.py`

Pass the config value to the coordinator:

```python
coordinator = ZHCHeatingCoordinator(
    # ... existing parameters ...
    entry.data.get(CONF_USE_ZHC_SCRAPER, DEFAULT_USE_ZHC_SCRAPER),
)
```

## Option 3: Separate ZHC Integration

Create a completely separate integration for ZHC (most maintainable):

### Step 1: Copy the integration folder

```bash
cp -r custom_components/zhc_heating_scheduler custom_components/zhc_heater
```

### Step 2: Update manifest.json

```json
{
  "domain": "zhc_heater",
  "name": "ZHC Heater",
  ...
}
```

### Step 3: Hardcode ZHC scraper in coordinator.py

```python
# Always use ZHC scraper
self.scraper = ZHCCustomScraper(
    training_url=schedule_url,
    match_url="https://www.zandvoortschehockeyclub.nl/wedstrijdschema",
    session=self._session
)
```

### Step 4: Simplify config flow

Remove the schedule URL input and hardcode it to ZHC's URLs.

## Testing the Integration

### Test Script

Before integrating, always test the scraper:

```bash
python test_zhc_scraper.py
```

Expected output:
```
Found X events from ZHC (next 14 days)
📅 Training events: X
🏑 Match events: Y
```

### Enable Debug Logging

In Home Assistant `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.zhc_heating_scheduler: debug
    custom_components.zhc_heating_scheduler.zhc_custom_scraper: debug
```

### Check Service Call

```yaml
service: zhc_heating_scheduler.refresh_schedule
```

Then check logs for:
```
INFO Fetching training schedule from ZHC
INFO Found X training events
INFO Fetching match schedule from ZHC
INFO Found Y match events
INFO Total: Z events from ZHC (next 14 days)
```

## Troubleshooting Integration

### Import Error: Cannot import ZHCCustomScraper

**Cause**: The file isn't in the right location

**Solution**:
```bash
# Verify file exists
ls custom_components/zhc_heating_scheduler/zhc_custom_scraper.py

# If missing, copy it there
cp zhc_custom_scraper.py custom_components/zhc_heating_scheduler/
```

### Error: No events found

**Cause**: The website structure changed or requires API access

**Solution**: Run the test script and check the debug output:
```bash
python test_zhc_scraper.py
```

Follow the troubleshooting steps in the test output.

### Error: Session is closed

**Cause**: Scraper trying to use closed aiohttp session

**Solution**: Ensure session is passed correctly:
```python
self.scraper = ZHCCustomScraper(
    training_url=schedule_url,
    match_url="https://www.zandvoortschehockeyclub.nl/wedstrijdschema",
    session=self._session  # Important!
)
```

## Verification Checklist

After integration:

- [ ] Test script shows events
- [ ] No import errors in logs
- [ ] Integration loads successfully
- [ ] Refresh schedule service works
- [ ] Sensors show upcoming events
- [ ] Logs show "Found X training events"
- [ ] Logs show "Found Y match events"
- [ ] Events have correct dates/times
- [ ] Both training and matches appear
- [ ] Heating windows calculated correctly

## Complete Example

Here's the complete modified section of `coordinator.py`:

```python
# At the top of coordinator.py (around line 12)
from .scraper import Event, ScheduleScraper
from .zhc_custom_scraper import ZHCCustomScraper  # Add this line

class ZHCHeatingCoordinator(DataUpdateCoordinator):
    """Coordinator to manage heating schedule and device control."""

    def __init__(
        self,
        hass: HomeAssistant,
        schedule_url: str,
        climate_entity: str,
        pre_heat_hours: int,
        cool_down_minutes: int,
        target_temperature: float,
        scan_interval: int,
        enabled: bool = True,
        dry_run: bool = False,
    ):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=60),
        )

        self.schedule_url = schedule_url
        self.climate_entity = climate_entity
        self.target_temperature = target_temperature
        self.scan_interval = scan_interval
        self.enabled = enabled
        self.dry_run = dry_run

        # Initialize scheduler
        self.scheduler = HeatingScheduler(pre_heat_hours, cool_down_minutes)

        # Initialize scraper - USE ZHC CUSTOM SCRAPER
        self._session = aiohttp.ClientSession()
        self.scraper = ZHCCustomScraper(
            training_url=schedule_url,
            match_url="https://www.zandvoortschehockeyclub.nl/wedstrijdschema",
            session=self._session
        )

        # ... rest of __init__ ...
```

That's it! The integration will now use the ZHC-specific scraper.

## Rolling Back

If something goes wrong, revert the changes:

```python
# Back to generic scraper
self.scraper = ScheduleScraper(schedule_url, self._session)
```

Then restart Home Assistant.

