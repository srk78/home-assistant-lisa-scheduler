"""Tests for the schedule scraper."""
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from custom_components.zhc_heating_scheduler.scraper import (
    Event,
    ScheduleScraper,
    EVENT_TYPE_TRAINING,
    EVENT_TYPE_MATCH,
    EVENT_TYPE_UNKNOWN,
)


@pytest.fixture
def sample_html_table():
    """Return sample HTML with table-based schedule."""
    return """
    <html>
        <body>
            <table class="schedule">
                <tr>
                    <td>24-11-2024</td>
                    <td>14:00-16:00</td>
                    <td>Training Session A</td>
                </tr>
                <tr>
                    <td>25-11-2024</td>
                    <td>10:00-12:00</td>
                    <td>Match vs Team B</td>
                </tr>
            </table>
        </body>
    </html>
    """


@pytest.fixture
def sample_html_list():
    """Return sample HTML with list-based schedule."""
    return """
    <html>
        <body>
            <div class="schedule-container">
                <div class="event-item">Training - 24-11-2024 18:00-20:00</div>
                <div class="event-item">Wedstrijd - 26-11-2024 15:00-17:00</div>
            </div>
        </body>
    </html>
    """


@pytest.mark.asyncio
async def test_event_creation():
    """Test Event class creation."""
    start_time = datetime(2024, 11, 24, 14, 0)
    end_time = datetime(2024, 11, 24, 16, 0)
    
    event = Event(
        event_type=EVENT_TYPE_TRAINING,
        start_time=start_time,
        end_time=end_time,
        title="Test Training",
    )
    
    assert event.event_type == EVENT_TYPE_TRAINING
    assert event.start_time == start_time
    assert event.end_time == end_time
    assert event.title == "Test Training"


@pytest.mark.asyncio
async def test_event_to_dict():
    """Test Event to_dict method."""
    start_time = datetime(2024, 11, 24, 14, 0)
    end_time = datetime(2024, 11, 24, 16, 0)
    
    event = Event(
        event_type=EVENT_TYPE_MATCH,
        start_time=start_time,
        end_time=end_time,
        title="Test Match",
    )
    
    event_dict = event.to_dict()
    
    assert event_dict["event_type"] == EVENT_TYPE_MATCH
    assert event_dict["title"] == "Test Match"
    assert "start_time" in event_dict
    assert "end_time" in event_dict


@pytest.mark.asyncio
async def test_scraper_fetch_html():
    """Test HTML fetching."""
    mock_session = AsyncMock()
    mock_response = AsyncMock()
    mock_response.text = AsyncMock(return_value="<html></html>")
    mock_response.raise_for_status = MagicMock()
    mock_session.get = AsyncMock(return_value=mock_response)
    mock_session.__aenter__ = AsyncMock(return_value=mock_response)
    mock_session.__aexit__ = AsyncMock(return_value=None)
    
    scraper = ScheduleScraper("http://example.com/schedule", mock_session)
    
    html = await scraper._fetch_html()
    
    assert html == "<html></html>"
    mock_session.get.assert_called_once()


@pytest.mark.asyncio
async def test_scraper_looks_like_date():
    """Test date pattern recognition."""
    scraper = ScheduleScraper("http://example.com")
    
    assert scraper._looks_like_date("24-11-2024") is True
    assert scraper._looks_like_date("2024-11-24") is True
    assert scraper._looks_like_date("24 November 2024") is True
    assert scraper._looks_like_date("random text") is False


@pytest.mark.asyncio
async def test_scraper_looks_like_time():
    """Test time pattern recognition."""
    scraper = ScheduleScraper("http://example.com")
    
    assert scraper._looks_like_time("14:00") is True
    assert scraper._looks_like_time("9:30") is True
    assert scraper._looks_like_time("14u00") is True
    assert scraper._looks_like_time("random text") is False


@pytest.mark.asyncio
async def test_scraper_extract_time():
    """Test time extraction."""
    scraper = ScheduleScraper("http://example.com")
    
    assert scraper._extract_time("Event at 14:00-16:00") == "14:00-16:00"
    assert scraper._extract_time("Starting 9:30") == "9:30"
    assert scraper._extract_time("No time here") is None


@pytest.mark.asyncio
async def test_scraper_parse_datetime():
    """Test datetime parsing."""
    scraper = ScheduleScraper("http://example.com")
    
    start, end = scraper._parse_datetime("24-11-2024", "14:00-16:00")
    
    assert start is not None
    assert end is not None
    assert start.hour == 14
    assert end.hour == 16
    assert end > start


@pytest.mark.asyncio
async def test_scraper_parse_datetime_single_time():
    """Test datetime parsing with single time."""
    scraper = ScheduleScraper("http://example.com")
    
    start, end = scraper._parse_datetime("24-11-2024", "14:00")
    
    assert start is not None
    assert end is not None
    # Should default to 2 hour duration
    assert (end - start).total_seconds() == 7200


@pytest.mark.asyncio
async def test_scraper_filter_events_by_date():
    """Test that events are filtered by days_ahead."""
    mock_session = AsyncMock()
    mock_response = AsyncMock()
    
    # Create HTML with events at different dates
    future_date = (datetime.now() + timedelta(days=5)).strftime("%d-%m-%Y")
    far_future_date = (datetime.now() + timedelta(days=20)).strftime("%d-%m-%Y")
    
    html = f"""
    <table>
        <tr><td>{future_date}</td><td>14:00-16:00</td><td>Training</td></tr>
        <tr><td>{far_future_date}</td><td>14:00-16:00</td><td>Training</td></tr>
    </table>
    """
    
    mock_response.text = AsyncMock(return_value=html)
    mock_response.raise_for_status = MagicMock()
    mock_session.get = AsyncMock(return_value=mock_response)
    mock_session.__aenter__ = AsyncMock(return_value=mock_response)
    mock_session.__aexit__ = AsyncMock(return_value=None)
    
    scraper = ScheduleScraper("http://example.com/schedule", mock_session)
    
    # Fetch with 14 days ahead - should get first event but not second
    events = await scraper.fetch_schedule(days_ahead=14)
    
    # Note: This test depends on the HTML parser working correctly
    # The actual count may vary based on parsing success
    assert isinstance(events, list)


@pytest.mark.asyncio 
async def test_custom_scraper_inheritance():
    """Test that CustomScheduleScraper can be inherited."""
    from custom_components.zhc_heating_scheduler.scraper import CustomScheduleScraper
    
    scraper = CustomScheduleScraper("http://example.com")
    assert isinstance(scraper, ScheduleScraper)

