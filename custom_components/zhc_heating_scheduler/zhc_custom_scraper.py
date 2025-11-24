"""Custom scraper for Zandvoortsche Hockey Club (ZHC) schedule."""
from __future__ import annotations

import logging
import re
from datetime import datetime, timedelta
from typing import Any

import aiohttp
from bs4 import BeautifulSoup
from dateutil import parser as date_parser

from .const import EVENT_TYPE_MATCH, EVENT_TYPE_TRAINING
from .scraper import Event, ScheduleScraper

_LOGGER = logging.getLogger(__name__)


class ZHCCustomScraper(ScheduleScraper):
    """Custom scraper for ZHC website with LISA integration."""

    def __init__(
        self,
        training_url: str = "https://www.zandvoortschehockeyclub.nl/trainingsschema",
        match_url: str = "https://www.zandvoortschehockeyclub.nl/wedstrijdschema",
        session: aiohttp.ClientSession | None = None,
    ):
        """Initialize the ZHC custom scraper."""
        # Use training URL as base for parent class
        super().__init__(training_url, session)
        self.training_url = training_url
        self.match_url = match_url

    async def fetch_schedule(self, days_ahead: int = 14) -> list[Event]:
        """
        Fetch and parse both training and match schedules.
        
        Args:
            days_ahead: Number of days to look ahead for events
            
        Returns:
            Combined list of training and match Event objects
        """
        all_events = []
        
        try:
            # Fetch training schedule
            _LOGGER.info("Fetching training schedule from ZHC")
            training_events = await self._fetch_training_schedule(days_ahead)
            all_events.extend(training_events)
            _LOGGER.info(f"Found {len(training_events)} training events")
            
        except Exception as e:
            _LOGGER.error(f"Error fetching training schedule: {e}", exc_info=True)
        
        try:
            # Fetch match schedule
            _LOGGER.info("Fetching match schedule from ZHC")
            match_events = await self._fetch_match_schedule(days_ahead)
            all_events.extend(match_events)
            _LOGGER.info(f"Found {len(match_events)} match events")
            
        except Exception as e:
            _LOGGER.error(f"Error fetching match schedule: {e}", exc_info=True)
        
        # Filter and sort events
        cutoff_date = datetime.now() + timedelta(days=days_ahead)
        filtered_events = [
            event for event in all_events
            if event.start_time <= cutoff_date
        ]
        
        # Sort by start time
        filtered_events.sort(key=lambda e: e.start_time)
        
        _LOGGER.info(
            f"Total: {len(filtered_events)} events from ZHC "
            f"(next {days_ahead} days)"
        )
        
        return filtered_events

    async def _fetch_training_schedule(self, days_ahead: int) -> list[Event]:
        """Fetch training schedule from ZHC."""
        try:
            # First, try to get the page and look for API endpoints
            html = await self._fetch_html_from_url(self.training_url)
            
            # Check if there's a data API or embedded JSON
            events = self._try_extract_embedded_data(html, EVENT_TYPE_TRAINING)
            if events:
                return events
            
            # Try to find LISA API endpoint in the page
            api_endpoint = self._find_api_endpoint(html)
            if api_endpoint:
                _LOGGER.info(f"Found API endpoint: {api_endpoint}")
                events = await self._fetch_from_api(api_endpoint, EVENT_TYPE_TRAINING)
                if events:
                    return events
            
            # Fallback: Try to parse any visible schedule data
            events = self._parse_training_html(html)
            
            return events
            
        except Exception as e:
            _LOGGER.error(f"Error in _fetch_training_schedule: {e}", exc_info=True)
            return []

    async def _fetch_match_schedule(self, days_ahead: int) -> list[Event]:
        """Fetch match schedule from ZHC."""
        try:
            # First, try to get the page and look for API endpoints
            html = await self._fetch_html_from_url(self.match_url)
            
            # Check if there's a data API or embedded JSON
            events = self._try_extract_embedded_data(html, EVENT_TYPE_MATCH)
            if events:
                return events
            
            # Try to find LISA API endpoint in the page
            api_endpoint = self._find_api_endpoint(html)
            if api_endpoint:
                _LOGGER.info(f"Found API endpoint: {api_endpoint}")
                events = await self._fetch_from_api(api_endpoint, EVENT_TYPE_MATCH)
                if events:
                    return events
            
            # Fallback: Try to parse any visible schedule data
            events = self._parse_match_html(html)
            
            return events
            
        except Exception as e:
            _LOGGER.error(f"Error in _fetch_match_schedule: {e}", exc_info=True)
            return []

    async def _fetch_html_from_url(self, url: str) -> str:
        """Fetch HTML from a specific URL."""
        if not self._session:
            self._session = aiohttp.ClientSession()
            self._own_session = True

        try:
            async with self._session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    "User-Agent": "Mozilla/5.0 (compatible; HomeAssistant-ZHC-Scheduler/1.0)",
                    "Accept": "text/html,application/json",
                },
            ) as response:
                response.raise_for_status()
                html = await response.text()
                _LOGGER.debug(f"Fetched {len(html)} bytes from {url}")
                
                # Save HTML for debugging
                if _LOGGER.isEnabledFor(logging.DEBUG):
                    _LOGGER.debug(f"First 1000 chars of HTML: {html[:1000]}")
                
                return html
                
        except aiohttp.ClientError as e:
            _LOGGER.error(f"HTTP error fetching {url}: {e}")
            raise

    def _find_api_endpoint(self, html: str) -> str | None:
        """Try to find API endpoint in the HTML."""
        # Look for common patterns in JavaScript
        patterns = [
            r'fetch\(["\']([^"\']+)["\']',  # fetch('url')
            r'ajax.*url:\s*["\']([^"\']+)["\']',  # jQuery ajax
            r'axios\.get\(["\']([^"\']+)["\']',  # axios
            r'data-api=["\']([^"\']+)["\']',  # data attributes
            r'apiUrl\s*=\s*["\']([^"\']+)["\']',  # variable assignments
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html)
            for match in matches:
                if 'schedule' in match.lower() or 'wedstrijd' in match.lower() or 'training' in match.lower():
                    _LOGGER.debug(f"Found potential API endpoint: {match}")
                    return match
        
        return None

    def _try_extract_embedded_data(self, html: str, event_type: str) -> list[Event]:
        """Try to extract embedded JSON data from the HTML."""
        events = []
        
        # Look for JSON data in script tags
        script_patterns = [
            r'var\s+scheduleData\s*=\s*({.*?});',
            r'window\.scheduleData\s*=\s*({.*?});',
            r'data-schedule=[\'"](.*?)[\'"]',
        ]
        
        import json
        
        for pattern in script_patterns:
            matches = re.findall(pattern, html, re.DOTALL)
            for match in matches:
                try:
                    data = json.loads(match)
                    _LOGGER.debug(f"Found embedded JSON data: {data}")
                    events = self._parse_json_data(data, event_type)
                    if events:
                        return events
                except json.JSONDecodeError:
                    continue
        
        return events

    def _parse_json_data(self, data: dict | list, event_type: str) -> list[Event]:
        """Parse JSON data into events."""
        events = []
        
        # Handle different JSON structures
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            # Try common keys
            items = data.get('events', data.get('items', data.get('schedule', [])))
        else:
            return events
        
        for item in items:
            try:
                # Try to extract date/time
                start_str = item.get('start', item.get('start_time', item.get('datum')))
                end_str = item.get('end', item.get('end_time'))
                title = item.get('title', item.get('name', item.get('omschrijving', '')))
                
                if start_str:
                    start_time = date_parser.parse(start_str)
                    
                    if end_str:
                        end_time = date_parser.parse(end_str)
                    else:
                        # Default to 2 hours for training, 1.5 for matches
                        duration = 2 if event_type == EVENT_TYPE_TRAINING else 1.5
                        end_time = start_time + timedelta(hours=duration)
                    
                    event = Event(
                        event_type=event_type,
                        start_time=start_time,
                        end_time=end_time,
                        title=title,
                    )
                    events.append(event)
                    
            except Exception as e:
                _LOGGER.debug(f"Could not parse JSON item: {e}")
                continue
        
        return events

    async def _fetch_from_api(self, api_url: str, event_type: str) -> list[Event]:
        """Fetch data from an API endpoint."""
        if not self._session:
            self._session = aiohttp.ClientSession()
            self._own_session = True

        try:
            # Handle relative URLs
            if api_url.startswith('/'):
                api_url = f"https://www.zandvoortschehockeyclub.nl{api_url}"
            
            async with self._session.get(
                api_url,
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    "User-Agent": "Mozilla/5.0 (compatible; HomeAssistant-ZHC-Scheduler/1.0)",
                    "Accept": "application/json",
                },
            ) as response:
                response.raise_for_status()
                data = await response.json()
                
                _LOGGER.debug(f"API response: {data}")
                return self._parse_json_data(data, event_type)
                
        except Exception as e:
            _LOGGER.error(f"Error fetching from API {api_url}: {e}")
            return []

    def _parse_training_html(self, html: str) -> list[Event]:
        """Parse training schedule from HTML as fallback."""
        soup = BeautifulSoup(html, "html.parser")
        events = []
        
        _LOGGER.debug("Attempting to parse training schedule from HTML")
        
        # Look for schedule containers
        # The LISA system might use specific classes
        schedule_containers = soup.find_all(
            ["div", "table", "ul"],
            class_=re.compile(r"(schedule|training|agenda|event)", re.I)
        )
        
        for container in schedule_containers:
            # Look for date/time patterns in the container
            text = container.get_text()
            
            # Dutch date patterns
            date_matches = re.findall(
                r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
                text
            )
            time_matches = re.findall(
                r'(\d{1,2}:\d{2})\s*[-–]\s*(\d{1,2}:\d{2})',
                text
            )
            
            if date_matches and time_matches:
                for date_str in date_matches:
                    for time_start, time_end in time_matches:
                        try:
                            start_time, end_time = self._parse_datetime(
                                date_str,
                                f"{time_start}-{time_end}"
                            )
                            
                            if start_time and end_time:
                                event = Event(
                                    event_type=EVENT_TYPE_TRAINING,
                                    start_time=start_time,
                                    end_time=end_time,
                                    title="Training",
                                )
                                events.append(event)
                        except Exception as e:
                            _LOGGER.debug(f"Could not parse training event: {e}")
        
        if not events:
            _LOGGER.warning(
                "No training events found in HTML. The page may use "
                "JavaScript to load content. Consider checking browser "
                "developer tools for API endpoints."
            )
        
        return events

    def _parse_match_html(self, html: str) -> list[Event]:
        """Parse match schedule from HTML as fallback."""
        soup = BeautifulSoup(html, "html.parser")
        events = []
        
        _LOGGER.debug("Attempting to parse match schedule from HTML")
        
        # Look for match/wedstrijd containers
        match_containers = soup.find_all(
            ["div", "table", "ul"],
            class_=re.compile(r"(match|wedstrijd|game|schedule)", re.I)
        )
        
        for container in match_containers:
            text = container.get_text()
            
            # Look for date and time patterns
            date_matches = re.findall(
                r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
                text
            )
            time_matches = re.findall(
                r'(\d{1,2}:\d{2})',
                text
            )
            
            if date_matches and time_matches:
                for date_str in date_matches:
                    for time_str in time_matches:
                        try:
                            start_time, end_time = self._parse_datetime(
                                date_str,
                                time_str
                            )
                            
                            if start_time and end_time:
                                # Default match duration: 1.5 hours
                                end_time = start_time + timedelta(hours=1, minutes=30)
                                
                                event = Event(
                                    event_type=EVENT_TYPE_MATCH,
                                    start_time=start_time,
                                    end_time=end_time,
                                    title="Wedstrijd",
                                )
                                events.append(event)
                        except Exception as e:
                            _LOGGER.debug(f"Could not parse match event: {e}")
        
        if not events:
            _LOGGER.warning(
                "No match events found in HTML. The page may use "
                "JavaScript to load content. Consider checking browser "
                "developer tools for API endpoints."
            )
        
        return events

