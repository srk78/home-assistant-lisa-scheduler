"""Sensor platform for ZHC Heating Scheduler."""
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
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ZHCHeatingCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up ZHC Heating Scheduler sensors."""
    coordinator: ZHCHeatingCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    sensors = [
        ZHCNextHeatingStartSensor(coordinator, config_entry),
        ZHCNextHeatingStopSensor(coordinator, config_entry),
        ZHCCurrentEventSensor(coordinator, config_entry),
        ZHCEventsTodaySensor(coordinator, config_entry),
        ZHCHeatingMinutesTodaySensor(coordinator, config_entry),
        ZHCTotalWindowsSensor(coordinator, config_entry),
        ZHCLastUpdateSensor(coordinator, config_entry),
    ]

    async_add_entities(sensors)


class ZHCSchedulerSensorBase(CoordinatorEntity, SensorEntity):
    """Base class for ZHC Heating Scheduler sensors."""

    def __init__(
        self,
        coordinator: ZHCHeatingCoordinator,
        config_entry: ConfigEntry,
        sensor_type: str,
        name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{config_entry.entry_id}_{sensor_type}"
        self._attr_name = f"ZHC {name}"
        self._attr_has_entity_name = True


class ZHCNextHeatingStartSensor(ZHCSchedulerSensorBase):
    """Sensor for next heating start time."""

    def __init__(
        self, coordinator: ZHCHeatingCoordinator, config_entry: ConfigEntry
    ) -> None:
        """Initialize the sensor."""
        super().__init__(
            coordinator, config_entry, "next_heating_start", "Next Heating Start"
        )
        self._attr_device_class = SensorDeviceClass.TIMESTAMP
        self._attr_icon = "mdi:clock-start"

    @property
    def native_value(self) -> datetime | None:
        """Return the next heating start time."""
        if not self.coordinator.data:
            return None

        summary = self.coordinator.data.get("summary", {})
        
        # If currently heating, return the start time of current window
        if summary.get("is_heating"):
            current_window = summary.get("current_window")
            if current_window:
                return datetime.fromisoformat(current_window["start_time"])
        
        # Otherwise return next window start
        next_window = summary.get("next_window")
        if next_window:
            return datetime.fromisoformat(next_window["start_time"])

        return None

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes."""
        if not self.coordinator.data:
            return {}

        summary = self.coordinator.data.get("summary", {})
        next_window = summary.get("next_window")

        if next_window:
            return {
                "event_count": next_window.get("event_count", 0),
                "duration_minutes": next_window.get("duration_minutes", 0),
            }

        return {}


class ZHCNextHeatingStopSensor(ZHCSchedulerSensorBase):
    """Sensor for next heating stop time."""

    def __init__(
        self, coordinator: ZHCHeatingCoordinator, config_entry: ConfigEntry
    ) -> None:
        """Initialize the sensor."""
        super().__init__(
            coordinator, config_entry, "next_heating_stop", "Next Heating Stop"
        )
        self._attr_device_class = SensorDeviceClass.TIMESTAMP
        self._attr_icon = "mdi:clock-end"

    @property
    def native_value(self) -> datetime | None:
        """Return the next heating stop time."""
        if not self.coordinator.data:
            return None

        summary = self.coordinator.data.get("summary", {})
        
        # If currently heating, return current window end time
        if summary.get("is_heating"):
            current_window = summary.get("current_window")
            if current_window:
                return datetime.fromisoformat(current_window["end_time"])

        # Otherwise return next window end
        next_window = summary.get("next_window")
        if next_window:
            return datetime.fromisoformat(next_window["end_time"])

        return None


class ZHCCurrentEventSensor(ZHCSchedulerSensorBase):
    """Sensor for current or next event details."""

    def __init__(
        self, coordinator: ZHCHeatingCoordinator, config_entry: ConfigEntry
    ) -> None:
        """Initialize the sensor."""
        super().__init__(
            coordinator, config_entry, "current_event", "Current Event"
        )
        self._attr_icon = "mdi:calendar"

    @property
    def native_value(self) -> str:
        """Return the current or next event name."""
        if not self.coordinator.data:
            return "No events"

        summary = self.coordinator.data.get("summary", {})
        
        # Get current or next window
        window = summary.get("current_window") or summary.get("next_window")
        
        if window and window.get("events"):
            events = window["events"]
            if events:
                first_event = events[0]
                return first_event.get("title", "Unknown event")

        return "No upcoming events"

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes."""
        if not self.coordinator.data:
            return {}

        summary = self.coordinator.data.get("summary", {})
        window = summary.get("current_window") or summary.get("next_window")

        if window and window.get("events"):
            events = window["events"]
            return {
                "event_count": len(events),
                "events": [
                    {
                        "title": e.get("title", ""),
                        "type": e.get("event_type", ""),
                        "start_time": e.get("start_time", ""),
                        "end_time": e.get("end_time", ""),
                    }
                    for e in events
                ],
                "window_start": window.get("start_time"),
                "window_end": window.get("end_time"),
            }

        return {}


class ZHCEventsTodaySensor(ZHCSchedulerSensorBase):
    """Sensor for number of events today."""

    def __init__(
        self, coordinator: ZHCHeatingCoordinator, config_entry: ConfigEntry
    ) -> None:
        """Initialize the sensor."""
        super().__init__(
            coordinator, config_entry, "events_today", "Events Today"
        )
        self._attr_icon = "mdi:calendar-today"
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> int:
        """Return the number of heating windows today."""
        if not self.coordinator.data:
            return 0

        summary = self.coordinator.data.get("summary", {})
        return summary.get("windows_today", 0)


class ZHCHeatingMinutesTodaySensor(ZHCSchedulerSensorBase):
    """Sensor for total heating minutes today."""

    def __init__(
        self, coordinator: ZHCHeatingCoordinator, config_entry: ConfigEntry
    ) -> None:
        """Initialize the sensor."""
        super().__init__(
            coordinator, config_entry, "heating_minutes_today", "Heating Minutes Today"
        )
        self._attr_icon = "mdi:timer"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = "min"

    @property
    def native_value(self) -> int:
        """Return the total heating minutes today."""
        if not self.coordinator.data:
            return 0

        summary = self.coordinator.data.get("summary", {})
        return summary.get("total_heating_minutes_today", 0)


class ZHCTotalWindowsSensor(ZHCSchedulerSensorBase):
    """Sensor for total number of heating windows."""

    def __init__(
        self, coordinator: ZHCHeatingCoordinator, config_entry: ConfigEntry
    ) -> None:
        """Initialize the sensor."""
        super().__init__(
            coordinator, config_entry, "total_windows", "Total Heating Windows"
        )
        self._attr_icon = "mdi:window-open"
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> int:
        """Return the total number of heating windows."""
        if not self.coordinator.data:
            return 0

        summary = self.coordinator.data.get("summary", {})
        return summary.get("total_windows", 0)

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes."""
        if not self.coordinator.data:
            return {}

        return {
            "heating_windows": self.coordinator.data.get("heating_windows", []),
        }


class ZHCLastUpdateSensor(ZHCSchedulerSensorBase):
    """Sensor for last schedule update time."""

    def __init__(
        self, coordinator: ZHCHeatingCoordinator, config_entry: ConfigEntry
    ) -> None:
        """Initialize the sensor."""
        super().__init__(
            coordinator, config_entry, "last_update", "Last Schedule Update"
        )
        self._attr_device_class = SensorDeviceClass.TIMESTAMP
        self._attr_icon = "mdi:update"

    @property
    def native_value(self) -> datetime | None:
        """Return the last update time."""
        if not self.coordinator.data:
            return None

        last_update = self.coordinator.data.get("last_schedule_update")
        if last_update:
            return datetime.fromisoformat(last_update)

        return None

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes."""
        if not self.coordinator.data:
            return {}

        return {
            "last_error": self.coordinator.data.get("last_error"),
            "event_count": len(self.coordinator.data.get("events", [])),
        }

