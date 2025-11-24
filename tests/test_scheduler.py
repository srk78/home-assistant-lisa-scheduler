"""Tests for the heating scheduler."""
import pytest
from datetime import datetime, timedelta

from custom_components.zhc_heating_scheduler.scheduler import (
    HeatingWindow,
    HeatingScheduler,
)
from custom_components.zhc_heating_scheduler.scraper import Event, EVENT_TYPE_TRAINING


@pytest.fixture
def sample_events():
    """Create sample events for testing."""
    now = datetime.now()
    return [
        Event(
            event_type=EVENT_TYPE_TRAINING,
            start_time=now + timedelta(hours=3),
            end_time=now + timedelta(hours=5),
            title="Training 1",
        ),
        Event(
            event_type=EVENT_TYPE_TRAINING,
            start_time=now + timedelta(hours=6),
            end_time=now + timedelta(hours=8),
            title="Training 2",
        ),
        Event(
            event_type=EVENT_TYPE_TRAINING,
            start_time=now + timedelta(days=1),
            end_time=now + timedelta(days=1, hours=2),
            title="Training Tomorrow",
        ),
    ]


def test_heating_window_creation():
    """Test HeatingWindow creation."""
    start = datetime(2024, 11, 24, 14, 0)
    end = datetime(2024, 11, 24, 16, 0)
    
    window = HeatingWindow(start, end)
    
    assert window.start_time == start
    assert window.end_time == end
    assert len(window.events) == 0


def test_heating_window_overlaps():
    """Test overlap detection between windows."""
    window1 = HeatingWindow(
        datetime(2024, 11, 24, 14, 0),
        datetime(2024, 11, 24, 16, 0),
    )
    window2 = HeatingWindow(
        datetime(2024, 11, 24, 15, 0),
        datetime(2024, 11, 24, 17, 0),
    )
    window3 = HeatingWindow(
        datetime(2024, 11, 24, 18, 0),
        datetime(2024, 11, 24, 20, 0),
    )
    
    assert window1.overlaps(window2) is True
    assert window2.overlaps(window1) is True
    assert window1.overlaps(window3) is False
    assert window3.overlaps(window1) is False


def test_heating_window_merge():
    """Test merging of overlapping windows."""
    event1 = Event(
        EVENT_TYPE_TRAINING,
        datetime(2024, 11, 24, 14, 0),
        datetime(2024, 11, 24, 16, 0),
        "Event 1",
    )
    event2 = Event(
        EVENT_TYPE_TRAINING,
        datetime(2024, 11, 24, 15, 30),
        datetime(2024, 11, 24, 17, 0),
        "Event 2",
    )
    
    window1 = HeatingWindow(
        datetime(2024, 11, 24, 14, 0),
        datetime(2024, 11, 24, 16, 0),
        [event1],
    )
    window2 = HeatingWindow(
        datetime(2024, 11, 24, 15, 0),
        datetime(2024, 11, 24, 17, 0),
        [event2],
    )
    
    merged = window1.merge(window2)
    
    assert merged.start_time == datetime(2024, 11, 24, 14, 0)
    assert merged.end_time == datetime(2024, 11, 24, 17, 0)
    assert len(merged.events) == 2


def test_heating_window_contains():
    """Test if window contains a datetime."""
    window = HeatingWindow(
        datetime(2024, 11, 24, 14, 0),
        datetime(2024, 11, 24, 16, 0),
    )
    
    assert window.contains(datetime(2024, 11, 24, 15, 0)) is True
    assert window.contains(datetime(2024, 11, 24, 14, 0)) is True
    assert window.contains(datetime(2024, 11, 24, 16, 0)) is True
    assert window.contains(datetime(2024, 11, 24, 13, 0)) is False
    assert window.contains(datetime(2024, 11, 24, 17, 0)) is False


def test_scheduler_creation():
    """Test HeatingScheduler creation."""
    scheduler = HeatingScheduler(pre_heat_hours=2, cool_down_minutes=30)
    
    assert scheduler.pre_heat_hours == 2
    assert scheduler.cool_down_minutes == 30


def test_scheduler_calculate_heating_windows(sample_events):
    """Test heating window calculation."""
    scheduler = HeatingScheduler(pre_heat_hours=2, cool_down_minutes=30)
    
    windows = scheduler.calculate_heating_windows(sample_events)
    
    assert len(windows) > 0
    assert all(isinstance(w, HeatingWindow) for w in windows)
    
    # Check that pre-heat is applied
    first_window = windows[0]
    first_event = sample_events[0]
    
    # Window should start 2 hours before event
    expected_start = first_event.start_time - timedelta(hours=2)
    assert abs((first_window.start_time - expected_start).total_seconds()) < 60


def test_scheduler_merge_overlapping_windows():
    """Test that overlapping windows are merged."""
    scheduler = HeatingScheduler(pre_heat_hours=2, cool_down_minutes=15)
    
    now = datetime.now()
    # Create events that will result in overlapping heating windows
    events = [
        Event(
            EVENT_TYPE_TRAINING,
            start_time=now + timedelta(hours=3),
            end_time=now + timedelta(hours=5),
            title="Event 1",
        ),
        Event(
            EVENT_TYPE_TRAINING,
            start_time=now + timedelta(hours=4),  # Overlaps with first
            end_time=now + timedelta(hours=6),
            title="Event 2",
        ),
    ]
    
    windows = scheduler.calculate_heating_windows(events)
    
    # Should be merged into one window
    assert len(windows) == 1
    assert len(windows[0].events) == 2


def test_scheduler_should_heat_now(sample_events):
    """Test should_heat_now logic."""
    scheduler = HeatingScheduler(pre_heat_hours=2, cool_down_minutes=30)
    
    windows = scheduler.calculate_heating_windows(sample_events)
    
    # Test with a time outside any window
    far_past = datetime.now() - timedelta(days=1)
    assert scheduler.should_heat_now(windows, far_past) is False
    
    # Test with a time inside the first window
    if windows:
        inside_first = windows[0].start_time + timedelta(minutes=30)
        assert scheduler.should_heat_now(windows, inside_first) is True


def test_scheduler_get_current_window(sample_events):
    """Test getting current heating window."""
    scheduler = HeatingScheduler(pre_heat_hours=2, cool_down_minutes=30)
    
    windows = scheduler.calculate_heating_windows(sample_events)
    
    # Test with time outside any window
    far_past = datetime.now() - timedelta(days=1)
    assert scheduler.get_current_window(windows, far_past) is None
    
    # Test with time inside first window
    if windows:
        inside_first = windows[0].start_time + timedelta(minutes=30)
        current = scheduler.get_current_window(windows, inside_first)
        assert current is not None
        assert current == windows[0]


def test_scheduler_get_next_window(sample_events):
    """Test getting next heating window."""
    scheduler = HeatingScheduler(pre_heat_hours=2, cool_down_minutes=30)
    
    windows = scheduler.calculate_heating_windows(sample_events)
    
    # Test with time before all windows
    if windows:
        before_all = windows[0].start_time - timedelta(hours=1)
        next_window = scheduler.get_next_window(windows, before_all)
        assert next_window is not None
        assert next_window == windows[0]


def test_scheduler_get_next_state_change(sample_events):
    """Test getting next state change time."""
    scheduler = HeatingScheduler(pre_heat_hours=2, cool_down_minutes=30)
    
    windows = scheduler.calculate_heating_windows(sample_events)
    
    if windows:
        # Test when not heating - next change should be window start
        before_all = windows[0].start_time - timedelta(hours=1)
        change_time, will_heat = scheduler.get_next_state_change(windows, before_all)
        
        assert change_time is not None
        assert will_heat is True
        assert change_time == windows[0].start_time
        
        # Test when heating - next change should be window end
        inside_first = windows[0].start_time + timedelta(minutes=30)
        change_time, will_heat = scheduler.get_next_state_change(windows, inside_first)
        
        assert change_time is not None
        assert will_heat is False
        assert change_time == windows[0].end_time


def test_scheduler_get_schedule_summary(sample_events):
    """Test schedule summary generation."""
    scheduler = HeatingScheduler(pre_heat_hours=2, cool_down_minutes=30)
    
    windows = scheduler.calculate_heating_windows(sample_events)
    
    summary = scheduler.get_schedule_summary(windows)
    
    assert "is_heating" in summary
    assert "current_window" in summary
    assert "next_window" in summary
    assert "total_windows" in summary
    assert "windows_today" in summary
    assert summary["total_windows"] == len(windows)


def test_scheduler_update_settings():
    """Test updating scheduler settings."""
    scheduler = HeatingScheduler(pre_heat_hours=2, cool_down_minutes=30)
    
    scheduler.update_settings(pre_heat_hours=3, cool_down_minutes=45)
    
    assert scheduler.pre_heat_hours == 3
    assert scheduler.cool_down_minutes == 45


def test_scheduler_skip_past_events():
    """Test that past events are skipped."""
    scheduler = HeatingScheduler(pre_heat_hours=2, cool_down_minutes=30)
    
    now = datetime.now()
    past_event = Event(
        EVENT_TYPE_TRAINING,
        start_time=now - timedelta(hours=5),
        end_time=now - timedelta(hours=3),
        title="Past Event",
    )
    
    windows = scheduler.calculate_heating_windows([past_event])
    
    # Should have no windows (past event ignored)
    assert len(windows) == 0


def test_heating_window_to_dict():
    """Test HeatingWindow to_dict method."""
    event = Event(
        EVENT_TYPE_TRAINING,
        datetime(2024, 11, 24, 14, 0),
        datetime(2024, 11, 24, 16, 0),
        "Test Event",
    )
    
    window = HeatingWindow(
        datetime(2024, 11, 24, 12, 0),
        datetime(2024, 11, 24, 15, 30),
        [event],
    )
    
    window_dict = window.to_dict()
    
    assert "start_time" in window_dict
    assert "end_time" in window_dict
    assert "duration_minutes" in window_dict
    assert "event_count" in window_dict
    assert window_dict["event_count"] == 1
    assert "events" in window_dict

