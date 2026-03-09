"""Sensor platform for LISA Scheduler."""
from __future__ import annotations

import logging
from datetime import datetime

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
    async_add_entities([
        LISANextWindowStartSensor(coordinator, config_entry),
        LISANextWindowEndSensor(coordinator, config_entry),
        LISANextEventStartSensor(coordinator, config_entry),
        LISACurrentEventSensor(coordinator, config_entry),
        LISAEventsTodaySensor(coordinator, config_entry),
        LISAWindowMinutesTodaySensor(coordinator, config_entry),
        LISATotalWindowsSensor(coordinator, config_entry),
        LISALastUpdateSensor(coordinator, config_entry),
    ])


class LISASchedulerSensorBase(CoordinatorEntity, SensorEntity):
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


class LISANextWindowStartSensor(LISASchedulerSensorBase):
    """Timestamp when the next (or current) pre-event window starts."""

    def __init__(self, coordinator: LISASchedulerCoordinator, config_entry: ConfigEntry) -> None:
        super().__init__(coordinator, config_entry, "next_window_start", "Next Window Start")
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
                return datetime.fromisoformat(current["window_start"])
        next_w = summary.get("next_window")
        if next_w:
            return datetime.fromisoformat(next_w["window_start"])
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

    def __init__(self, coordinator: LISASchedulerCoordinator, config_entry: ConfigEntry) -> None:
        super().__init__(coordinator, config_entry, "next_window_end", "Next Window End")
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
                return datetime.fromisoformat(current["window_end"])
        next_w = summary.get("next_window")
        if next_w:
            return datetime.fromisoformat(next_w["window_end"])
        return None


class LISANextEventStartSensor(LISASchedulerSensorBase):
    """Timestamp when the next actual event starts."""

    def __init__(self, coordinator: LISASchedulerCoordinator, config_entry: ConfigEntry) -> None:
        super().__init__(coordinator, config_entry, "next_event_start", "Next Event Start")
        self._attr_device_class = SensorDeviceClass.TIMESTAMP
        self._attr_icon = "mdi:calendar-arrow-right"

    @property
    def native_value(self) -> datetime | None:
        if not self.coordinator.data:
            return None
        summary = self.coordinator.data.get("summary", {})
        window = summary.get("current_window") or summary.get("next_window")
        if window:
            return datetime.fromisoformat(window["event_start"])
        return None


class LISACurrentEventSensor(LISASchedulerSensorBase):
    """Name of the current or next event."""

    def __init__(self, coordinator: LISASchedulerCoordinator, config_entry: ConfigEntry) -> None:
        super().__init__(coordinator, config_entry, "current_event", "Current Event")
        self._attr_icon = "mdi:calendar"

    @property
    def native_value(self) -> str:
        if not self.coordinator.data:
            return "No events"
        summary = self.coordinator.data.get("summary", {})
        window = summary.get("current_window") or summary.get("next_window")
        if window and window.get("events"):
            first = window["events"][0]
            return first.get("title", "Unknown event")
        return "No upcoming events"

    @property
    def extra_state_attributes(self) -> dict:
        if not self.coordinator.data:
            return {}
        summary = self.coordinator.data.get("summary", {})
        window = summary.get("current_window") or summary.get("next_window")
        if window and window.get("events"):
            return {
                "event_count": len(window["events"]),
                "events": [
                    {
                        "title": e.get("title", ""),
                        "type": e.get("event_type", ""),
                        "start_time": e.get("start_time", ""),
                        "end_time": e.get("end_time", ""),
                    }
                    for e in window["events"]
                ],
                "window_start": window.get("window_start"),
                "event_start": window.get("event_start"),
                "window_end": window.get("window_end"),
            }
        return {}


class LISAEventsTodaySensor(LISASchedulerSensorBase):
    """Number of event windows today."""

    def __init__(self, coordinator: LISASchedulerCoordinator, config_entry: ConfigEntry) -> None:
        super().__init__(coordinator, config_entry, "events_today", "Events Today")
        self._attr_icon = "mdi:calendar-today"
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> int:
        if not self.coordinator.data:
            return 0
        return self.coordinator.data.get("summary", {}).get("windows_today", 0)


class LISAWindowMinutesTodaySensor(LISASchedulerSensorBase):
    """Total minutes inside event windows today."""

    def __init__(self, coordinator: LISASchedulerCoordinator, config_entry: ConfigEntry) -> None:
        super().__init__(coordinator, config_entry, "window_minutes_today", "Window Minutes Today")
        self._attr_icon = "mdi:timer"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = "min"

    @property
    def native_value(self) -> int:
        if not self.coordinator.data:
            return 0
        return self.coordinator.data.get("summary", {}).get("total_window_minutes_today", 0)


class LISATotalWindowsSensor(LISASchedulerSensorBase):
    """Total number of upcoming event windows."""

    def __init__(self, coordinator: LISASchedulerCoordinator, config_entry: ConfigEntry) -> None:
        super().__init__(coordinator, config_entry, "total_windows", "Total Event Windows")
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

    def __init__(self, coordinator: LISASchedulerCoordinator, config_entry: ConfigEntry) -> None:
        super().__init__(coordinator, config_entry, "last_update", "Last Schedule Update")
        self._attr_device_class = SensorDeviceClass.TIMESTAMP
        self._attr_icon = "mdi:update"

    @property
    def native_value(self) -> datetime | None:
        if not self.coordinator.data:
            return None
        last_update = self.coordinator.data.get("last_schedule_update")
        if last_update:
            return datetime.fromisoformat(last_update)
        return None

    @property
    def extra_state_attributes(self) -> dict:
        if not self.coordinator.data:
            return {}
        events = self.coordinator.data.get("events", [])
        windows = self.coordinator.data.get("event_windows", [])
        return {
            "scraped_events": events,
            "scraped_event_count": len(events),
            "event_windows": windows,
            "event_window_count": len(windows),
            "last_error": self.coordinator.data.get("last_error"),
        }

    @property
    def extra_state_attributes(self) -> dict:
        if not self.coordinator.data:
            return {}
        return {
            "last_error": self.coordinator.data.get("last_error"),
            "event_count": len(self.coordinator.data.get("events", [])),
        }
