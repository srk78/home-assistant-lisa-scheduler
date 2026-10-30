"""Config flow for LISA Scheduler."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api_client import (
    LisaScheduleApiClient,
    ScheduleApiConnectionError,
    ScheduleApiForbiddenError,
    ScheduleApiResponseError,
    ScheduleApiTimezoneError,
    normalize_api_url,
)
from .const import (
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
    DEFAULT_INCLUDE_EXTERNAL_EVENTS,
    DEFAULT_PRE_EVENT_TRIGGERS,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    LEGACY_CONF_SCHEDULE_URL,
)

_LOGGER = logging.getLogger(__name__)


def _parse_triggers(value: str) -> list[int]:
    """Parse a comma-separated trigger list into sorted unique minutes."""
    try:
        parts = [part.strip() for part in value.split(",") if part.strip()]
        if not parts:
            raise vol.Invalid("At least one trigger time is required")
        values = [int(part) for part in parts]
        if any(value < 0 or value > 1440 for value in values):
            raise vol.Invalid("Trigger times must be between 0 and 1440")
        return sorted(set(values), reverse=True)
    except vol.Invalid:
        raise
    except (TypeError, ValueError) as err:
        raise vol.Invalid(f"Invalid trigger times: {err}") from err


def _parse_optional_triggers(value: str) -> list[int]:
    """Parse optional trigger minutes; blank input becomes an empty list."""
    if not value or not value.strip():
        return []
    return _parse_triggers(value)


async def validate_api(
    hass: HomeAssistant,
    api_url: str,
    include_external_events: bool,
) -> str:
    """Validate an API endpoint and return its declared timezone."""
    client = LisaScheduleApiClient(
        api_url=api_url,
        session=async_get_clientsession(hass),
        timezone=None,
        include_external_events=include_external_events,
    )
    result = await client.async_fetch(days_ahead=1)
    return result.metadata.timezone


def _api_error_key(err: Exception) -> str:
    if isinstance(err, ScheduleApiForbiddenError):
        return "forbidden"
    if isinstance(err, ScheduleApiTimezoneError):
        return "invalid_timezone"
    if isinstance(err, ScheduleApiResponseError):
        return "invalid_api_response"
    if isinstance(err, ScheduleApiConnectionError):
        return "cannot_connect"
    return "unknown"


def _parse_trigger_fields(user_input: dict[str, Any]) -> None:
    user_input[CONF_PRE_EVENT_TRIGGERS] = _parse_triggers(
        user_input[CONF_PRE_EVENT_TRIGGERS]
    )
    user_input[CONF_PRE_FIRST_EVENT_TRIGGERS] = _parse_optional_triggers(
        user_input.get(CONF_PRE_FIRST_EVENT_TRIGGERS, "")
    )
    user_input[CONF_PRE_LAST_EVENT_END_TRIGGERS] = _parse_optional_triggers(
        user_input.get(CONF_PRE_LAST_EVENT_END_TRIGGERS, "")
    )
    user_input[CONF_POST_LAST_EVENT_TRIGGERS] = _parse_optional_triggers(
        user_input.get(CONF_POST_LAST_EVENT_TRIGGERS, "")
    )


def _user_schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Required(CONF_API_URL, default=defaults.get(CONF_API_URL, "")): str,
            vol.Optional(
                CONF_INCLUDE_EXTERNAL_EVENTS,
                default=defaults.get(
                    CONF_INCLUDE_EXTERNAL_EVENTS, DEFAULT_INCLUDE_EXTERNAL_EVENTS
                ),
            ): bool,
            vol.Optional(CONF_LOGO_URL, default=defaults.get(CONF_LOGO_URL, "")): str,
            vol.Optional(
                CONF_PRE_EVENT_TRIGGERS,
                default=defaults.get(
                    CONF_PRE_EVENT_TRIGGERS,
                    ", ".join(str(value) for value in DEFAULT_PRE_EVENT_TRIGGERS),
                ),
            ): str,
            vol.Optional(
                CONF_PRE_FIRST_EVENT_TRIGGERS,
                default=defaults.get(CONF_PRE_FIRST_EVENT_TRIGGERS, ""),
            ): str,
            vol.Optional(
                CONF_PRE_LAST_EVENT_END_TRIGGERS,
                default=defaults.get(CONF_PRE_LAST_EVENT_END_TRIGGERS, ""),
            ): str,
            vol.Optional(
                CONF_POST_LAST_EVENT_TRIGGERS,
                default=defaults.get(CONF_POST_LAST_EVENT_TRIGGERS, ""),
            ): str,
            vol.Optional(
                CONF_SCAN_INTERVAL,
                default=defaults.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
            ): vol.All(vol.Coerce(int), vol.Range(min=600, max=86400)),
            vol.Optional(
                CONF_DRY_RUN,
                default=defaults.get(CONF_DRY_RUN, DEFAULT_DRY_RUN),
            ): bool,
        }
    )


class LISASchedulerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle configuration for LISA Scheduler."""

    VERSION = 2

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        errors: dict[str, str] = {}
        submitted = dict(user_input) if user_input is not None else None

        if submitted is not None:
            try:
                submitted[CONF_API_URL] = normalize_api_url(submitted[CONF_API_URL])
                _parse_trigger_fields(submitted)
            except ValueError:
                errors["base"] = "invalid_url"
            except vol.Invalid:
                errors["base"] = "invalid_triggers"

            if not errors:
                try:
                    submitted[CONF_API_TIMEZONE] = await validate_api(
                        self.hass,
                        submitted[CONF_API_URL],
                        submitted[CONF_INCLUDE_EXTERNAL_EVENTS],
                    )
                except Exception as err:
                    errors["base"] = _api_error_key(err)
                    _LOGGER.warning("API validation failed: %s", err)

            if not errors:
                await self.async_set_unique_id(submitted[CONF_API_URL])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title="LISA Scheduler", data=submitted)

        return self.async_show_form(
            step_id="user",
            data_schema=_user_schema(user_input),  # type: ignore[arg-type]
            errors=errors,
        )

    async def async_step_import(
        self, import_config: dict[str, Any]
    ) -> config_entries.ConfigFlowResult:
        data = dict(import_config)
        try:
            data[CONF_API_URL] = normalize_api_url(data[CONF_API_URL])
            data[CONF_API_TIMEZONE] = await validate_api(
                self.hass,
                data[CONF_API_URL],
                data.get(CONF_INCLUDE_EXTERNAL_EVENTS, DEFAULT_INCLUDE_EXTERNAL_EVENTS),
            )
        except Exception as err:
            _LOGGER.error("Cannot import LISA Scheduler API configuration: %s", err)
            return self.async_abort(reason=_api_error_key(err))

        await self.async_set_unique_id(data[CONF_API_URL])
        self._abort_if_unique_id_configured()
        return self.async_create_entry(title="LISA Scheduler", data=data)

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}
        current_url = entry.data.get(
            CONF_API_URL, entry.data.get(LEGACY_CONF_SCHEDULE_URL, "")
        )

        if user_input is not None:
            try:
                api_url = normalize_api_url(user_input[CONF_API_URL])
                timezone = await validate_api(
                    self.hass,
                    api_url,
                    entry.options.get(
                        CONF_INCLUDE_EXTERNAL_EVENTS,
                        entry.data.get(
                            CONF_INCLUDE_EXTERNAL_EVENTS,
                            DEFAULT_INCLUDE_EXTERNAL_EVENTS,
                        ),
                    ),
                )
            except ValueError:
                errors["base"] = "invalid_url"
            except Exception as err:
                errors["base"] = _api_error_key(err)
                _LOGGER.warning("API reconfiguration failed: %s", err)
            else:
                await self.async_set_unique_id(api_url)
                self._abort_if_unique_id_configured()
                return self.async_update_reload_and_abort(
                    entry,
                    unique_id=api_url,
                    data_updates={
                        **entry.data,
                        CONF_API_URL: api_url,
                        CONF_API_TIMEZONE: timezone,
                    },
                )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(  # type: ignore[arg-type]
                {vol.Required(CONF_API_URL, default=current_url): str}
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> LISASchedulerOptionsFlow:
        return LISASchedulerOptionsFlow(config_entry)


class LISASchedulerOptionsFlow(config_entries.OptionsFlow):
    """Handle mutable scheduler options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        errors: dict[str, str] = {}
        submitted = dict(user_input) if user_input is not None else None

        if submitted is not None:
            try:
                _parse_trigger_fields(submitted)
            except vol.Invalid:
                errors["base"] = "invalid_triggers"
            if not errors:
                return self.async_create_entry(title="", data=submitted)

        def current(key: str, default: Any) -> Any:
            return self._config_entry.options.get(
                key, self._config_entry.data.get(key, default)
            )

        def trigger_string(key: str, default: list[int]) -> str:
            return ", ".join(str(value) for value in current(key, default))

        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_INCLUDE_EXTERNAL_EVENTS,
                    default=current(
                        CONF_INCLUDE_EXTERNAL_EVENTS,
                        DEFAULT_INCLUDE_EXTERNAL_EVENTS,
                    ),
                ): bool,
                vol.Optional(CONF_LOGO_URL, default=current(CONF_LOGO_URL, "")): str,
                vol.Optional(
                    CONF_PRE_EVENT_TRIGGERS,
                    default=trigger_string(
                        CONF_PRE_EVENT_TRIGGERS, DEFAULT_PRE_EVENT_TRIGGERS
                    ),
                ): str,
                vol.Optional(
                    CONF_PRE_FIRST_EVENT_TRIGGERS,
                    default=trigger_string(CONF_PRE_FIRST_EVENT_TRIGGERS, []),
                ): str,
                vol.Optional(
                    CONF_PRE_LAST_EVENT_END_TRIGGERS,
                    default=trigger_string(CONF_PRE_LAST_EVENT_END_TRIGGERS, []),
                ): str,
                vol.Optional(
                    CONF_POST_LAST_EVENT_TRIGGERS,
                    default=trigger_string(CONF_POST_LAST_EVENT_TRIGGERS, []),
                ): str,
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=current(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                ): vol.All(vol.Coerce(int), vol.Range(min=600, max=86400)),
                vol.Optional(
                    CONF_ENABLED, default=current(CONF_ENABLED, DEFAULT_ENABLED)
                ): bool,
                vol.Optional(
                    CONF_DRY_RUN, default=current(CONF_DRY_RUN, DEFAULT_DRY_RUN)
                ): bool,
            }
        )
        return self.async_show_form(
            step_id="init",
            data_schema=schema,  # type: ignore[arg-type]
            errors=errors,
        )
