"""Pytest configuration and fixtures."""
import pytest
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

from homeassistant.core import HomeAssistant

# Add the parent directory to the path so we can import the custom component
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations for all tests."""
    return enable_custom_integrations


@pytest.fixture
def mock_hass():
    """Return a minimal mocked Home Assistant object for unit tests."""
    hass = MagicMock(spec=HomeAssistant)
    hass.services = MagicMock()
    hass.services.async_call = AsyncMock()
    hass.async_create_task = MagicMock()
    hass.bus = MagicMock()
    hass.bus.async_fire = MagicMock()
    return hass
