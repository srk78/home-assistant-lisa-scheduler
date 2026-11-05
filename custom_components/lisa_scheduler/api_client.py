"""Client for the authoritative lisa-schedule-api."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from typing import Any
from urllib.parse import urlsplit, urlunsplit
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import aiohttp

from .const import (
    DEFAULT_TIMEZONE,
    EVENT_TYPE_CLUB_EVENT,
    EVENT_TYPE_MATCH,
    EVENT_TYPE_TRAINING,
)
from .models import Event

API_EVENTS_PATH = "/v1/events"
API_EVENT_TYPES = {
    "game": EVENT_TYPE_MATCH,
    "training": EVENT_TYPE_TRAINING,
    "event": EVENT_TYPE_CLUB_EVENT,
}
REQUEST_TIMEOUT_SECONDS = 15


class ScheduleApiError(Exception):
    """Base exception for API failures."""


class ScheduleApiConnectionError(ScheduleApiError):
    """The API could not be reached."""


class ScheduleApiForbiddenError(ScheduleApiError):
    """The API denied the request."""


class ScheduleApiResponseError(ScheduleApiError):
    """The API returned an unusable response."""


class ScheduleApiTimezoneError(ScheduleApiResponseError):
    """The API timezone is invalid or changed unexpectedly."""


@dataclass(slots=True)
class ScheduleApiMetadata:
    """Health and freshness metadata returned by the API."""

    timezone: str
    generated_at: datetime
    last_attempt_at: datetime | None
    last_successful_sync_at: datetime | None
    error_category: str | None
    stale: bool
    partial: bool
    record_counts: dict[str, int]
    unschedulable_counts: dict[str, int]
    sources: dict[str, Any]
    truncated: bool


@dataclass(slots=True)
class ScheduleFetchResult:
    """A validated API snapshot."""

    events: list[Event]
    metadata: ScheduleApiMetadata
    not_modified: bool = False


def normalize_api_url(value: str) -> str:
    """Normalize a base URL or events URL to the canonical events endpoint."""
    value = value.strip()
    parts = urlsplit(value)
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        raise ValueError("API URL must be an absolute HTTP or HTTPS URL")
    if parts.username is not None or parts.password is not None:
        raise ValueError("API URL must not contain credentials")
    if parts.query or parts.fragment:
        raise ValueError("API URL must not contain a query or fragment")

    path = parts.path.rstrip("/")
    if not path.endswith(API_EVENTS_PATH):
        path = f"{path}{API_EVENTS_PATH}"
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, "", ""))


class LisaScheduleApiClient:
    """Fetch and validate normalized schedule snapshots."""

    def __init__(
        self,
        api_url: str,
        session: aiohttp.ClientSession,
        timezone: str | None,
        include_external_events: bool = False,
    ) -> None:
        self.api_url = normalize_api_url(api_url)
        self._session = session
        self.timezone = timezone
        self.include_external_events = include_external_events
        self._etag: str | None = None
        self._last_result: ScheduleFetchResult | None = None

    async def async_fetch(self, days_ahead: int = 14) -> ScheduleFetchResult:
        """Fetch one schedule snapshot from the API."""
        try:
            schedule_timezone = ZoneInfo(self.timezone or DEFAULT_TIMEZONE)
        except ZoneInfoNotFoundError as err:
            raise ScheduleApiTimezoneError(
                f"Invalid configured timezone: {self.timezone}"
            ) from err

        today = datetime.now(schedule_timezone).date()
        params = self._request_params(today, days_ahead)
        headers = {"Accept": "application/json"}
        if self._etag:
            headers["If-None-Match"] = self._etag

        try:
            async with asyncio.timeout(REQUEST_TIMEOUT_SECONDS):
                async with self._session.get(
                    self.api_url, params=params, headers=headers
                ) as response:
                    if response.status == 304:
                        if self._last_result is None:
                            raise ScheduleApiResponseError(
                                "API returned 304 without a cached snapshot"
                            )
                        return ScheduleFetchResult(
                            events=self._last_result.events,
                            metadata=self._last_result.metadata,
                            not_modified=True,
                        )
                    if response.status == 403:
                        raise ScheduleApiForbiddenError(
                            "API request was forbidden; check ALLOWED_CIDRS"
                        )
                    if 400 <= response.status < 500:
                        raise ScheduleApiResponseError(
                            f"API endpoint returned HTTP {response.status}"
                        )
                    if response.status != 200:
                        raise ScheduleApiConnectionError(
                            f"API returned HTTP {response.status}"
                        )
                    try:
                        payload = await response.json(content_type=None)
                    except (ValueError, aiohttp.ContentTypeError) as err:
                        raise ScheduleApiResponseError(
                            "API response is not valid JSON"
                        ) from err
                    etag = response.headers.get("ETag")
        except ScheduleApiError:
            raise
        except (TimeoutError, aiohttp.ClientError) as err:
            raise ScheduleApiConnectionError(f"Cannot connect to API: {err}") from err

        result = self._parse_response(payload)
        self._etag = etag
        self._last_result = result
        return result

    def _request_params(self, today: date, days_ahead: int) -> dict[str, str]:
        params = {
            "from": today.isoformat(),
            "to": (today + timedelta(days=days_ahead)).isoformat(),
            "cancelled": "false",
        }
        if not self.include_external_events:
            params["atClubVenue"] = "true"
        return params

    def _parse_response(self, payload: Any) -> ScheduleFetchResult:
        if not isinstance(payload, dict):
            raise ScheduleApiResponseError("API response must be an object")
        records = payload.get("data")
        meta = payload.get("meta")
        if not isinstance(records, list) or not isinstance(meta, dict):
            raise ScheduleApiResponseError("API response requires data and meta")

        metadata = self._parse_metadata(meta)
        if self.timezone is not None and metadata.timezone != self.timezone:
            raise ScheduleApiTimezoneError(
                f"API timezone changed from {self.timezone} to {metadata.timezone}"
            )
        if metadata.truncated:
            raise ScheduleApiResponseError("API response is truncated")

        timezone = ZoneInfo(metadata.timezone)
        events = [self._parse_event(record, timezone) for record in records]
        events.sort(key=lambda event: event.start_time)
        return ScheduleFetchResult(events=events, metadata=metadata)

    def _parse_metadata(self, value: dict[str, Any]) -> ScheduleApiMetadata:
        required = {
            "timezone",
            "generatedAt",
            "lastAttemptAt",
            "lastSuccessfulSyncAt",
            "errorCategory",
            "stale",
            "partial",
            "recordCounts",
            "unschedulableCounts",
            "sources",
            "truncated",
        }
        if not required.issubset(value):
            missing = ", ".join(sorted(required - value.keys()))
            raise ScheduleApiResponseError(f"API metadata is missing: {missing}")

        timezone_name = _require_string(value["timezone"], "meta.timezone")
        try:
            ZoneInfo(timezone_name)
        except ZoneInfoNotFoundError as err:
            raise ScheduleApiTimezoneError(
                f"API returned invalid timezone: {timezone_name}"
            ) from err

        return ScheduleApiMetadata(
            timezone=timezone_name,
            generated_at=_parse_aware_datetime(
                value["generatedAt"], "meta.generatedAt"
            ),
            last_attempt_at=_parse_optional_datetime(
                value["lastAttemptAt"], "meta.lastAttemptAt"
            ),
            last_successful_sync_at=_parse_optional_datetime(
                value["lastSuccessfulSyncAt"], "meta.lastSuccessfulSyncAt"
            ),
            error_category=_optional_string(
                value["errorCategory"], "meta.errorCategory"
            ),
            stale=_require_bool(value["stale"], "meta.stale"),
            partial=_require_bool(value["partial"], "meta.partial"),
            record_counts=_require_count_dict(
                value["recordCounts"], "meta.recordCounts"
            ),
            unschedulable_counts=_require_count_dict(
                value["unschedulableCounts"], "meta.unschedulableCounts"
            ),
            sources=_require_dict(value["sources"], "meta.sources"),
            truncated=_require_bool(value["truncated"], "meta.truncated"),
        )

    def _parse_event(self, value: Any, timezone: ZoneInfo) -> Event:
        if not isinstance(value, dict):
            raise ScheduleApiResponseError("Each API event must be an object")
        required = {
            "id",
            "type",
            "localDate",
            "startsAt",
            "endsAt",
            "endTimeEstimated",
            "title",
            "location",
            "cancelled",
            "schedulable",
            "atClubVenue",
            "venueId",
            "sourceRecordId",
        }
        if not required.issubset(value):
            missing = ", ".join(sorted(required - value.keys()))
            raise ScheduleApiResponseError(f"API event is missing: {missing}")

        event_type = value["type"]
        if event_type not in API_EVENT_TYPES:
            raise ScheduleApiResponseError(f"Unsupported event type: {event_type}")
        if _require_bool(value["cancelled"], "event.cancelled"):
            raise ScheduleApiResponseError("API returned a cancelled event")
        if not _require_bool(value["schedulable"], "event.schedulable"):
            raise ScheduleApiResponseError("API returned an unschedulable event")
        at_club_venue = _require_bool(value["atClubVenue"], "event.atClubVenue")
        if not self.include_external_events and not at_club_venue:
            raise ScheduleApiResponseError("API returned an external event")
        try:
            date.fromisoformat(_require_string(value["localDate"], "event.localDate"))
        except ValueError as err:
            raise ScheduleApiResponseError(
                "event.localDate must be an ISO date"
            ) from err

        start = _parse_aware_datetime(value["startsAt"], "event.startsAt")
        end = _parse_aware_datetime(value["endsAt"], "event.endsAt")
        if end <= start:
            raise ScheduleApiResponseError("Event end must be after its start")

        return Event(
            event_type=API_EVENT_TYPES[event_type],
            start_time=start.astimezone(timezone).replace(tzinfo=None),
            end_time=end.astimezone(timezone).replace(tzinfo=None),
            title=_require_string(value["title"], "event.title"),
            location=_optional_string(value["location"], "event.location") or "",
            source_event_id=_require_string(value["id"], "event.id"),
            source_record_id=_require_string(
                value["sourceRecordId"], "event.sourceRecordId"
            ),
            end_time_estimated=_require_bool(
                value["endTimeEstimated"], "event.endTimeEstimated"
            ),
            at_club_venue=at_club_venue,
            venue_id=_optional_string(value["venueId"], "event.venueId"),
            home_logo_url=_optional_string(
                value.get("homeLogoUrl"), "event.homeLogoUrl"
            ),
            away_logo_url=_optional_string(
                value.get("awayLogoUrl"), "event.awayLogoUrl"
            ),
            image_url=_optional_string(value.get("imageUrl"), "event.imageUrl"),
        )


def _parse_aware_datetime(value: Any, field: str) -> datetime:
    if not isinstance(value, str):
        raise ScheduleApiResponseError(f"{field} must be an ISO timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as err:
        raise ScheduleApiResponseError(f"{field} is not a valid timestamp") from err
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ScheduleApiResponseError(f"{field} must include a timezone")
    return parsed.astimezone(UTC)


def _parse_optional_datetime(value: Any, field: str) -> datetime | None:
    return None if value is None else _parse_aware_datetime(value, field)


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise ScheduleApiResponseError(f"{field} must be a non-empty string")
    return value


def _optional_string(value: Any, field: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ScheduleApiResponseError(f"{field} must be a string or null")
    return value


def _require_bool(value: Any, field: str) -> bool:
    if not isinstance(value, bool):
        raise ScheduleApiResponseError(f"{field} must be a boolean")
    return value


def _require_dict(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ScheduleApiResponseError(f"{field} must be an object")
    return value


def _require_count_dict(value: Any, field: str) -> dict[str, int]:
    mapping = _require_dict(value, field)
    if any(
        not isinstance(count, int) or isinstance(count, bool) or count < 0
        for count in mapping.values()
    ):
        raise ScheduleApiResponseError(f"{field} values must be non-negative integers")
    return dict(mapping)
