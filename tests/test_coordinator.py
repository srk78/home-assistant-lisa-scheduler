"""Tests for the coordinator."""
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

from homeassistant.core import HomeAssistant

from custom_components.lisa_scheduler.coordinator import LISASchedulerCoordinator
from custom_components.lisa_scheduler.scraper import Event
from custom_components.lisa_scheduler.const import EVENT_TYPE_TRAINING


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
        pre_event_minutes=120,
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

    coordinator.update_settings(pre_event_minutes=90, scan_interval=3600)

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
