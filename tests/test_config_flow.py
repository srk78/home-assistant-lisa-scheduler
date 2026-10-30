"""Tests for config and options flow helpers."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lisa_scheduler import CONFIG_SCHEMA, async_migrate_entry
from custom_components.lisa_scheduler.api_client import ScheduleApiForbiddenError
from custom_components.lisa_scheduler.config_flow import LISASchedulerOptionsFlow
from custom_components.lisa_scheduler.const import (
    CONF_API_TIMEZONE,
    CONF_API_URL,
    CONF_DRY_RUN,
    CONF_ENABLED,
    CONF_INCLUDE_EXTERNAL_EVENTS,
    CONF_LOGO_URL,
    CONF_POST_LAST_EVENT_TRIGGERS,
    CONF_PRE_EVENT_TRIGGERS,
    CONF_PRE_FIRST_EVENT_TRIGGERS,
    CONF_PRE_LAST_EVENT_END_TRIGGERS,
    CONF_SCAN_INTERVAL,
    DEFAULT_DRY_RUN,
    DEFAULT_ENABLED,
    DEFAULT_PRE_EVENT_TRIGGERS,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    LEGACY_CONF_SCHEDULE_URL,
)


def _flow() -> LISASchedulerOptionsFlow:
    config_entry = MagicMock()
    config_entry.options = {}
    config_entry.data = {
        CONF_LOGO_URL: "",
        CONF_PRE_EVENT_TRIGGERS: DEFAULT_PRE_EVENT_TRIGGERS,
        CONF_PRE_FIRST_EVENT_TRIGGERS: [],
        CONF_PRE_LAST_EVENT_END_TRIGGERS: [],
        CONF_POST_LAST_EVENT_TRIGGERS: [],
        CONF_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL,
        CONF_ENABLED: DEFAULT_ENABLED,
        CONF_DRY_RUN: DEFAULT_DRY_RUN,
        CONF_INCLUDE_EXTERNAL_EVENTS: False,
    }
    return LISASchedulerOptionsFlow(config_entry)


@pytest.mark.asyncio
async def test_options_flow_parses_trigger_strings():
    result = await _flow().async_step_init(
        {
            CONF_LOGO_URL: "",
            CONF_PRE_EVENT_TRIGGERS: "30, 120, 30",
            CONF_PRE_FIRST_EVENT_TRIGGERS: "45",
            CONF_PRE_LAST_EVENT_END_TRIGGERS: "15",
            CONF_POST_LAST_EVENT_TRIGGERS: "10",
            CONF_SCAN_INTERVAL: 3600,
            CONF_ENABLED: True,
            CONF_DRY_RUN: False,
        }
    )

    assert result["type"] == "create_entry"
    data = result["data"]
    assert data[CONF_PRE_EVENT_TRIGGERS] == [120, 30]
    assert data[CONF_PRE_FIRST_EVENT_TRIGGERS] == [45]
    assert data[CONF_PRE_LAST_EVENT_END_TRIGGERS] == [15]
    assert data[CONF_POST_LAST_EVENT_TRIGGERS] == [10]


@pytest.mark.asyncio
async def test_options_flow_rejects_invalid_trigger_strings():
    result = await _flow().async_step_init(
        {
            CONF_LOGO_URL: "",
            CONF_PRE_EVENT_TRIGGERS: "120, nope",
            CONF_PRE_FIRST_EVENT_TRIGGERS: "",
            CONF_PRE_LAST_EVENT_END_TRIGGERS: "",
            CONF_POST_LAST_EVENT_TRIGGERS: "",
            CONF_SCAN_INTERVAL: 3600,
            CONF_ENABLED: True,
            CONF_DRY_RUN: False,
        }
    )

    assert result["type"] == "form"
    assert result["errors"] == {"base": "invalid_triggers"}


@pytest.mark.asyncio
async def test_options_flow_empty_optional_triggers_save_as_empty_lists():
    result = await _flow().async_step_init(
        {
            CONF_LOGO_URL: "",
            CONF_PRE_EVENT_TRIGGERS: "120",
            CONF_PRE_FIRST_EVENT_TRIGGERS: "",
            CONF_PRE_LAST_EVENT_END_TRIGGERS: "",
            CONF_POST_LAST_EVENT_TRIGGERS: "",
            CONF_SCAN_INTERVAL: 3600,
            CONF_ENABLED: True,
            CONF_DRY_RUN: False,
        }
    )

    assert result["type"] == "create_entry"
    data = result["data"]
    assert data[CONF_PRE_FIRST_EVENT_TRIGGERS] == []
    assert data[CONF_PRE_LAST_EVENT_END_TRIGGERS] == []
    assert data[CONF_POST_LAST_EVENT_TRIGGERS] == []


def _user_input(**overrides):
    data = {
        CONF_API_URL: "http://schedule.local",
        CONF_INCLUDE_EXTERNAL_EVENTS: False,
        CONF_LOGO_URL: "",
        CONF_PRE_EVENT_TRIGGERS: "30, 120, 30",
        CONF_PRE_FIRST_EVENT_TRIGGERS: "",
        CONF_PRE_LAST_EVENT_END_TRIGGERS: "",
        CONF_POST_LAST_EVENT_TRIGGERS: "",
        CONF_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL,
        CONF_DRY_RUN: False,
    }
    data.update(overrides)
    return data


def test_yaml_schema_accepts_api_and_logo_configuration():
    result = CONFIG_SCHEMA(
        {
            DOMAIN: {
                CONF_API_URL: "http://schedule.local",
                CONF_INCLUDE_EXTERNAL_EVENTS: False,
                CONF_LOGO_URL: "https://club.example/logo.png",
                CONF_PRE_EVENT_TRIGGERS: [120, 30],
                CONF_SCAN_INTERVAL: 600,
            }
        }
    )

    assert result[DOMAIN][CONF_API_URL] == "http://schedule.local"
    assert result[DOMAIN][CONF_LOGO_URL] == "https://club.example/logo.png"


@pytest.mark.asyncio
async def test_user_flow_validates_and_normalizes_api(hass):
    with patch(
        "custom_components.lisa_scheduler.config_flow.validate_api",
        AsyncMock(return_value="Europe/Amsterdam"),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "user"}, data=_user_input()
        )

    assert result["type"] == "create_entry"
    assert result["data"][CONF_API_URL] == "http://schedule.local/v1/events"
    assert result["data"][CONF_API_TIMEZONE] == "Europe/Amsterdam"
    assert result["data"][CONF_PRE_EVENT_TRIGGERS] == [120, 30]
    assert result["data"][CONF_INCLUDE_EXTERNAL_EVENTS] is False
    assert result["data"][CONF_SCAN_INTERVAL] == 600


@pytest.mark.asyncio
async def test_user_flow_rejects_duplicate_api_url(hass):
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="http://schedule.local/v1/events",
        data={CONF_API_URL: "http://schedule.local/v1/events"},
    )
    entry.add_to_hass(hass)

    with patch(
        "custom_components.lisa_scheduler.config_flow.validate_api",
        AsyncMock(return_value="Europe/Amsterdam"),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "user"}, data=_user_input()
        )

    assert result["type"] == "abort"
    assert result["reason"] == "already_configured"


@pytest.mark.asyncio
async def test_user_flow_reports_forbidden_api(hass):
    with patch(
        "custom_components.lisa_scheduler.config_flow.validate_api",
        AsyncMock(side_effect=ScheduleApiForbiddenError("forbidden")),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "user"}, data=_user_input()
        )

    assert result["type"] == "form"
    assert result["errors"] == {"base": "forbidden"}


@pytest.mark.asyncio
async def test_yaml_import_validates_and_normalizes_api(hass):
    data = {
        CONF_API_URL: "http://schedule.local",
        CONF_INCLUDE_EXTERNAL_EVENTS: False,
        CONF_PRE_EVENT_TRIGGERS: [120],
        CONF_SCAN_INTERVAL: 600,
        CONF_DRY_RUN: False,
    }
    with patch(
        "custom_components.lisa_scheduler.config_flow.validate_api",
        AsyncMock(return_value="Europe/Amsterdam"),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "import"}, data=data
        )

    assert result["type"] == "create_entry"
    assert result["data"][CONF_API_URL] == "http://schedule.local/v1/events"
    assert result["data"][CONF_API_TIMEZONE] == "Europe/Amsterdam"


@pytest.mark.asyncio
async def test_reconfigure_updates_api_url(hass):
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="http://old.local/v1/events",
        data={
            CONF_API_URL: "http://old.local/v1/events",
            CONF_API_TIMEZONE: "Europe/Amsterdam",
        },
    )
    entry.add_to_hass(hass)

    with patch(
        "custom_components.lisa_scheduler.config_flow.validate_api",
        AsyncMock(return_value="Europe/Amsterdam"),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": "reconfigure", "entry_id": entry.entry_id},
            data={CONF_API_URL: "http://new.local"},
        )

    assert result["type"] == "abort"
    assert result["reason"] == "reconfigure_successful"
    assert entry.data[CONF_API_URL] == "http://new.local/v1/events"


@pytest.mark.asyncio
async def test_v1_entry_migrates_without_scraper_options(hass):
    entry = MockConfigEntry(
        domain=DOMAIN,
        version=1,
        data={
            LEGACY_CONF_SCHEDULE_URL: "http://schedule.local",
            "scraper_sources": [{"url": "http://old.local"}],
            CONF_SCAN_INTERVAL: 3600,
        },
        options={"date_format": "%d-%m-%Y"},
    )
    entry.add_to_hass(hass)
    assert await async_migrate_entry(hass, entry) is True
    assert entry.version == 2
    assert entry.data[CONF_API_URL] == "http://schedule.local/v1/events"
    assert entry.data[CONF_SCAN_INTERVAL] == 3600
    assert entry.data[CONF_INCLUDE_EXTERNAL_EVENTS] is False
    assert "scraper_sources" not in entry.data
    assert "date_format" not in entry.options
