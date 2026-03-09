"""Configurable scraper for LISA Scheduler."""
from __future__ import annotations

import logging
import re
from datetime import datetime, timedelta
from typing import Any

import aiohttp
from bs4 import BeautifulSoup
from dateutil import parser as date_parser
import pytz

from .const import (
    CONF_DATE_FORMAT,
    CONF_SOURCE_API_ENDPOINT,
    CONF_SOURCE_API_HEADERS,
    CONF_SOURCE_API_PARAMS,
    CONF_SOURCE_METHOD,
    CONF_SOURCE_SELECTORS,
    CONF_SOURCE_TYPE,
    CONF_SOURCE_URL,
    CONF_TIME_FORMAT,
    CONF_TIMEZONE,
    DEFAULT_DATE_FORMAT,
    DEFAULT_TIME_FORMAT,
    DEFAULT_TIMEZONE,
    EVENT_TYPE_MATCH,
    EVENT_TYPE_TRAINING,
    EVENT_TYPE_UNKNOWN,
    SCRAPER_METHOD_API,
    SCRAPER_METHOD_HTML,
    SCRAPER_METHOD_ICAL,
)
from .scraper import Event, ScheduleScraper

_LOGGER = logging.getLogger(__name__)


class ConfigurableScraper(ScheduleScraper):
    """
    Configurable scraper that uses configuration instead of code.
    
    Supports multiple sources, selectors, and parsing strategies.
    """

    def __init__(
        self,
        sources: list[dict[str, Any]],
        date_format: str = DEFAULT_DATE_FORMAT,
        time_format: str = DEFAULT_TIME_FORMAT,
        timezone: str = DEFAULT_TIMEZONE,
        session: aiohttp.ClientSession | None = None,
    ):
        """
        Initialize the configurable scraper.
        
        Args:
            sources: List of source configurations
            date_format: strptime format for parsing dates
            time_format: strptime format for parsing times
            timezone: Timezone name (e.g., 'Europe/Amsterdam')
            session: Optional aiohttp session
        """
        # Use first source URL as base for parent class
        base_url = sources[0][CONF_SOURCE_URL] if sources else ""
        super().__init__(base_url, session)
        
        self.sources = sources
        self.date_format = date_format
        self.time_format = time_format
        
        try:
            self.timezone = pytz.timezone(timezone)
        except Exception as e:
            _LOGGER.warning(f"Invalid timezone {timezone}, using UTC: {e}")
            self.timezone = pytz.UTC

    async def fetch_schedule(self, days_ahead: int = 14) -> list[Event]:
        """
        Fetch schedule from all configured sources.
        
        Args:
            days_ahead: Number of days to look ahead for events
            
        Returns:
            Combined list of Event objects from all sources
        """
        all_events = []
        
        for source in self.sources:
            try:
                _LOGGER.info(f"Fetching from source: {source.get(CONF_SOURCE_URL)}")
                events = await self._fetch_from_source(source, days_ahead)
                all_events.extend(events)
                _LOGGER.info(
                    f"Found {len(events)} events from {source.get(CONF_SOURCE_URL)}"
                )
            except Exception as e:
                _LOGGER.error(
                    f"Error fetching from {source.get(CONF_SOURCE_URL)}: {e}",
                    exc_info=True
                )
        
        # Filter by date range (naive, matching coordinator and scheduler)
        cutoff_date = datetime.now() + timedelta(days=days_ahead)
        filtered_events = [
            event for event in all_events
            if event.start_time <= cutoff_date
        ]
        
        # Sort by start time
        filtered_events.sort(key=lambda e: e.start_time)
        
        _LOGGER.info(
            f"Total: {len(filtered_events)} events (next {days_ahead} days)"
        )
        
        return filtered_events

    async def _fetch_from_source(
        self, source: dict[str, Any], days_ahead: int
    ) -> list[Event]:
        """Fetch events from a single source."""
        method = source.get(CONF_SOURCE_METHOD, SCRAPER_METHOD_HTML)
        
        if method == SCRAPER_METHOD_HTML:
            return await self._fetch_html_source(source)
        elif method == SCRAPER_METHOD_API:
            return await self._fetch_api_source(source)
        elif method == SCRAPER_METHOD_ICAL:
            return await self._fetch_ical_source(source)
        else:
            _LOGGER.error(f"Unknown scraper method: {method}")
            return []

    async def _fetch_html_source(self, source: dict[str, Any]) -> list[Event]:
        """Fetch and parse HTML source."""
        url = source[CONF_SOURCE_URL]
        event_type = source.get(CONF_SOURCE_TYPE, EVENT_TYPE_UNKNOWN)
        selectors = source.get(CONF_SOURCE_SELECTORS, {})
        
        # Fetch HTML
        html = await self._fetch_html_from_url(url)
        
        # Parse using selectors
        return self._parse_html_with_selectors(html, event_type, selectors)

    async def _fetch_api_source(self, source: dict[str, Any]) -> list[Event]:
        """Fetch events from API endpoint."""
        url = source.get(CONF_SOURCE_API_ENDPOINT, source[CONF_SOURCE_URL])
        event_type = source.get(CONF_SOURCE_TYPE, EVENT_TYPE_UNKNOWN)
        headers = source.get(CONF_SOURCE_API_HEADERS, {})
        params = source.get(CONF_SOURCE_API_PARAMS, {})
        
        if not self._session:
            self._session = aiohttp.ClientSession()
            self._own_session = True
        
        try:
            async with self._session.get(
                url,
                headers=headers,
                params=params,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                response.raise_for_status()
                data = await response.json()
                
                return self._parse_api_response(data, event_type)
                
        except Exception as e:
            _LOGGER.error(f"Error fetching from API {url}: {e}")
            return []

    async def _fetch_ical_source(self, source: dict[str, Any]) -> list[Event]:
        """Fetch and parse iCal/ICS feed."""
        url = source[CONF_SOURCE_URL]
        event_type = source.get(CONF_SOURCE_TYPE, EVENT_TYPE_UNKNOWN)
        
        if not self._session:
            self._session = aiohttp.ClientSession()
            self._own_session = True
        
        try:
            async with self._session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                response.raise_for_status()
                ical_data = await response.text()
                
                return self._parse_ical(ical_data, event_type)
                
        except Exception as e:
            _LOGGER.error(f"Error fetching iCal from {url}: {e}")
            return []

    async def _fetch_html_from_url(self, url: str) -> str:
        """Fetch HTML content from URL."""
        if not self._session:
            self._session = aiohttp.ClientSession()
            self._own_session = True
        
        try:
            async with self._session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    "User-Agent": "Mozilla/5.0 (compatible; HomeAssistant-LISA-Scheduler/1.0)"
                },
            ) as response:
                response.raise_for_status()
                return await response.text()
        except Exception as e:
            _LOGGER.error(f"Error fetching HTML from {url}: {e}")
            raise

    def _parse_html_with_selectors(
        self, html: str, event_type: str, selectors: dict[str, str]
    ) -> list[Event]:
        """Parse HTML using configured CSS selectors."""
        soup = BeautifulSoup(html, "html.parser")
        events = []
        
        # Get container selector
        container_selector = selectors.get("container")
        if not container_selector:
            _LOGGER.warning("No container selector configured, using fallback")
            return self._parse_html(html)
        
        # Find all event containers
        containers = soup.select(container_selector)
        _LOGGER.debug(f"Found {len(containers)} containers with selector '{container_selector}'")
        
        for container in containers:
            try:
                event = self._parse_container(container, event_type, selectors)
                if event:
                    events.append(event)
            except Exception as e:
                _LOGGER.debug(f"Error parsing container: {e}")
                continue
        
        return events

    def _parse_container(
        self, container, event_type: str, selectors: dict[str, str]
    ) -> Event | None:
        """Parse a single event container."""
        # Extract date
        date_str = None
        if "date" in selectors:
            date_elem = container.select_one(selectors["date"])
            if date_elem:
                date_str = date_elem.get_text(strip=True)
        
        # Extract time
        time_str = None
        if "time" in selectors:
            time_elem = container.select_one(selectors["time"])
            if time_elem:
                time_str = time_elem.get_text(strip=True)
        
        # Extract title
        title = ""
        if "title" in selectors:
            title_elem = container.select_one(selectors["title"])
            if title_elem:
                title = title_elem.get_text(strip=True)
        
        # Extract location
        location = ""
        if "location" in selectors:
            location_elem = container.select_one(selectors["location"])
            if location_elem:
                location = location_elem.get_text(strip=True)
        
        # Parse datetime
        if date_str and time_str:
            start_time, end_time = self._parse_datetime_with_format(date_str, time_str)
            if start_time and end_time:
                return Event(
                    event_type=event_type,
                    start_time=start_time,
                    end_time=end_time,
                    title=title,
                    location=location,
                )
        
        return None

    def _parse_datetime_with_format(
        self, date_str: str, time_str: str
    ) -> tuple[datetime | None, datetime | None]:
        """Parse date and time using configured formats."""
        try:
            # Check if time contains a range
            time_range_match = re.match(r"(\d{1,2}:\d{2})\s*[-–]\s*(\d{1,2}:\d{2})", time_str)
            
            # Parse date
            date_obj = datetime.strptime(date_str, self.date_format)
            
            if time_range_match:
                # Parse time range
                start_time_str = time_range_match.group(1)
                end_time_str = time_range_match.group(2)

                start_time = datetime.strptime(
                    f"{date_str} {start_time_str}",
                    f"{self.date_format} {self.time_format}"
                )
                end_time = datetime.strptime(
                    f"{date_str} {end_time_str}",
                    f"{self.date_format} {self.time_format}"
                )
            else:
                # Single time - default 2 hour duration
                start_time = datetime.strptime(
                    f"{date_str} {time_str}",
                    f"{self.date_format} {self.time_format}"
                )
                end_time = start_time + timedelta(hours=2)

            # Return naive datetimes to stay consistent with the rest of the codebase.
            # The strptime result is already in the club's local time; no localization needed.
            return start_time, end_time
            
        except Exception as e:
            _LOGGER.debug(f"Error parsing datetime '{date_str}' '{time_str}': {e}")
            # Fallback to flexible parsing
            return self._parse_datetime(date_str, time_str)

    def _parse_api_response(self, data: dict | list, event_type: str) -> list[Event]:
        """Parse API JSON response."""
        events = []
        
        # Handle different JSON structures
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            # Try common keys
            items = data.get('events', data.get('items', data.get('schedule', [])))
            if not items and 'data' in data:
                items = data['data']
                if isinstance(items, dict):
                    items = items.get('events', items.get('items', []))
        else:
            return events
        
        for item in items:
            try:
                # Try to extract date/time in various formats
                start_str = item.get('start', item.get('start_time', item.get('startTime', item.get('datum'))))
                end_str = item.get('end', item.get('end_time', item.get('endTime')))
                title = item.get('title', item.get('name', item.get('omschrijving', item.get('description', ''))))
                location = item.get('location', item.get('locatie', item.get('venue', '')))
                
                if start_str:
                    # Try to parse ISO format or use flexible parser
                    try:
                        start_time = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
                    except Exception:
                        start_time = date_parser.parse(start_str)

                    # Normalise to naive local time (club timezone)
                    if start_time.tzinfo is not None:
                        start_time = start_time.astimezone(self.timezone).replace(tzinfo=None)

                    if end_str:
                        try:
                            end_time = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
                        except Exception:
                            end_time = date_parser.parse(end_str)

                        if end_time.tzinfo is not None:
                            end_time = end_time.astimezone(self.timezone).replace(tzinfo=None)
                    else:
                        # Default duration
                        duration = 2 if event_type == EVENT_TYPE_TRAINING else 1.5
                        end_time = start_time + timedelta(hours=duration)
                    
                    event = Event(
                        event_type=event_type,
                        start_time=start_time,
                        end_time=end_time,
                        title=title,
                        location=location,
                    )
                    events.append(event)
                    
            except Exception as e:
                _LOGGER.debug(f"Could not parse API item: {e}")
                continue
        
        return events

    def _parse_ical(self, ical_data: str, event_type: str) -> list[Event]:
        """Parse iCal/ICS format."""
        events = []
        
        try:
            from icalendar import Calendar
            
            cal = Calendar.from_ical(ical_data)
            
            for component in cal.walk('VEVENT'):
                try:
                    start_time = component.get('dtstart').dt
                    end_time = component.get('dtend').dt
                    title = str(component.get('summary', ''))
                    location = str(component.get('location', ''))
                    
                    # Normalise to naive datetime in the club's local timezone
                    if isinstance(start_time, datetime):
                        if start_time.tzinfo is not None:
                            start_time = start_time.astimezone(self.timezone).replace(tzinfo=None)
                    else:
                        # Date only — convert to midnight, naive
                        start_time = datetime.combine(start_time, datetime.min.time())

                    if isinstance(end_time, datetime):
                        if end_time.tzinfo is not None:
                            end_time = end_time.astimezone(self.timezone).replace(tzinfo=None)
                    else:
                        end_time = datetime.combine(end_time, datetime.min.time())
                    
                    event = Event(
                        event_type=event_type,
                        start_time=start_time,
                        end_time=end_time,
                        title=title,
                        location=location,
                    )
                    events.append(event)
                    
                except Exception as e:
                    _LOGGER.debug(f"Error parsing iCal event: {e}")
                    continue
                    
        except ImportError:
            _LOGGER.error("icalendar package not installed. Install with: pip install icalendar")
        except Exception as e:
            _LOGGER.error(f"Error parsing iCal data: {e}")
        
        return events

