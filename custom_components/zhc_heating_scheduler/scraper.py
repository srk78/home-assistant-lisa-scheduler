"""Schedule scraper for ZHC Heating Scheduler."""
from __future__ import annotations

import logging
import re
from datetime import datetime, timedelta
from typing import Any

import aiohttp
from bs4 import BeautifulSoup
from dateutil import parser as date_parser

from .const import EVENT_TYPE_MATCH, EVENT_TYPE_TRAINING, EVENT_TYPE_UNKNOWN

_LOGGER = logging.getLogger(__name__)


class Event:
    """Represents a scheduled event."""

    def __init__(
        self,
        event_type: str,
        start_time: datetime,
        end_time: datetime,
        title: str = "",
        location: str = "",
    ):
        """Initialize an event."""
        self.event_type = event_type
        self.start_time = start_time
        self.end_time = end_time
        self.title = title
        self.location = location

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"Event(type={self.event_type}, "
            f"start={self.start_time.isoformat()}, "
            f"end={self.end_time.isoformat()}, "
            f"title={self.title})"
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "event_type": self.event_type,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "title": self.title,
            "location": self.location,
        }


class ScheduleScraper:
    """Scraper for field hockey club schedule."""

    def __init__(self, url: str, session: aiohttp.ClientSession | None = None):
        """Initialize the scraper."""
        self.url = url
        self._session = session
        self._own_session = session is None

    async def __aenter__(self):
        """Async context manager entry."""
        if self._own_session:
            self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._own_session and self._session:
            await self._session.close()

    async def fetch_schedule(self, days_ahead: int = 14) -> list[Event]:
        """
        Fetch and parse the schedule from the website.
        
        Args:
            days_ahead: Number of days to look ahead for events
            
        Returns:
            List of Event objects
        """
        try:
            html = await self._fetch_html()
            events = self._parse_html(html)
            
            # Filter events to only include those within the specified timeframe
            cutoff_date = datetime.now() + timedelta(days=days_ahead)
            filtered_events = [
                event for event in events
                if event.start_time <= cutoff_date
            ]
            
            _LOGGER.info(
                f"Fetched {len(filtered_events)} events from schedule "
                f"(next {days_ahead} days)"
            )
            
            return filtered_events
            
        except Exception as e:
            _LOGGER.error(f"Error fetching schedule: {e}", exc_info=True)
            raise

    async def _fetch_html(self) -> str:
        """Fetch HTML content from the URL."""
        if not self._session:
            self._session = aiohttp.ClientSession()
            self._own_session = True

        try:
            async with self._session.get(
                self.url,
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    "User-Agent": "Mozilla/5.0 (compatible; HomeAssistant-ZHC-Scheduler/1.0)"
                },
            ) as response:
                response.raise_for_status()
                html = await response.text()
                _LOGGER.debug(f"Fetched {len(html)} bytes from {self.url}")
                return html
                
        except aiohttp.ClientError as e:
            _LOGGER.error(f"HTTP error fetching schedule: {e}")
            raise
        except Exception as e:
            _LOGGER.error(f"Unexpected error fetching schedule: {e}")
            raise

    def _parse_html(self, html: str) -> list[Event]:
        """
        Parse HTML content to extract events.
        
        This is a generic parser that looks for common patterns.
        Override this method for site-specific parsing.
        """
        soup = BeautifulSoup(html, "html.parser")
        events = []

        # Strategy 1: Look for table-based schedules
        events.extend(self._parse_table_schedule(soup))

        # Strategy 2: Look for list-based schedules
        if not events:
            events.extend(self._parse_list_schedule(soup))

        # Strategy 3: Look for calendar-based schedules
        if not events:
            events.extend(self._parse_calendar_schedule(soup))

        if not events:
            _LOGGER.warning("No events found in HTML - may need custom parser")
            
        return events

    def _parse_table_schedule(self, soup: BeautifulSoup) -> list[Event]:
        """Parse table-based schedule format."""
        events = []
        
        # Look for tables that might contain schedule data
        tables = soup.find_all("table")
        
        for table in tables:
            rows = table.find_all("tr")
            
            for row in rows:
                cells = row.find_all(["td", "th"])
                if len(cells) < 3:
                    continue
                    
                try:
                    event = self._parse_row_to_event(cells)
                    if event:
                        events.append(event)
                except Exception as e:
                    _LOGGER.debug(f"Could not parse row: {e}")
                    continue
                    
        return events

    def _parse_list_schedule(self, soup: BeautifulSoup) -> list[Event]:
        """Parse list-based schedule format."""
        events = []
        
        # Look for common list patterns (ul, ol, div with class schedule/event)
        list_containers = soup.find_all(["ul", "ol", "div"], class_=re.compile(r"(schedule|event|calendar)", re.I))
        
        for container in list_containers:
            items = container.find_all(["li", "div"], class_=re.compile(r"(item|event|entry)", re.I))
            
            for item in items:
                try:
                    event = self._parse_item_to_event(item)
                    if event:
                        events.append(event)
                except Exception as e:
                    _LOGGER.debug(f"Could not parse list item: {e}")
                    continue
                    
        return events

    def _parse_calendar_schedule(self, soup: BeautifulSoup) -> list[Event]:
        """Parse calendar-based schedule format."""
        events = []
        
        # Look for calendar day cells
        day_cells = soup.find_all(["div", "td"], class_=re.compile(r"(day|date|cell)", re.I))
        
        for cell in day_cells:
            # Look for events within each day
            event_elements = cell.find_all(["div", "span", "a"], class_=re.compile(r"event", re.I))
            
            for elem in event_elements:
                try:
                    event = self._parse_element_to_event(elem, cell)
                    if event:
                        events.append(event)
                except Exception as e:
                    _LOGGER.debug(f"Could not parse calendar event: {e}")
                    continue
                    
        return events

    def _parse_row_to_event(self, cells) -> Event | None:
        """Parse a table row into an Event."""
        # Extract text from cells
        cell_texts = [cell.get_text(strip=True) for cell in cells]
        
        # Try to find date, time, and event type
        date_str = None
        time_str = None
        event_type = EVENT_TYPE_UNKNOWN
        title = ""
        
        for text in cell_texts:
            # Look for date patterns
            if not date_str and self._looks_like_date(text):
                date_str = text
                
            # Look for time patterns
            if not time_str and self._looks_like_time(text):
                time_str = text
                
            # Look for event type indicators
            if "training" in text.lower() or "train" in text.lower():
                event_type = EVENT_TYPE_TRAINING
                title = text
            elif "match" in text.lower() or "wedstrijd" in text.lower():
                event_type = EVENT_TYPE_MATCH
                title = text
                
        if date_str and time_str:
            start_time, end_time = self._parse_datetime(date_str, time_str)
            if start_time and end_time:
                return Event(event_type, start_time, end_time, title)
                
        return None

    def _parse_item_to_event(self, item) -> Event | None:
        """Parse a list item into an Event."""
        text = item.get_text(strip=True)
        
        # Try to extract structured data
        date_str = self._extract_date(text)
        time_str = self._extract_time(text)
        
        event_type = EVENT_TYPE_UNKNOWN
        if "training" in text.lower() or "train" in text.lower():
            event_type = EVENT_TYPE_TRAINING
        elif "match" in text.lower() or "wedstrijd" in text.lower():
            event_type = EVENT_TYPE_MATCH
            
        if date_str and time_str:
            start_time, end_time = self._parse_datetime(date_str, time_str)
            if start_time and end_time:
                return Event(event_type, start_time, end_time, text)
                
        return None

    def _parse_element_to_event(self, element, parent) -> Event | None:
        """Parse a calendar element into an Event."""
        text = element.get_text(strip=True)
        parent_text = parent.get_text(strip=True)
        
        # Try to find date in parent (day cell)
        date_str = self._extract_date(parent_text)
        time_str = self._extract_time(text)
        
        event_type = EVENT_TYPE_UNKNOWN
        if "training" in text.lower():
            event_type = EVENT_TYPE_TRAINING
        elif "match" in text.lower() or "wedstrijd" in text.lower():
            event_type = EVENT_TYPE_MATCH
            
        if date_str and time_str:
            start_time, end_time = self._parse_datetime(date_str, time_str)
            if start_time and end_time:
                return Event(event_type, start_time, end_time, text)
                
        return None

    def _looks_like_date(self, text: str) -> bool:
        """Check if text looks like a date."""
        # Common date patterns
        date_patterns = [
            r"\d{1,2}[-/]\d{1,2}[-/]\d{2,4}",  # DD-MM-YYYY or similar
            r"\d{4}[-/]\d{1,2}[-/]\d{1,2}",  # YYYY-MM-DD
            r"\d{1,2}\s+\w+\s+\d{4}",  # DD Month YYYY
        ]
        return any(re.search(pattern, text) for pattern in date_patterns)

    def _looks_like_time(self, text: str) -> bool:
        """Check if text looks like a time."""
        # Time patterns
        time_patterns = [
            r"\d{1,2}:\d{2}",  # HH:MM
            r"\d{1,2}u\d{2}",  # HHuMM (Dutch format)
        ]
        return any(re.search(pattern, text) for pattern in time_patterns)

    def _extract_date(self, text: str) -> str | None:
        """Extract date string from text."""
        date_patterns = [
            r"\d{1,2}[-/]\d{1,2}[-/]\d{2,4}",
            r"\d{4}[-/]\d{1,2}[-/]\d{1,2}",
            r"\d{1,2}\s+\w+\s+\d{4}",
        ]
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return None

    def _extract_time(self, text: str) -> str | None:
        """Extract time string from text."""
        # Look for time ranges like "14:00-16:00" or "14:00 - 16:00"
        time_range_pattern = r"(\d{1,2}:\d{2})\s*[-–]\s*(\d{1,2}:\d{2})"
        match = re.search(time_range_pattern, text)
        if match:
            return match.group(0)
            
        # Single time
        time_pattern = r"\d{1,2}:\d{2}"
        match = re.search(time_pattern, text)
        if match:
            return match.group(0)
            
        return None

    def _parse_datetime(
        self, date_str: str, time_str: str
    ) -> tuple[datetime | None, datetime | None]:
        """
        Parse date and time strings into datetime objects.
        
        Returns:
            Tuple of (start_time, end_time)
        """
        try:
            # Parse the date
            date_obj = date_parser.parse(date_str, dayfirst=True)
            
            # Check if time_str contains a range
            time_range_match = re.match(r"(\d{1,2}:\d{2})\s*[-–]\s*(\d{1,2}:\d{2})", time_str)
            
            if time_range_match:
                start_time_str = time_range_match.group(1)
                end_time_str = time_range_match.group(2)
                
                start_time = date_parser.parse(
                    f"{date_obj.date()} {start_time_str}"
                )
                end_time = date_parser.parse(
                    f"{date_obj.date()} {end_time_str}"
                )
                
            else:
                # Single time - assume 2 hour duration
                start_time = date_parser.parse(f"{date_obj.date()} {time_str}")
                end_time = start_time + timedelta(hours=2)
                
            return start_time, end_time
            
        except Exception as e:
            _LOGGER.debug(f"Could not parse datetime '{date_str}' '{time_str}': {e}")
            return None, None


class CustomScheduleScraper(ScheduleScraper):
    """
    Custom scraper for specific website formats.
    
    Override _parse_html() method to implement site-specific parsing logic.
    """

    def _parse_html(self, html: str) -> list[Event]:
        """
        Site-specific parsing logic.
        
        Example implementation:
        
        soup = BeautifulSoup(html, "html.parser")
        events = []
        
        # Find schedule container
        schedule_div = soup.find("div", class_="schedule-container")
        
        # Parse events
        for event_div in schedule_div.find_all("div", class_="event"):
            # Extract event details
            ...
            
        return events
        """
        # For now, fall back to parent class generic parsing
        return super()._parse_html(html)

