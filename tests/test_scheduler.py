"""Tests for the event scheduler."""
import pytest
from datetime import datetime, timedelta

from custom_components.lisa_scheduler.scheduler import (
    EventWindow,
    EventScheduler,
)
from custom_components.lisa_scheduler.models import Event
from custom_components.lisa_scheduler.const import EVENT_TYPE_TRAINING


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
        Event(
            event_type=EVENT_TYPE_TRAINING,
            start_time=now + timedelta(hours=6),
            end_time=now + timedelta(hours=8),
            title="Training 2",
        ),
        Event(
            event_type=EVENT_TYPE_TRAINING,
            start_time=now + timedelta(days=1),
            end_time=now + timedelta(days=1, hours=2),
            title="Training Tomorrow",
        ),
    ]


def test_event_window_creation():
    window_start = datetime(2024, 11, 24, 12, 0)
    event_start = datetime(2024, 11, 24, 14, 0)
    window_end = datetime(2024, 11, 24, 16, 0)

    window = EventWindow(window_start, event_start, window_end)

    assert window.window_start == window_start
    assert window.event_start == event_start
    assert window.window_end == window_end
    assert len(window.events) == 0


def test_event_window_overlaps():
    window1 = EventWindow(
        datetime(2024, 11, 24, 12, 0),
        datetime(2024, 11, 24, 14, 0),
        datetime(2024, 11, 24, 16, 0),
    )
    window2 = EventWindow(
        datetime(2024, 11, 24, 15, 0),
        datetime(2024, 11, 24, 15, 30),
        datetime(2024, 11, 24, 17, 0),
    )
    window3 = EventWindow(
        datetime(2024, 11, 24, 18, 0),
        datetime(2024, 11, 24, 19, 0),
        datetime(2024, 11, 24, 20, 0),
    )

    assert window1.overlaps(window2) is True
    assert window2.overlaps(window1) is True
    assert window1.overlaps(window3) is False
    assert window3.overlaps(window1) is False


def test_event_window_merge():
    event1 = Event(EVENT_TYPE_TRAINING, datetime(2024, 11, 24, 14, 0), datetime(2024, 11, 24, 16, 0), "Event 1")
    event2 = Event(EVENT_TYPE_TRAINING, datetime(2024, 11, 24, 15, 30), datetime(2024, 11, 24, 17, 0), "Event 2")

    window1 = EventWindow(datetime(2024, 11, 24, 12, 0), datetime(2024, 11, 24, 14, 0), datetime(2024, 11, 24, 16, 0), [event1])
    window2 = EventWindow(datetime(2024, 11, 24, 13, 30), datetime(2024, 11, 24, 15, 30), datetime(2024, 11, 24, 17, 0), [event2])

    merged = window1.merge(window2)

    assert merged.window_start == datetime(2024, 11, 24, 12, 0)
    assert merged.event_start == datetime(2024, 11, 24, 14, 0)  # earliest event start
    assert merged.window_end == datetime(2024, 11, 24, 17, 0)
    assert len(merged.events) == 2


def test_event_window_in_window():
    window = EventWindow(
        datetime(2024, 11, 24, 12, 0),
        datetime(2024, 11, 24, 14, 0),
        datetime(2024, 11, 24, 16, 0),
    )

    assert window.in_window(datetime(2024, 11, 24, 13, 0)) is True
    assert window.in_window(datetime(2024, 11, 24, 15, 0)) is True
    assert window.in_window(datetime(2024, 11, 24, 12, 0)) is True
    assert window.in_window(datetime(2024, 11, 24, 16, 0)) is True
    assert window.in_window(datetime(2024, 11, 24, 11, 59)) is False
    assert window.in_window(datetime(2024, 11, 24, 17, 0)) is False


def test_event_window_in_event_period():
    window = EventWindow(
        datetime(2024, 11, 24, 12, 0),
        datetime(2024, 11, 24, 14, 0),
        datetime(2024, 11, 24, 16, 0),
    )

    # During pre-event lead time: not in event period
    assert window.in_event_period(datetime(2024, 11, 24, 13, 0)) is False
    # During actual event: in event period
    assert window.in_event_period(datetime(2024, 11, 24, 15, 0)) is True
    assert window.in_event_period(datetime(2024, 11, 24, 14, 0)) is True
    assert window.in_event_period(datetime(2024, 11, 24, 16, 0)) is True


def test_scheduler_creation():
    scheduler = EventScheduler(pre_event_triggers=[120])
    assert scheduler.pre_event_triggers == [120]
    assert scheduler.pre_event_minutes == 120


def test_scheduler_calculate_event_windows(sample_events):
    scheduler = EventScheduler(pre_event_triggers=[120])
    windows = scheduler.calculate_event_windows(sample_events)

    assert len(windows) > 0
    assert all(isinstance(w, EventWindow) for w in windows)

    first_window = windows[0]
    first_event = sample_events[0]
    expected_window_start = first_event.start_time - timedelta(minutes=120)
    assert abs((first_window.window_start - expected_window_start).total_seconds()) < 60


def test_scheduler_merge_overlapping_windows():
    scheduler = EventScheduler(pre_event_triggers=[120])
    now = datetime.now()
    events = [
        Event(EVENT_TYPE_TRAINING, start_time=now + timedelta(hours=3), end_time=now + timedelta(hours=5), title="Event 1"),
        Event(EVENT_TYPE_TRAINING, start_time=now + timedelta(hours=4), end_time=now + timedelta(hours=6), title="Event 2"),
    ]

    windows = scheduler.calculate_event_windows(events)

    assert len(windows) == 1
    assert len(windows[0].events) == 2


def test_scheduler_is_in_window(sample_events):
    scheduler = EventScheduler(pre_event_triggers=[120])
    windows = scheduler.calculate_event_windows(sample_events)

    far_past = datetime.now() - timedelta(days=1)
    assert scheduler.is_in_window(windows, far_past) is False

    if windows:
        inside_first = windows[0].window_start + timedelta(minutes=30)
        assert scheduler.is_in_window(windows, inside_first) is True


def test_scheduler_is_event_active(sample_events):
    scheduler = EventScheduler(pre_event_triggers=[120])
    windows = scheduler.calculate_event_windows(sample_events)

    if windows:
        # During pre-event lead time: not event active
        pre_event = windows[0].window_start + timedelta(minutes=30)
        assert scheduler.is_event_active(windows, pre_event) is False

        # During actual event: event active
        during_event = windows[0].event_start + timedelta(minutes=30)
        assert scheduler.is_event_active(windows, during_event) is True


def test_scheduler_get_current_window(sample_events):
    scheduler = EventScheduler(pre_event_triggers=[120])
    windows = scheduler.calculate_event_windows(sample_events)

    far_past = datetime.now() - timedelta(days=1)
    assert scheduler.get_current_window(windows, far_past) is None

    if windows:
        inside_first = windows[0].window_start + timedelta(minutes=30)
        current = scheduler.get_current_window(windows, inside_first)
        assert current is not None
        assert current == windows[0]


def test_scheduler_get_next_window(sample_events):
    scheduler = EventScheduler(pre_event_triggers=[120])
    windows = scheduler.calculate_event_windows(sample_events)

    if windows:
        before_all = windows[0].window_start - timedelta(hours=1)
        next_window = scheduler.get_next_window(windows, before_all)
        assert next_window is not None
        assert next_window == windows[0]


def test_scheduler_get_next_state_change(sample_events):
    scheduler = EventScheduler(pre_event_triggers=[120])
    windows = scheduler.calculate_event_windows(sample_events)

    if windows:
        before_all = windows[0].window_start - timedelta(hours=1)
        change_time, will_be_active = scheduler.get_next_state_change(windows, before_all)
        assert change_time is not None
        assert will_be_active is True
        assert change_time == windows[0].window_start

        inside_first = windows[0].window_start + timedelta(minutes=30)
        change_time, will_be_active = scheduler.get_next_state_change(windows, inside_first)
        assert change_time is not None
        assert will_be_active is False
        assert change_time == windows[0].window_end


def test_scheduler_get_schedule_summary(sample_events):
    scheduler = EventScheduler(pre_event_triggers=[120])
    windows = scheduler.calculate_event_windows(sample_events)
    summary = scheduler.get_schedule_summary(windows)

    assert "is_window_active" in summary
    assert "is_event_active" in summary
    assert "current_window" in summary
    assert "next_window" in summary
    assert "total_windows" in summary
    assert "windows_today" in summary
    assert summary["total_windows"] == len(windows)


def test_scheduler_update_settings():
    scheduler = EventScheduler(pre_event_triggers=[120])
    scheduler.update_settings(pre_event_triggers=[90])
    assert scheduler.pre_event_triggers == [90]
    assert scheduler.pre_event_minutes == 90


def test_scheduler_skip_past_events():
    scheduler = EventScheduler(pre_event_triggers=[120])
    now = datetime.now()
    past_event = Event(
        EVENT_TYPE_TRAINING,
        start_time=now - timedelta(hours=5),
        end_time=now - timedelta(hours=3),
        title="Past Event",
    )
    windows = scheduler.calculate_event_windows([past_event])
    assert len(windows) == 0


def test_event_window_to_dict():
    event = Event(EVENT_TYPE_TRAINING, datetime(2024, 11, 24, 14, 0), datetime(2024, 11, 24, 16, 0), "Test Event")
    window = EventWindow(
        datetime(2024, 11, 24, 12, 0),
        datetime(2024, 11, 24, 14, 0),
        datetime(2024, 11, 24, 16, 0),
        [event],
    )
    d = window.to_dict()

    assert "window_start" in d
    assert "event_start" in d
    assert "window_end" in d
    assert "duration_minutes" in d
    assert "pre_event_minutes" in d
    assert d["pre_event_minutes"] == 120
    assert "event_count" in d
    assert d["event_count"] == 1
    assert "events" in d


def test_current_event_ignores_lead_time_and_next_event_skips_running():
    base = datetime(2026, 11, 4, 10, 0)
    first = Event(EVENT_TYPE_TRAINING, base, base + timedelta(hours=1), title="First")
    second = Event(
        EVENT_TYPE_TRAINING,
        base + timedelta(hours=3),
        base + timedelta(hours=4),
        title="Second",
    )
    scheduler = EventScheduler(pre_event_triggers=[120])
    windows = scheduler.calculate_event_windows([first, second], now=base)

    # In the lead time of the first event: nothing running, first is next.
    lead = base - timedelta(minutes=30)
    assert scheduler.get_current_event(windows, lead) is None
    assert scheduler.get_next_event(windows, lead) is first

    # While the first runs: it is current, the second is next.
    during = base + timedelta(minutes=30)
    assert scheduler.get_current_event(windows, during) is first
    assert scheduler.get_next_event(windows, during) is second

    # The end time is exclusive; between events nothing is current.
    gap = base + timedelta(hours=1)
    assert scheduler.get_current_event(windows, gap) is None
    assert scheduler.get_next_event(windows, gap) is second

    # After everything has finished there is neither.
    done = base + timedelta(hours=5)
    assert scheduler.get_current_event(windows, done) is None
    assert scheduler.get_next_event(windows, done) is None
    summary = scheduler.get_schedule_summary(windows, done)
    assert summary["current_event"] is None
    assert summary["next_event"] is None


def test_events_today_counts_every_event_even_when_windows_merge():
    base = datetime(2026, 11, 4, 18, 0)
    events = [
        Event(EVENT_TYPE_TRAINING, base, base + timedelta(hours=1), title="A"),
        Event(EVENT_TYPE_TRAINING, base + timedelta(hours=1), base + timedelta(hours=2), title="B"),
        Event("match", base + timedelta(hours=2), base + timedelta(hours=3), title="C"),
        Event("event", base + timedelta(days=1), base + timedelta(days=1, hours=1), title="Tomorrow"),
    ]
    scheduler = EventScheduler(pre_event_triggers=[30])
    windows = scheduler.calculate_event_windows(events, now=base)

    summary = scheduler.get_schedule_summary(windows, base + timedelta(hours=4))

    assert summary["windows_today"] == 1
    assert summary["events_today"] == 3
    assert summary["events_today_by_type"] == {"training": 2, "match": 1}
    assert [e["title"] for e in summary["events_today_list"]] == ["A", "B", "C"]


def test_get_next_event_index_selects_nth_upcoming_event():
    base = datetime(2026, 11, 4, 10, 0)
    events = [
        Event(EVENT_TYPE_TRAINING, base + timedelta(hours=h), base + timedelta(hours=h, minutes=30), title=f"E{h}")
        for h in (3, 1, 2)
    ]
    scheduler = EventScheduler(pre_event_triggers=[10])
    windows = scheduler.calculate_event_windows(events, now=base)

    assert scheduler.get_next_event(windows, base).title == "E1"
    assert scheduler.get_next_event(windows, base, index=1).title == "E2"
    assert scheduler.get_next_event(windows, base, index=2).title == "E3"
    assert scheduler.get_next_event(windows, base, index=3) is None
    assert scheduler.get_schedule_summary(windows, base, 1)["next_event"]["title"] == "E2"
