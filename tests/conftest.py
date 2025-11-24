"""Pytest configuration and fixtures."""
import pytest
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the custom component
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations for all tests."""
    return enable_custom_integrations

