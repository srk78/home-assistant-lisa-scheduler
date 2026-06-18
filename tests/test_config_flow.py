"""Tests for config and options flow helpers."""
from unittest.mock import MagicMock

import pytest

from custom_components.lisa_scheduler.config_flow import LISASchedulerOptionsFlow
from custom_components.lisa_scheduler.const import (
    CONF_DRY_RUN,
    CONF_ENABLED,
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
