# Scraper Customization Guide

The ZHC Heating Scheduler includes a generic HTML scraper that attempts to parse common schedule formats. However, every website is different, and you may need to customize the scraper for your specific site.

## When to Customize

You should customize the scraper if:

- The integration reports "No events found" but your website has events
- Events are parsed incorrectly (wrong times, dates, or event types)
- Your website uses a non-standard format

## Understanding the Default Scraper

The default scraper tries three strategies:

1. **Table-based schedules**: Looks for `<table>` elements with date, time, and event information
2. **List-based schedules**: Looks for `<ul>`, `<ol>`, or `<div>` elements with class names containing "schedule", "event", or "calendar"
3. **Calendar-based schedules**: Looks for calendar-style layouts with day cells

## Analyzing Your Website

### Step 1: Inspect the HTML

1. Open your club's schedule page in a web browser
2. Right-click on an event and select "Inspect" or "Inspect Element"
3. Look at the HTML structure around the event

### Step 2: Identify Patterns

Look for:
- Container elements (divs, sections, etc.)
- Repeating patterns for each event
- How dates are formatted
- How times are displayed
- Event type indicators (training, match, etc.)

## Example: Custom Scraper for a Specific Website

Let's say your website has this HTML structure:

```html
<div class="agenda">
  <div class="agenda-item">
    <span class="datum">24-11-2024</span>
    <span class="tijd">14:00 - 16:00</span>
    <span class="activiteit">Training A1</span>
    <span class="type">training</span>
  </div>
  <div class="agenda-item">
    <span class="datum">25-11-2024</span>
    <span class="tijd">10:00 - 12:00</span>
    <span class="activiteit">Wedstrijd vs HC Rotterdam</span>
    <span class="type">wedstrijd</span>
  </div>
</div>
```

### Creating a Custom Scraper

Create a file `custom_scraper.py` in your Home Assistant config directory:

```python
"""Custom scraper for ZHC schedule."""
from datetime import datetime
from bs4 import BeautifulSoup

from custom_components.zhc_heating_scheduler.scraper import (
    ScheduleScraper,
    Event,
    EVENT_TYPE_TRAINING,
    EVENT_TYPE_MATCH,
    EVENT_TYPE_UNKNOWN,
)


class ZHCCustomScraper(ScheduleScraper):
    """Custom scraper for ZHC website."""
    
    def _parse_html(self, html: str) -> list[Event]:
        """Parse the ZHC schedule page."""
        soup = BeautifulSoup(html, "html.parser")
        events = []
        
        # Find all agenda items
        agenda_items = soup.find_all("div", class_="agenda-item")
        
        for item in agenda_items:
            try:
                # Extract date
                date_elem = item.find("span", class_="datum")
                if not date_elem:
                    continue
                date_str = date_elem.get_text(strip=True)
                
                # Extract time
                time_elem = item.find("span", class_="tijd")
                if not time_elem:
                    continue
                time_str = time_elem.get_text(strip=True)
                
                # Extract activity name
                activity_elem = item.find("span", class_="activiteit")
                title = activity_elem.get_text(strip=True) if activity_elem else ""
                
                # Determine event type
                type_elem = item.find("span", class_="type")
                type_text = type_elem.get_text(strip=True).lower() if type_elem else ""
                
                if "training" in type_text:
                    event_type = EVENT_TYPE_TRAINING
                elif "wedstrijd" in type_text or "match" in type_text:
                    event_type = EVENT_TYPE_MATCH
                else:
                    event_type = EVENT_TYPE_UNKNOWN
                
                # Parse datetime
                start_time, end_time = self._parse_datetime(date_str, time_str)
                
                if start_time and end_time:
                    event = Event(
                        event_type=event_type,
                        start_time=start_time,
                        end_time=end_time,
                        title=title,
                    )
                    events.append(event)
                    
            except Exception as e:
                self._logger.warning(f"Error parsing agenda item: {e}")
                continue
        
        return events
```

## Installing Your Custom Scraper

### Option 1: Modify the Integration

1. Copy your custom scraper code into:
   ```
   custom_components/zhc_heating_scheduler/scraper.py
   ```
2. Replace the `CustomScheduleScraper` class with your implementation
3. Restart Home Assistant

### Option 2: Package as Add-on

For cleaner separation, create a separate Python package and import it:

1. Create `config/custom_scrapers/zhc_custom.py`
2. Add your scraper code
3. Modify `coordinator.py` to use your custom scraper:

```python
from custom_scrapers.zhc_custom import ZHCCustomScraper

# In coordinator __init__:
self.scraper = ZHCCustomScraper(schedule_url, self._session)
```

## Testing Your Custom Scraper

### Method 1: Python Script

Create a test script to verify your scraper works:

```python
"""Test script for custom scraper."""
import asyncio
import aiohttp
from datetime import datetime

from custom_components.zhc_heating_scheduler.scraper import CustomScheduleScraper


async def test_scraper():
    """Test the custom scraper."""
    url = "https://your-club-website.com/schedule"
    
    async with aiohttp.ClientSession() as session:
        scraper = CustomScheduleScraper(url, session)
        events = await scraper.fetch_schedule(days_ahead=14)
        
        print(f"Found {len(events)} events:")
        for event in events:
            print(f"  - {event.title}")
            print(f"    Type: {event.event_type}")
            print(f"    Start: {event.start_time}")
            print(f"    End: {event.end_time}")
            print()


if __name__ == "__main__":
    asyncio.run(test_scraper())
```

Run it:
```bash
python test_scraper.py
```

### Method 2: Home Assistant Logs

1. Enable debug logging in `configuration.yaml`:
   ```yaml
   logger:
     logs:
       custom_components.zhc_heating_scheduler.scraper: debug
   ```
2. Call the `zhc_heating_scheduler.refresh_schedule` service
3. Check the logs for parsing details

## Common Scraping Patterns

### Pattern 1: JSON Embedded in HTML

Some websites embed schedule data as JSON:

```python
def _parse_html(self, html: str) -> list[Event]:
    """Parse schedule from embedded JSON."""
    import json
    import re
    
    # Find JSON in script tag
    match = re.search(r'var scheduleData = ({.*?});', html, re.DOTALL)
    if not match:
        return []
    
    data = json.loads(match.group(1))
    
    events = []
    for item in data.get("events", []):
        start_time = datetime.fromisoformat(item["start"])
        end_time = datetime.fromisoformat(item["end"])
        
        event = Event(
            event_type=self._determine_type(item.get("type", "")),
            start_time=start_time,
            end_time=end_time,
            title=item.get("title", ""),
        )
        events.append(event)
    
    return events
```

### Pattern 2: API Endpoint

If your website has an API:

```python
async def fetch_schedule(self, days_ahead: int = 14) -> list[Event]:
    """Fetch schedule from API."""
    api_url = f"{self.url}/api/events"
    
    async with self._session.get(api_url) as response:
        response.raise_for_status()
        data = await response.json()
    
    events = []
    for item in data["events"]:
        # Parse API response
        ...
    
    return events
```

### Pattern 3: iCal/ICS Feed

If your club publishes an iCal feed:

```python
def _parse_html(self, html: str) -> list[Event]:
    """Parse iCal format."""
    from icalendar import Calendar
    
    cal = Calendar.from_ical(html)
    events = []
    
    for component in cal.walk('VEVENT'):
        start_time = component.get('dtstart').dt
        end_time = component.get('dtend').dt
        title = str(component.get('summary'))
        
        event = Event(
            event_type=self._determine_type(title),
            start_time=start_time,
            end_time=end_time,
            title=title,
        )
        events.append(event)
    
    return events
```

## Troubleshooting

### Problem: Events not found

**Solution**: Add debug logging to see what HTML is being fetched:

```python
def _parse_html(self, html: str) -> list[Event]:
    """Parse HTML."""
    self._logger.debug(f"HTML length: {len(html)}")
    self._logger.debug(f"First 500 chars: {html[:500]}")
    
    # ... rest of parsing
```

### Problem: Dates parsed incorrectly

**Solution**: Check date format and specify dayfirst parameter:

```python
from dateutil import parser

# For European dates (DD-MM-YYYY)
date_obj = parser.parse(date_str, dayfirst=True)

# For US dates (MM-DD-YYYY)
date_obj = parser.parse(date_str, dayfirst=False)
```

### Problem: Some events missing

**Solution**: Check if pagination exists:

```python
async def fetch_schedule(self, days_ahead: int = 14) -> list[Event]:
    """Fetch all pages of schedule."""
    all_events = []
    
    for page in range(1, 5):  # Check up to 5 pages
        url = f"{self.url}?page={page}"
        html = await self._fetch_html_from_url(url)
        events = self._parse_html(html)
        
        if not events:
            break  # No more events
        
        all_events.extend(events)
    
    return all_events
```

## Advanced: Handling Authentication

If your schedule requires login:

```python
async def _fetch_html(self) -> str:
    """Fetch HTML with authentication."""
    # Login first
    login_data = {
        "username": self.username,
        "password": self.password,
    }
    
    async with self._session.post(
        f"{self.base_url}/login",
        data=login_data
    ) as response:
        response.raise_for_status()
    
    # Now fetch schedule with authenticated session
    async with self._session.get(self.url) as response:
        response.raise_for_status()
        return await response.text()
```

## Best Practices

1. **Always validate dates**: Check that parsed dates are reasonable
2. **Handle missing data gracefully**: Use try/except blocks
3. **Log parsing issues**: Help debug problems
4. **Test with real data**: Use actual website HTML
5. **Handle timezone**: Ensure datetimes are in the correct timezone
6. **Respect rate limits**: Don't scrape too frequently

## Getting Help

If you're having trouble creating a custom scraper:

1. Enable debug logging and check what HTML is being fetched
2. Share the HTML structure (sanitized) in a GitHub issue
3. Ask for help in the Home Assistant community forums
4. Consider hiring a developer if needed

## Contributing Your Scraper

If you create a scraper that could help others, consider contributing it to the project! We can create a library of site-specific scrapers that users can choose from.

