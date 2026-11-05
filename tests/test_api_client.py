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
from custom_components.lisa_scheduler.const import (
    EVENT_TYPE_CLUB_EVENT,
    EVENT_TYPE_MATCH,
    EVENT_TYPE_TRAINING,
)


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
async def test_fetch_maps_every_api_event_type():
    client, session = _client()
    session.get.return_value = _Response(
        payload=_payload(
            [
                _event(id="event_1", type="game"),
                _event(
                    id="event_2",
                    type="training",
                    startsAt="2026-10-30T11:00:00Z",
                    endsAt="2026-10-30T12:00:00Z",
                ),
                _event(
                    id="event_3",
                    type="event",
                    title="Eten op de club",
                    location="Sportpark Duintjesveld",
                    startsAt="2026-10-30T15:00:00Z",
                    endsAt="2026-10-30T19:00:00Z",
                    endTimeEstimated=False,
                    url="https://club.example/event-detail/abc",
                    description="Samen eten.",
                ),
            ]
        )
    )

    result = await client.async_fetch()

    assert [event.event_type for event in result.events] == [
        EVENT_TYPE_MATCH,
        EVENT_TYPE_TRAINING,
        EVENT_TYPE_CLUB_EVENT,
    ]
    club_event = result.events[2]
    assert club_event.title == "Eten op de club"
    assert club_event.location == "Sportpark Duintjesveld"
    assert club_event.end_time_estimated is False


@pytest.mark.asyncio
async def test_fetch_maps_logo_and_image_urls():
    client, session = _client()
    session.get.return_value = _Response(
        payload=_payload(
            [
                _event(
                    id="game",
                    type="game",
                    homeLogoUrl="https://images.example/home.png",
                    awayLogoUrl="https://images.example/away.png",
                    imageUrl=None,
                ),
                _event(
                    id="club",
                    type="event",
                    startsAt="2026-10-30T11:00:00Z",
                    endsAt="2026-10-30T12:00:00Z",
                    homeLogoUrl=None,
                    awayLogoUrl=None,
                    imageUrl="https://storage.example/EventLogo/1.png",
                ),
                # Older API versions do not send the fields at all.
                _event(
                    id="old",
                    type="training",
                    startsAt="2026-10-30T13:00:00Z",
                    endsAt="2026-10-30T14:00:00Z",
                ),
            ]
        )
    )

    game, club, old = (await client.async_fetch()).events

    assert game.home_logo_url == "https://images.example/home.png"
    assert game.away_logo_url == "https://images.example/away.png"
    assert game.image_url is None
    assert club.image_url == "https://storage.example/EventLogo/1.png"
    assert club.home_logo_url is None
    assert (old.home_logo_url, old.away_logo_url, old.image_url) == (None, None, None)
    assert game.to_dict()["home_logo_url"] == "https://images.example/home.png"


@pytest.mark.asyncio
async def test_fetch_rejects_non_string_logo_url():
    client, session = _client()
    session.get.return_value = _Response(
        payload=_payload([_event(homeLogoUrl=123)])
    )

    with pytest.raises(ScheduleApiResponseError):
        await client.async_fetch()


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
            _Response(payload=_payload([_event(type="tournament")])),
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
