"""Configuration validator for scraper settings."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from .const import (
    CONF_DATE_FORMAT,
    CONF_SCRAPER_SOURCES,
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

_LOGGER = logging.getLogger(__name__)

# Selector schema
SELECTOR_SCHEMA = vol.Schema({
    vol.Optional("container"): str,
    vol.Optional("date"): str,
    vol.Optional("time"): str,
    vol.Optional("title"): str,
    vol.Optional("location"): str,
}, extra=vol.ALLOW_EXTRA)

# Source schema
SOURCE_SCHEMA = vol.Schema({
    vol.Required(CONF_SOURCE_URL): str,
    vol.Optional(CONF_SOURCE_TYPE, default=EVENT_TYPE_UNKNOWN): vol.In([
        EVENT_TYPE_TRAINING,
        EVENT_TYPE_MATCH,
        EVENT_TYPE_UNKNOWN,
    ]),
    vol.Optional(CONF_SOURCE_METHOD, default=SCRAPER_METHOD_HTML): vol.In([
        SCRAPER_METHOD_HTML,
        SCRAPER_METHOD_API,
        SCRAPER_METHOD_ICAL,
    ]),
    vol.Optional(CONF_SOURCE_SELECTORS): SELECTOR_SCHEMA,
    vol.Optional(CONF_SOURCE_API_ENDPOINT): str,
    vol.Optional(CONF_SOURCE_API_HEADERS): dict,
    vol.Optional(CONF_SOURCE_API_PARAMS): dict,
}, extra=vol.ALLOW_EXTRA)

# Complete scraper configuration schema
SCRAPER_CONFIG_SCHEMA = vol.Schema({
    vol.Required(CONF_SCRAPER_SOURCES): [SOURCE_SCHEMA],
    vol.Optional(CONF_DATE_FORMAT, default=DEFAULT_DATE_FORMAT): str,
    vol.Optional(CONF_TIME_FORMAT, default=DEFAULT_TIME_FORMAT): str,
    vol.Optional(CONF_TIMEZONE, default=DEFAULT_TIMEZONE): str,
}, extra=vol.ALLOW_EXTRA)


class ScraperConfigValidator:
    """Validator for scraper configuration."""

    @staticmethod
    def validate_config(config: dict[str, Any]) -> dict[str, Any]:
        """
        Validate scraper configuration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Validated configuration
            
        Raises:
            vol.Invalid: If configuration is invalid
        """
        try:
            validated = SCRAPER_CONFIG_SCHEMA(config)
            _LOGGER.debug("Scraper configuration is valid")
            return validated
        except vol.Invalid as e:
            _LOGGER.error(f"Invalid scraper configuration: {e}")
            raise

    @staticmethod
    def validate_source(source: dict[str, Any]) -> dict[str, Any]:
        """
        Validate a single source configuration.
        
        Args:
            source: Source configuration dictionary
            
        Returns:
            Validated source configuration
            
        Raises:
            vol.Invalid: If source is invalid
        """
        try:
            validated = SOURCE_SCHEMA(source)
            return validated
        except vol.Invalid as e:
            _LOGGER.error(f"Invalid source configuration: {e}")
            raise

    @staticmethod
    async def test_url_accessible(url: str, timeout: int = 10) -> tuple[bool, str]:
        """
        Test if a URL is accessible.
        
        Args:
            url: URL to test
            timeout: Timeout in seconds
            
        Returns:
            Tuple of (success, message)
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(total=timeout),
                    headers={
                        "User-Agent": "Mozilla/5.0 (compatible; HomeAssistant-ZHC-Scheduler/1.0)"
                    }
                ) as response:
                    if response.status == 200:
                        return True, f"URL accessible (status: {response.status})"
                    else:
                        return False, f"URL returned status: {response.status}"
        except aiohttp.ClientError as e:
            return False, f"Connection error: {str(e)}"
        except Exception as e:
            return False, f"Error accessing URL: {str(e)}"

    @staticmethod
    async def test_selectors(
        html: str,
        selectors: dict[str, str]
    ) -> dict[str, Any]:
        """
        Test if selectors find elements in HTML.
        
        Args:
            html: HTML content to test
            selectors: Dictionary of selectors to test
            
        Returns:
            Dictionary with test results for each selector
        """
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html, "html.parser")
        results = {}
        
        for name, selector in selectors.items():
            try:
                elements = soup.select(selector)
                results[name] = {
                    "found": len(elements),
                    "success": len(elements) > 0,
                    "sample": elements[0].get_text(strip=True)[:100] if elements else None
                }
            except Exception as e:
                results[name] = {
                    "found": 0,
                    "success": False,
                    "error": str(e)
                }
        
        return results

    @staticmethod
    def validate_date_format(date_format: str, test_string: str) -> tuple[bool, str]:
        """
        Validate a date format string.
        
        Args:
            date_format: strptime format string
            test_string: Example date string to test
            
        Returns:
            Tuple of (success, message)
        """
        from datetime import datetime
        
        try:
            datetime.strptime(test_string, date_format)
            return True, f"Date format valid (parsed: {test_string})"
        except ValueError as e:
            return False, f"Invalid date format: {str(e)}"

    @staticmethod
    def validate_timezone(timezone: str) -> tuple[bool, str]:
        """
        Validate a timezone string.
        
        Args:
            timezone: Timezone name
            
        Returns:
            Tuple of (success, message)
        """
        import pytz
        
        try:
            tz = pytz.timezone(timezone)
            return True, f"Timezone valid: {tz.zone}"
        except pytz.exceptions.UnknownTimeZoneError:
            return False, f"Unknown timezone: {timezone}"

    @staticmethod
    async def test_configuration(config: dict[str, Any]) -> dict[str, Any]:
        """
        Comprehensively test a scraper configuration.
        
        Args:
            config: Configuration to test
            
        Returns:
            Dictionary with detailed test results
        """
        results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "sources": [],
        }
        
        # Validate schema
        try:
            ScraperConfigValidator.validate_config(config)
        except vol.Invalid as e:
            results["valid"] = False
            results["errors"].append(f"Schema validation failed: {str(e)}")
            return results
        
        # Validate timezone
        timezone = config.get(CONF_TIMEZONE, DEFAULT_TIMEZONE)
        tz_valid, tz_msg = ScraperConfigValidator.validate_timezone(timezone)
        if not tz_valid:
            results["valid"] = False
            results["errors"].append(tz_msg)
        
        # Test each source
        sources = config.get(CONF_SCRAPER_SOURCES, [])
        for i, source in enumerate(sources):
            source_result = {
                "index": i,
                "url": source.get(CONF_SOURCE_URL),
                "accessible": False,
                "method": source.get(CONF_SOURCE_METHOD, SCRAPER_METHOD_HTML),
                "selectors_tested": False,
            }
            
            # Test URL accessibility
            url = source.get(CONF_SOURCE_URL)
            url_accessible, url_msg = await ScraperConfigValidator.test_url_accessible(url)
            source_result["accessible"] = url_accessible
            source_result["access_message"] = url_msg
            
            if not url_accessible:
                results["warnings"].append(f"Source {i}: {url_msg}")
            
            # Test selectors if HTML method
            if source.get(CONF_SOURCE_METHOD) == SCRAPER_METHOD_HTML:
                selectors = source.get(CONF_SOURCE_SELECTORS, {})
                if not selectors:
                    results["warnings"].append(
                        f"Source {i}: No selectors configured for HTML method"
                    )
                elif url_accessible:
                    # We would need to fetch HTML to test selectors
                    # This is optional in the validator
                    source_result["selectors_tested"] = False
                    source_result["selectors_message"] = "Selectors configured but not tested"
            
            results["sources"].append(source_result)
        
        if not sources:
            results["valid"] = False
            results["errors"].append("No sources configured")
        
        return results


def create_example_config() -> dict[str, Any]:
    """Create an example scraper configuration."""
    return {
        CONF_SCRAPER_SOURCES: [
            {
                CONF_SOURCE_URL: "https://www.example.com/training",
                CONF_SOURCE_TYPE: EVENT_TYPE_TRAINING,
                CONF_SOURCE_METHOD: SCRAPER_METHOD_HTML,
                CONF_SOURCE_SELECTORS: {
                    "container": "div.event-item",
                    "date": "span.date",
                    "time": "span.time",
                    "title": "span.title",
                },
            },
            {
                CONF_SOURCE_URL: "https://www.example.com/matches",
                CONF_SOURCE_TYPE: EVENT_TYPE_MATCH,
                CONF_SOURCE_METHOD: SCRAPER_METHOD_HTML,
                CONF_SOURCE_SELECTORS: {
                    "container": "div.match-item",
                    "date": "span.match-date",
                    "time": "span.match-time",
                    "title": "span.match-title",
                },
            },
        ],
        CONF_DATE_FORMAT: "%d-%m-%Y",
        CONF_TIME_FORMAT: "%H:%M",
        CONF_TIMEZONE: "Europe/Amsterdam",
    }

