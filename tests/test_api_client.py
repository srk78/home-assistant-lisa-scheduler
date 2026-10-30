"""Tests for the lisa-schedule-api client."""

from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock

import aiohttp
import pytest

from custom_components.lisa_scheduler.api_client import (
    LisaScheduleApiClient,
    ScheduleApiConnectionError,
    ScheduleApiForbiddenError,
    ScheduleApiResponseError,
    ScheduleApiTimezoneError,
    normalize_api_url,
)
from custom_components.lisa_scheduler.const import EVENT_TYPE_MATCH


def _metadata(**overrides):
    value = {
        "timezone": "Europe/Amsterdam",
        "generatedAt": "2026-10-30T09:00:00Z",
        "lastAttemptAt": "2026-10-30T08:55:00Z",
        "lastSuccessfulSyncAt": "2026-10-30T08:55:00Z",
        "errorCategory": None,
        "stale": False,
        "partial": False,
        "recordCounts": {"games": 1, "trainings": 0},
        "unschedulableCounts": {"games": 0, "trainings": 0},
        "sources": {"games": {"stale": False}},
        "truncated": False,
    }
    value.update(overrides)
    return value


def _event(**overrides):
    value = {
        "id": "event_1",
        "type": "game",
        "localDate": "2026-10-30",
        "startsAt": "2026-10-30T09:00:00Z",
        "endsAt": "2026-10-30T10:20:00Z",
        "endTimeEstimated": True,
        "title": "ZHC H1 - Opponent H1",
        "location": None,
        "cancelled": False,
        "schedulable": True,
        "atClubVenue": True,
        "venueId": "duintjesveld",
        "sourceRecordId": "game_1",
    }
    value.update(overrides)
    return value


def _payload(events=None, meta=None):
    return {
        "data": [_event()] if events is None else events,
        "meta": _metadata() if meta is None else meta,
    }


class _Response:
    def __init__(self, status=200, payload=None, headers=None):
        self.status = status
        self._payload = payload
        self.headers = headers or {}

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return False

    async def json(self, content_type=None):
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload


def _client(*, include_external=False, timezone="Europe/Amsterdam"):
    session = MagicMock()
    return (
        LisaScheduleApiClient(
            "http://schedule.local",
            session,
            timezone,
            include_external_events=include_external,
        ),
        session,
    )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("https://schedule.example.com", "https://schedule.example.com/v1/events"),
        (
            "https://schedule.example.com/v1/events/",
            "https://schedule.example.com/v1/events",
        ),
        (
            "http://HOST.local/prefix",
            "http://host.local/prefix/v1/events",
        ),
    ],
)
def test_normalize_api_url(value, expected):
    assert normalize_api_url(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        "ftp://schedule.example.com",
        "https://user:secret@schedule.example.com",
        "https://schedule.example.com?token=secret",
    ],
)
def test_normalize_api_url_rejects_unsafe_values(value):
    with pytest.raises(ValueError):
        normalize_api_url(value)


@pytest.mark.asyncio
async def test_fetch_maps_event_and_sends_club_filter():
    client, session = _client()
    session.get.return_value = _Response(
        payload=_payload(), headers={"ETag": '"snapshot-1"'}
    )
    result = await client.async_fetch(days_ahead=14)

    _, kwargs = session.get.call_args
    params = kwargs["params"]
    assert params["cancelled"] == "false"
    assert params["atClubVenue"] == "true"
    assert (
        date.fromisoformat(params["to"]) - date.fromisoformat(params["from"])
    ).days == 14
    event = result.events[0]
    assert event.event_type == EVENT_TYPE_MATCH
    assert event.start_time.isoformat() == "2026-10-30T10:00:00"
    assert event.location == ""
    assert event.source_event_id == "event_1"
    assert event.source_record_id == "game_1"
    assert event.end_time_estimated is True


@pytest.mark.asyncio
async def test_fetch_can_include_external_events():
    client, session = _client(include_external=True)
    session.get.return_value = _Response(
        payload=_payload([_event(atClubVenue=False, venueId=None)])
    )
    result = await client.async_fetch()

    assert "atClubVenue" not in session.get.call_args.kwargs["params"]
    assert result.events[0].at_club_venue is False


@pytest.mark.asyncio
async def test_fetch_accepts_empty_schedule():
    client, session = _client()
    session.get.return_value = _Response(payload=_payload(events=[]))

    result = await client.async_fetch()

    assert result.events == []


@pytest.mark.asyncio
async def test_fetch_uses_etag_and_handles_not_modified():
    client, session = _client()
    session.get.side_effect = [
        _Response(payload=_payload(), headers={"ETag": '"snapshot-1"'}),
        _Response(status=304),
    ]

    first = await client.async_fetch()
    second = await client.async_fetch()

    assert second.not_modified is True
    assert second.events == first.events
    assert session.get.call_args.kwargs["headers"]["If-None-Match"] == '"snapshot-1"'


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("response", "error"),
    [
        (_Response(status=403), ScheduleApiForbiddenError),
        (_Response(status=404), ScheduleApiResponseError),
        (_Response(status=500), ScheduleApiConnectionError),
        (_Response(payload=[]), ScheduleApiResponseError),
        (
            _Response(payload=_payload(meta=_metadata(truncated=True))),
            ScheduleApiResponseError,
        ),
        (
            _Response(payload=_payload([_event(schedulable=False)])),
            ScheduleApiResponseError,
        ),
        (
            _Response(payload=_payload([_event(endsAt="2026-10-30T08:00:00Z")])),
            ScheduleApiResponseError,
        ),
        (
            _Response(payload=_payload(meta=_metadata(timezone="UTC"))),
            ScheduleApiTimezoneError,
        ),
    ],
)
async def test_fetch_rejects_unusable_responses(response, error):
    client, session = _client()
    session.get.return_value = response

    with pytest.raises(error):
        await client.async_fetch()


@pytest.mark.asyncio
async def test_fetch_wraps_connection_errors():
    client, session = _client()
    session.get.side_effect = aiohttp.ClientConnectionError("offline")

    with pytest.raises(ScheduleApiConnectionError, match="offline"):
        await client.async_fetch()


@pytest.mark.asyncio
async def test_dst_timestamp_is_converted_to_schedule_local_time():
    client, session = _client()
    session.get.return_value = _Response(
        payload=_payload(
            [
                _event(
                    localDate="2026-03-29",
                    startsAt="2026-03-29T01:30:00Z",
                    endsAt="2026-03-29T02:30:00Z",
                )
            ]
        )
    )

    result = await client.async_fetch()

    assert result.events[0].start_time.isoformat() == "2026-03-29T03:30:00"
    assert result.events[0].end_time.isoformat() == "2026-03-29T04:30:00"
