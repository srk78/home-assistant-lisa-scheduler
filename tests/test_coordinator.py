"""Tests for the coordinator."""
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

from homeassistant.core import HomeAssistant

from custom_components.lisa_scheduler.coordinator import LISASchedulerCoordinator
from custom_components.lisa_scheduler.scraper import Event
from custom_components.lisa_scheduler.const import (
    EVENT_TYPE_TRAINING,
    EVENT_FIRST_EVENT_STARTED,
    EVENT_LAST_EVENT_ENDED,
    EVENT_PRE_FIRST_EVENT_TRIGGER,
    EVENT_PRE_LAST_EVENT_END_TRIGGER,
    EVENT_POST_LAST_EVENT_TRIGGER,
)


@pytest.fixture
def mock_hass():
    hass = MagicMock(spec=HomeAssistant)
    hass.services = MagicMock()
    hass.services.async_call = AsyncMock()
    hass.async_create_task = MagicMock()
    hass.bus = MagicMock()
    hass.bus.async_fire = MagicMock()
    return hass


@pytest.fixture
def sample_events():
    now = datetime.now()
    return [
        Event(
            event_type=EVENT_TYPE_TRAINING,
            start_time=now + timedelta(hours=3),
            end_time=now + timedelta(hours=5),
            title="Training 1",
        ),
    ]


def _make_coordinator(mock_hass, **kwargs):
    defaults = dict(
        schedule_url="http://example.com/schedule",
        pre_event_triggers=[120],
        scan_interval=21600,
        enabled=True,
        dry_run=False,
    )
    defaults.update(kwargs)
    return LISASchedulerCoordinator(hass=mock_hass, **defaults)


@pytest.mark.asyncio
async def test_coordinator_initialization(mock_hass):
    coordinator = _make_coordinator(mock_hass)

    assert coordinator.schedule_url == "http://example.com/schedule"
    assert coordinator.scheduler.pre_event_triggers == [120]
    assert coordinator.scheduler.pre_event_minutes == 120
    assert coordinator.enabled is True
    assert coordinator.dry_run is False


@pytest.mark.asyncio
async def test_coordinator_set_enabled(mock_hass):
    coordinator = _make_coordinator(mock_hass)

    coordinator.set_enabled(False)
    assert coordinator.enabled is False

    coordinator.set_enabled(True)
    assert coordinator.enabled is True


@pytest.mark.asyncio
async def test_coordinator_set_override(mock_hass):
    coordinator = _make_coordinator(mock_hass)
    start_time = datetime.now() + timedelta(hours=1)
    end_time = datetime.now() + timedelta(hours=3)

    coordinator.set_override(start_time, end_time)

    assert coordinator.manual_override is not None
    assert coordinator.manual_override[0] == start_time
    assert coordinator.manual_override[1] == end_time


@pytest.mark.asyncio
async def test_coordinator_clear_override(mock_hass):
    coordinator = _make_coordinator(mock_hass)
    coordinator.set_override(datetime.now() + timedelta(hours=1), datetime.now() + timedelta(hours=3))
    assert coordinator.manual_override is not None

    coordinator.clear_override()
    assert coordinator.manual_override is None


@pytest.mark.asyncio
async def test_coordinator_calculate_window_state_disabled(mock_hass):
    coordinator = _make_coordinator(mock_hass, enabled=False)
    assert coordinator._calculate_window_state(datetime.now()) is False


@pytest.mark.asyncio
async def test_coordinator_calculate_window_state_with_override(mock_hass):
    coordinator = _make_coordinator(mock_hass, enabled=True)
    now = datetime.now()
    coordinator.set_override(now - timedelta(minutes=30), now + timedelta(hours=2))
    assert coordinator._calculate_window_state(now) is True


@pytest.mark.asyncio
async def test_coordinator_update_settings(mock_hass):
    coordinator = _make_coordinator(mock_hass)

    coordinator.update_settings(pre_event_triggers=[90], scan_interval=3600)

    assert coordinator.scheduler.pre_event_triggers == [90]
    assert coordinator.scheduler.pre_event_minutes == 90
    assert coordinator.scan_interval == 3600


@pytest.mark.asyncio
async def test_coordinator_should_refresh_schedule(mock_hass):
    coordinator = _make_coordinator(mock_hass, scan_interval=3600)

    assert coordinator._should_refresh_schedule(datetime.now()) is True

    coordinator.last_schedule_update = datetime.now()
    assert coordinator._should_refresh_schedule(datetime.now()) is False

    future_time = datetime.now() + timedelta(seconds=3601)
    assert coordinator._should_refresh_schedule(future_time) is True


@pytest.mark.asyncio
async def test_coordinator_dry_run_mode(mock_hass):
    coordinator = _make_coordinator(mock_hass, enabled=True, dry_run=True)
    assert coordinator.dry_run is True


@pytest.mark.asyncio
async def test_coordinator_fires_window_started(mock_hass):
    coordinator = _make_coordinator(mock_hass, enabled=True, dry_run=False)
    now = datetime.now()

    # Transition: not active → active
    coordinator.is_window_active = False
    coordinator._fire_transition_events(True, False, now)

    mock_hass.bus.async_fire.assert_called_once()
    call_args = mock_hass.bus.async_fire.call_args[0]
    assert call_args[0] == "lisa_scheduler_window_started"


@pytest.mark.asyncio
async def test_coordinator_fires_window_ended(mock_hass):
    coordinator = _make_coordinator(mock_hass, enabled=True, dry_run=False)
    now = datetime.now()

    # Transition: active → not active
    coordinator.is_window_active = True
    coordinator.is_event_active = False
    coordinator._fire_transition_events(False, False, now)

    mock_hass.bus.async_fire.assert_called_once()
    call_args = mock_hass.bus.async_fire.call_args[0]
    assert call_args[0] == "lisa_scheduler_window_ended"


@pytest.mark.asyncio
async def test_coordinator_fires_event_started(mock_hass):
    coordinator = _make_coordinator(mock_hass, enabled=True, dry_run=False)
    now = datetime.now()

    coordinator.is_window_active = True
    coordinator.is_event_active = False
    coordinator._fire_transition_events(True, True, now)

    fired = [c[0][0] for c in mock_hass.bus.async_fire.call_args_list]
    assert "lisa_scheduler_event_started" in fired


@pytest.mark.asyncio
async def test_coordinator_no_duplicate_events(mock_hass):
    coordinator = _make_coordinator(mock_hass, enabled=True, dry_run=False)
    now = datetime.now()

    # No state change — no events should fire
    coordinator.is_window_active = True
    coordinator.is_event_active = True
    coordinator._fire_transition_events(True, True, now)

    mock_hass.bus.async_fire.assert_not_called()


def _make_today_events(now, count=2):
    """Create `count` non-overlapping future events today (anchored to `now`)."""
    events = []
    base = now + timedelta(hours=1)
    for i in range(count):
        start = base + timedelta(hours=i * 3)
        end = start + timedelta(hours=2)
        events.append(
            Event(
                event_type=EVENT_TYPE_TRAINING,
                start_time=start,
                end_time=end,
                title=f"Event {i + 1}",
            )
        )
    return events


@pytest.mark.asyncio
async def test_first_and_last_event_of_day_triggers(mock_hass):
    """Verify first_event_started and last_event_ended fire at the right times."""
    coordinator = _make_coordinator(mock_hass, enabled=True, dry_run=False, pre_event_triggers=[0])

    now = datetime.now()
    events = _make_today_events(now, count=2)
    # Manually load windows so no scraping is needed
    coordinator.events = events
    coordinator.event_windows = coordinator.scheduler.calculate_event_windows(events, now=now - timedelta(hours=1))

    first_event_start = events[0].start_time
    last_event_end = events[-1].end_time

    # --- Advance to just after first event starts ---
    t1 = first_event_start + timedelta(seconds=30)
    coordinator._fire_day_boundary_events(t1)

    fired_events = [c[0][0] for c in mock_hass.bus.async_fire.call_args_list]
    assert EVENT_FIRST_EVENT_STARTED in fired_events
    assert EVENT_LAST_EVENT_ENDED not in fired_events

    mock_hass.bus.async_fire.reset_mock()

    # --- Advance to just after last event ends ---
    t2 = last_event_end + timedelta(seconds=30)
    coordinator._fire_day_boundary_events(t2)

    fired_events2 = [c[0][0] for c in mock_hass.bus.async_fire.call_args_list]
    assert EVENT_LAST_EVENT_ENDED in fired_events2

    # Calling again should NOT re-fire (deduplication)
    mock_hass.bus.async_fire.reset_mock()
    coordinator._fire_day_boundary_events(t2 + timedelta(seconds=60))
    mock_hass.bus.async_fire.assert_not_called()


@pytest.mark.asyncio
async def test_pre_post_day_boundary_triggers(mock_hass):
    """Verify pre_first, pre_last_end and post_last triggers fire correctly."""
    now = datetime.now()
    events = _make_today_events(now, count=2)

    coordinator = _make_coordinator(
        mock_hass,
        enabled=True,
        dry_run=False,
        pre_event_triggers=[0],
        pre_first_event_triggers=[30],
        pre_last_event_end_triggers=[15],
        post_last_event_triggers=[10],
    )
    coordinator.events = events
    coordinator.event_windows = coordinator.scheduler.calculate_event_windows(events, now=now - timedelta(hours=1))

    first_event_start = events[0].start_time
    last_window_end = events[-1].end_time

    # --- Fire pre_first trigger (30 min before first event) ---
    t_pre_first = first_event_start - timedelta(minutes=30) + timedelta(seconds=10)
    coordinator._fire_day_boundary_events(t_pre_first)
    fired = [c[0][0] for c in mock_hass.bus.async_fire.call_args_list]
    assert EVENT_PRE_FIRST_EVENT_TRIGGER in fired
    assert EVENT_PRE_LAST_EVENT_END_TRIGGER not in fired
    assert EVENT_POST_LAST_EVENT_TRIGGER not in fired

    mock_hass.bus.async_fire.reset_mock()

    # --- Fire pre_last_end trigger (15 min before last window ends) ---
    t_pre_last_end = last_window_end - timedelta(minutes=15) + timedelta(seconds=10)
    coordinator._fire_day_boundary_events(t_pre_last_end)
    fired2 = [c[0][0] for c in mock_hass.bus.async_fire.call_args_list]
    assert EVENT_PRE_LAST_EVENT_END_TRIGGER in fired2

    mock_hass.bus.async_fire.reset_mock()

    # --- Fire post_last trigger (10 min after last window ends) ---
    t_post_last = last_window_end + timedelta(minutes=10) + timedelta(seconds=10)
    coordinator._fire_day_boundary_events(t_post_last)
    fired3 = [c[0][0] for c in mock_hass.bus.async_fire.call_args_list]
    assert EVENT_POST_LAST_EVENT_TRIGGER in fired3

    # Payload should include minutes_after
    post_call = next(
        c for c in mock_hass.bus.async_fire.call_args_list
        if c[0][0] == EVENT_POST_LAST_EVENT_TRIGGER
    )
    assert post_call[0][1]["minutes_after"] == 10


@pytest.mark.asyncio
async def test_day_boundary_events_disabled_coordinator(mock_hass):
    """Day boundary events must not fire when coordinator is disabled."""
    now = datetime.now()
    events = _make_today_events(now, count=1)

    coordinator = _make_coordinator(mock_hass, enabled=False, pre_event_triggers=[0])
    coordinator.events = events
    coordinator.event_windows = coordinator.scheduler.calculate_event_windows(events, now=now - timedelta(hours=1))

    t = events[0].start_time + timedelta(seconds=30)
    coordinator._fire_day_boundary_events(t)

    mock_hass.bus.async_fire.assert_not_called()


@pytest.mark.asyncio
async def test_day_boundary_events_dry_run(mock_hass):
    """In dry_run mode, day boundary events must NOT call async_fire."""
    now = datetime.now()
    events = _make_today_events(now, count=1)

    coordinator = _make_coordinator(
        mock_hass, enabled=True, dry_run=True, pre_event_triggers=[0],
        pre_first_event_triggers=[5],
        post_last_event_triggers=[5],
    )
    coordinator.events = events
    coordinator.event_windows = coordinator.scheduler.calculate_event_windows(events, now=now - timedelta(hours=1))

    # After first event and after last window ends
    t = events[0].end_time + timedelta(minutes=6)
    coordinator._fire_day_boundary_events(t)

    mock_hass.bus.async_fire.assert_not_called()
