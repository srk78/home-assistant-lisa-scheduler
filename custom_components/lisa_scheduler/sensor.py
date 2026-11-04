"""Sensor platform for LISA Scheduler."""

from __future__ import annotations

import logging
from datetime import datetime

from homeassistant.util import dt as dt_util
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import LISASchedulerCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: LISASchedulerCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        [
            LISANextWindowStartSensor(coordinator, config_entry),
            LISANextWindowEndSensor(coordinator, config_entry),
            LISANextEventStartSensor(coordinator, config_entry),
            LISACurrentEventSensor(coordinator, config_entry),
            LISANextEventSensor(coordinator, config_entry),
            LISAEventsTodaySensor(coordinator, config_entry),
            LISAWindowMinutesTodaySensor(coordinator, config_entry),
            LISATotalWindowsSensor(coordinator, config_entry),
            LISALastUpdateSensor(coordinator, config_entry),
        ]
    )


class LISASchedulerSensorBase(
    CoordinatorEntity[LISASchedulerCoordinator], SensorEntity
):
    def __init__(
        self,
        coordinator: LISASchedulerCoordinator,
        config_entry: ConfigEntry,
        sensor_type: str,
        name: str,
    ) -> None:
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_{sensor_type}"
        self._attr_name = name
        self._attr_has_entity_name = True
        self._attr_entity_picture = coordinator.logo_url or None

    @property
    def device_info(self) -> DeviceInfo:
        info = DeviceInfo(
            identifiers={(DOMAIN, self._config_entry.entry_id)},
            name="LISA Scheduler",
            manufacturer="LISA",
            model="Event Scheduler",
        )
        if self.coordinator.logo_url:
            info["configuration_url"] = self.coordinator.logo_url
        return info

    def _timestamp_value(self, value: str) -> datetime:
        """Return an HA-local aware timestamp from a schedule-local ISO value."""
        return dt_util.as_local(self.coordinator.localize_schedule_datetime(value))


class LISANextWindowStartSensor(LISASchedulerSensorBase):
    """Timestamp when the next (or current) pre-event window starts."""

    def __init__(
        self, coordinator: LISASchedulerCoordinator, config_entry: ConfigEntry
    ) -> None:
        super().__init__(
            coordinator, config_entry, "next_window_start", "Next Window Start"
        )
        self._attr_device_class = SensorDeviceClass.TIMESTAMP
        self._attr_icon = "mdi:clock-start"

    @property
    def native_value(self) -> datetime | None:
        if not self.coordinator.data:
            return None
        summary = self.coordinator.data.get("summary", {})
        if summary.get("is_window_active"):
            current = summary.get("current_window")
            if current:
                return self._timestamp_value(current["window_start"])
        next_w = summary.get("next_window")
        if next_w:
            return self._timestamp_value(next_w["window_start"])
        return None

    @property
    def extra_state_attributes(self) -> dict:
        if not self.coordinator.data:
            return {}
        summary = self.coordinator.data.get("summary", {})
        window = summary.get("current_window") or summary.get("next_window")
        if window:
            return {
                "event_count": window.get("event_count", 0),
                "pre_event_minutes": window.get("pre_event_minutes", 0),
            }
        return {}


class LISANextWindowEndSensor(LISASchedulerSensorBase):
    """Timestamp when the next (or current) window ends."""

    def __init__(
        self, coordinator: LISASchedulerCoordinator, config_entry: ConfigEntry
    ) -> None:
        super().__init__(
            coordinator, config_entry, "next_window_end", "Next Window End"
        )
        self._attr_device_class = SensorDeviceClass.TIMESTAMP
        self._attr_icon = "mdi:clock-end"

    @property
    def native_value(self) -> datetime | None:
        if not self.coordinator.data:
            return None
        summary = self.coordinator.data.get("summary", {})
        if summary.get("is_window_active"):
            current = summary.get("current_window")
            if current:
                return self._timestamp_value(current["window_end"])
        next_w = summary.get("next_window")
        if next_w:
            return self._timestamp_value(next_w["window_end"])
        return None


class LISANextEventStartSensor(LISASchedulerSensorBase):
    """Timestamp when the next actual event starts."""

    def __init__(
        self, coordinator: LISASchedulerCoordinator, config_entry: ConfigEntry
    ) -> None:
        super().__init__(
            coordinator, config_entry, "next_event_start", "Next Event Start"
        )
        self._attr_device_class = SensorDeviceClass.TIMESTAMP
        self._attr_icon = "mdi:calendar-arrow-right"

    @property
    def native_value(self) -> datetime | None:
        if not self.coordinator.data:
            return None
        summary = self.coordinator.data.get("summary", {})
        window = summary.get("current_window") or summary.get("next_window")
        if window:
            return self._timestamp_value(window["event_start"])
        return None


def _event_attributes(event: dict | None) -> dict:
    if not event:
        return {}
    return {
        "title": event.get("title", ""),
        "type": event.get("event_type", ""),
        "start_time": event.get("start_time", ""),
        "end_time": event.get("end_time", ""),
        "location": event.get("location", ""),
    }


class LISACurrentEventSensor(LISASchedulerSensorBase):
    """Name of the event in progress, or None."""

    def __init__(
        self, coordinator: LISASchedulerCoordinator, config_entry: ConfigEntry
    ) -> None:
        super().__init__(coordinator, config_entry, "current_event", "Current Event")
        self._attr_icon = "mdi:calendar"

    def _event(self) -> dict | None:
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("summary", {}).get("current_event")

    @property
    def native_value(self) -> str:
        event = self._event()
        return (event.get("title") or "Unknown event") if event else "None"

    @property
    def extra_state_attributes(self) -> dict:
        return _event_attributes(self._event())


class LISANextEventSensor(LISASchedulerSensorBase):
    """Name of an upcoming event (the first by default, see next_event_index)."""

    def __init__(
        self, coordinator: LISASchedulerCoordinator, config_entry: ConfigEntry
    ) -> None:
        super().__init__(coordinator, config_entry, "next_event", "Next Event")
        self._attr_icon = "mdi:calendar-arrow-right"

    def _event(self) -> dict | None:
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("summary", {}).get("next_event")

    @property
    def native_value(self) -> str:
        event = self._event()
        return (event.get("title") or "Unknown event") if event else "None"

    @property
    def extra_state_attributes(self) -> dict:
        index = (self.coordinator.data or {}).get("next_event_index", 0)
        return {"event_index": index, **_event_attributes(self._event())}


class LISAEventsTodaySensor(LISASchedulerSensorBase):
    """Number of events (matches, trainings and club events) today."""

    def __init__(
        self, coordinator: LISASchedulerCoordinator, config_entry: ConfigEntry
    ) -> None:
        super().__init__(coordinator, config_entry, "events_today", "Events Today")
        self._attr_icon = "mdi:calendar-today"
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> int:
        if not self.coordinator.data:
            return 0
        return self.coordinator.data.get("summary", {}).get("events_today", 0)

    @property
    def extra_state_attributes(self) -> dict:
        if not self.coordinator.data:
            return {}
        summary = self.coordinator.data.get("summary", {})
        by_type = summary.get("events_today_by_type", {})
        return {
            "matches": by_type.get("match", 0),
            "trainings": by_type.get("training", 0),
            "club_events": by_type.get("event", 0),
            "windows": summary.get("windows_today", 0),
            "events": [
                {
                    "title": e.get("title", ""),
                    "type": e.get("event_type", ""),
                    "start_time": e.get("start_time", ""),
                    "end_time": e.get("end_time", ""),
                }
                for e in summary.get("events_today_list", [])
            ],
        }


class LISAWindowMinutesTodaySensor(LISASchedulerSensorBase):
    """Total minutes inside event windows today."""

    def __init__(
        self, coordinator: LISASchedulerCoordinator, config_entry: ConfigEntry
    ) -> None:
        super().__init__(
            coordinator, config_entry, "window_minutes_today", "Window Minutes Today"
        )
        self._attr_icon = "mdi:timer"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = "min"

    @property
    def native_value(self) -> int:
        if not self.coordinator.data:
            return 0
        return self.coordinator.data.get("summary", {}).get(
            "total_window_minutes_today", 0
        )


class LISATotalWindowsSensor(LISASchedulerSensorBase):
    """Total number of upcoming event windows."""

    def __init__(
        self, coordinator: LISASchedulerCoordinator, config_entry: ConfigEntry
    ) -> None:
        super().__init__(
            coordinator, config_entry, "total_windows", "Total Event Windows"
        )
        self._attr_icon = "mdi:calendar-multiselect"
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> int:
        if not self.coordinator.data:
            return 0
        return self.coordinator.data.get("summary", {}).get("total_windows", 0)

    @property
    def extra_state_attributes(self) -> dict:
        if not self.coordinator.data:
            return {}
        return {"event_windows": self.coordinator.data.get("event_windows", [])}


class LISALastUpdateSensor(LISASchedulerSensorBase):
    """Timestamp of the last schedule fetch."""

    def __init__(
        self, coordinator: LISASchedulerCoordinator, config_entry: ConfigEntry
    ) -> None:
        super().__init__(
            coordinator, config_entry, "last_update", "Last Schedule Update"
        )
        self._attr_device_class = SensorDeviceClass.TIMESTAMP
        self._attr_icon = "mdi:update"

    @property
    def native_value(self) -> datetime | None:
        if not self.coordinator.data:
            return None
        last_update = self.coordinator.data.get("last_schedule_update")
        if last_update:
            return self._timestamp_value(last_update)
        return None

    @property
    def extra_state_attributes(self) -> dict:
        if not self.coordinator.data:
            return {}
        events = self.coordinator.data.get("events", [])
        windows = self.coordinator.data.get("event_windows", [])
        return {
            "api_url": self.coordinator.data.get("api_url"),
            "include_external_events": self.coordinator.data.get(
                "include_external_events"
            ),
            "api_events": events,
            "api_event_count": len(events),
            "scraped_events": events,
            "scraped_event_count": len(events),
            "event_windows": windows,
            "event_window_count": len(windows),
            "last_error": self.coordinator.data.get("last_error"),
            "last_refresh_attempt": self.coordinator.data.get("last_refresh_attempt"),
            "last_api_fetch_success": self.coordinator.data.get(
                "last_api_fetch_success"
            ),
            "last_refresh_failed": self.coordinator.data.get("last_refresh_failed"),
            "schedule_stale": self.coordinator.data.get("schedule_stale"),
            "timezone": self.coordinator.data.get("timezone"),
            "api_generated_at": self.coordinator.data.get("api_generated_at"),
            "upstream_last_attempt": self.coordinator.data.get("upstream_last_attempt"),
            "upstream_error_category": self.coordinator.data.get(
                "upstream_error_category"
            ),
            "upstream_stale": self.coordinator.data.get("upstream_stale"),
            "upstream_partial": self.coordinator.data.get("upstream_partial"),
            "upstream_record_counts": self.coordinator.data.get(
                "upstream_record_counts", {}
            ),
            "upstream_unschedulable_counts": self.coordinator.data.get(
                "upstream_unschedulable_counts", {}
            ),
            "upstream_sources": self.coordinator.data.get("upstream_sources", {}),
        }
