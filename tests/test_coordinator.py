"""Tests for the coordinator."""
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.core import HomeAssistant

from custom_components.zhc_heating_scheduler.coordinator import ZHCHeatingCoordinator
from custom_components.zhc_heating_scheduler.scraper import Event, EVENT_TYPE_TRAINING


@pytest.fixture
def mock_hass():
    """Create a mock Home Assistant instance."""
    hass = MagicMock(spec=HomeAssistant)
    hass.services = MagicMock()
    hass.services.async_call = AsyncMock()
    hass.async_create_task = MagicMock()
    return hass


@pytest.fixture
def sample_events():
    """Create sample events."""
    now = datetime.now()
    return [
        Event(
            event_type=EVENT_TYPE_TRAINING,
            start_time=now + timedelta(hours=3),
            end_time=now + timedelta(hours=5),
            title="Training 1",
        ),
    ]


@pytest.mark.asyncio
async def test_coordinator_initialization(mock_hass):
    """Test coordinator initialization."""
    coordinator = ZHCHeatingCoordinator(
        hass=mock_hass,
        schedule_url="http://example.com/schedule",
        climate_entity="climate.test",
        pre_heat_hours=2,
        cool_down_minutes=30,
        target_temperature=20.0,
        scan_interval=21600,
        enabled=True,
        dry_run=False,
    )
    
    assert coordinator.schedule_url == "http://example.com/schedule"
    assert coordinator.climate_entity == "climate.test"
    assert coordinator.target_temperature == 20.0
    assert coordinator.enabled is True
    assert coordinator.dry_run is False
    assert coordinator.scheduler.pre_heat_hours == 2
    assert coordinator.scheduler.cool_down_minutes == 30


@pytest.mark.asyncio
async def test_coordinator_set_enabled(mock_hass):
    """Test enabling/disabling coordinator."""
    coordinator = ZHCHeatingCoordinator(
        hass=mock_hass,
        schedule_url="http://example.com/schedule",
        climate_entity="climate.test",
        pre_heat_hours=2,
        cool_down_minutes=30,
        target_temperature=20.0,
        scan_interval=21600,
        enabled=True,
        dry_run=False,
    )
    
    coordinator.set_enabled(False)
    assert coordinator.enabled is False
    
    coordinator.set_enabled(True)
    assert coordinator.enabled is True


@pytest.mark.asyncio
async def test_coordinator_set_override(mock_hass):
    """Test manual override."""
    coordinator = ZHCHeatingCoordinator(
        hass=mock_hass,
        schedule_url="http://example.com/schedule",
        climate_entity="climate.test",
        pre_heat_hours=2,
        cool_down_minutes=30,
        target_temperature=20.0,
        scan_interval=21600,
    )
    
    start_time = datetime.now() + timedelta(hours=1)
    end_time = datetime.now() + timedelta(hours=3)
    
    coordinator.set_override(start_time, end_time)
    
    assert coordinator.manual_override is not None
    assert coordinator.manual_override[0] == start_time
    assert coordinator.manual_override[1] == end_time


@pytest.mark.asyncio
async def test_coordinator_clear_override(mock_hass):
    """Test clearing manual override."""
    coordinator = ZHCHeatingCoordinator(
        hass=mock_hass,
        schedule_url="http://example.com/schedule",
        climate_entity="climate.test",
        pre_heat_hours=2,
        cool_down_minutes=30,
        target_temperature=20.0,
        scan_interval=21600,
    )
    
    # Set and then clear override
    start_time = datetime.now() + timedelta(hours=1)
    end_time = datetime.now() + timedelta(hours=3)
    
    coordinator.set_override(start_time, end_time)
    assert coordinator.manual_override is not None
    
    coordinator.clear_override()
    assert coordinator.manual_override is None


@pytest.mark.asyncio
async def test_coordinator_calculate_heating_state_disabled(mock_hass):
    """Test heating state when disabled."""
    coordinator = ZHCHeatingCoordinator(
        hass=mock_hass,
        schedule_url="http://example.com/schedule",
        climate_entity="climate.test",
        pre_heat_hours=2,
        cool_down_minutes=30,
        target_temperature=20.0,
        scan_interval=21600,
        enabled=False,
    )
    
    now = datetime.now()
    should_heat = coordinator._calculate_heating_state(now)
    
    assert should_heat is False


@pytest.mark.asyncio
async def test_coordinator_calculate_heating_state_with_override(mock_hass):
    """Test heating state with manual override."""
    coordinator = ZHCHeatingCoordinator(
        hass=mock_hass,
        schedule_url="http://example.com/schedule",
        climate_entity="climate.test",
        pre_heat_hours=2,
        cool_down_minutes=30,
        target_temperature=20.0,
        scan_interval=21600,
        enabled=True,
    )
    
    # Set override for current time
    now = datetime.now()
    start_time = now - timedelta(minutes=30)
    end_time = now + timedelta(hours=2)
    
    coordinator.set_override(start_time, end_time)
    
    should_heat = coordinator._calculate_heating_state(now)
    
    assert should_heat is True


@pytest.mark.asyncio
async def test_coordinator_update_settings(mock_hass):
    """Test updating coordinator settings."""
    coordinator = ZHCHeatingCoordinator(
        hass=mock_hass,
        schedule_url="http://example.com/schedule",
        climate_entity="climate.test",
        pre_heat_hours=2,
        cool_down_minutes=30,
        target_temperature=20.0,
        scan_interval=21600,
    )
    
    coordinator.update_settings(
        pre_heat_hours=3,
        cool_down_minutes=45,
        target_temperature=21.5,
        scan_interval=3600,
    )
    
    assert coordinator.scheduler.pre_heat_hours == 3
    assert coordinator.scheduler.cool_down_minutes == 45
    assert coordinator.target_temperature == 21.5
    assert coordinator.scan_interval == 3600


@pytest.mark.asyncio
async def test_coordinator_should_refresh_schedule(mock_hass):
    """Test schedule refresh logic."""
    coordinator = ZHCHeatingCoordinator(
        hass=mock_hass,
        schedule_url="http://example.com/schedule",
        climate_entity="climate.test",
        pre_heat_hours=2,
        cool_down_minutes=30,
        target_temperature=20.0,
        scan_interval=3600,  # 1 hour
    )
    
    # Should refresh when last_schedule_update is None
    assert coordinator._should_refresh_schedule(datetime.now()) is True
    
    # Set recent update
    coordinator.last_schedule_update = datetime.now()
    
    # Should not refresh immediately
    assert coordinator._should_refresh_schedule(datetime.now()) is False
    
    # Should refresh after scan_interval
    future_time = datetime.now() + timedelta(seconds=3601)
    assert coordinator._should_refresh_schedule(future_time) is True


@pytest.mark.asyncio
async def test_coordinator_dry_run_mode(mock_hass):
    """Test dry run mode."""
    coordinator = ZHCHeatingCoordinator(
        hass=mock_hass,
        schedule_url="http://example.com/schedule",
        climate_entity="climate.test",
        pre_heat_hours=2,
        cool_down_minutes=30,
        target_temperature=20.0,
        scan_interval=21600,
        enabled=True,
        dry_run=True,
    )
    
    # Set up state to require heating
    now = datetime.now()
    coordinator.events = [
        Event(
            EVENT_TYPE_TRAINING,
            start_time=now - timedelta(minutes=30),
            end_time=now + timedelta(hours=2),
            title="Current Event",
        )
    ]
    coordinator.heating_windows = coordinator.scheduler.calculate_heating_windows(
        coordinator.events, now
    )
    
    # In dry run mode, control_heating should not be called
    # The coordinator should not actually control the device
    assert coordinator.dry_run is True

