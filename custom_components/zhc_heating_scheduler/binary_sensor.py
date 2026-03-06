"""Binary sensor platform for ZHC Scheduler."""
from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
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
    coordinator: ZHCHeatingCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([
        ZHCWindowActiveSensor(coordinator, config_entry),
        ZHCEventActiveSensor(coordinator, config_entry),
        ZHCSchedulerEnabledSensor(coordinator, config_entry),
        ZHCManualOverrideSensor(coordinator, config_entry),
    ])


class ZHCBinarySensorBase(CoordinatorEntity, BinarySensorEntity):
    def __init__(
        self,
        coordinator: ZHCHeatingCoordinator,
        config_entry: ConfigEntry,
        sensor_type: str,
        name: str,
    ) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{config_entry.entry_id}_{sensor_type}"
        self._attr_name = f"ZHC {name}"
        self._attr_has_entity_name = True


class ZHCWindowActiveSensor(ZHCBinarySensorBase):
    """True while the pre-event window is active (lead time + event duration)."""

    def __init__(self, coordinator: ZHCHeatingCoordinator, config_entry: ConfigEntry) -> None:
        super().__init__(coordinator, config_entry, "window_active", "Window Active")
        self._attr_icon = "mdi:calendar-clock"

    @property
    def is_on(self) -> bool:
        if not self.coordinator.data:
            return False
        return self.coordinator.data.get("is_window_active", False)

    @property
    def extra_state_attributes(self) -> dict:
        if not self.coordinator.data:
            return {}
        summary = self.coordinator.data.get("summary", {})
        attributes = {
            "next_state_change": summary.get("next_state_change"),
            "next_state_active": summary.get("next_state_active", False),
        }
        if self.is_on:
            current = summary.get("current_window")
            if current:
                attributes["window_end"] = current.get("window_end")
                attributes["event_start"] = current.get("event_start")
                attributes["event_count"] = current.get("event_count", 0)
        return attributes


class ZHCEventActiveSensor(ZHCBinarySensorBase):
    """True only during the actual event time (not the pre-event lead time)."""

    def __init__(self, coordinator: ZHCHeatingCoordinator, config_entry: ConfigEntry) -> None:
        super().__init__(coordinator, config_entry, "event_active", "Event Active")
        self._attr_icon = "mdi:calendar-check"

    @property
    def is_on(self) -> bool:
        if not self.coordinator.data:
            return False
        return self.coordinator.data.get("is_event_active", False)

    @property
    def extra_state_attributes(self) -> dict:
        if not self.coordinator.data:
            return {}
        summary = self.coordinator.data.get("summary", {})
        current = summary.get("current_window")
        if current and self.is_on:
            return {
                "window_end": current.get("window_end"),
                "event_count": current.get("event_count", 0),
                "events": [
                    {
                        "title": e.get("title", ""),
                        "type": e.get("event_type", ""),
                        "start_time": e.get("start_time", ""),
                        "end_time": e.get("end_time", ""),
                    }
                    for e in current.get("events", [])
                ],
            }
        return {}


class ZHCSchedulerEnabledSensor(ZHCBinarySensorBase):
    def __init__(self, coordinator: ZHCHeatingCoordinator, config_entry: ConfigEntry) -> None:
        super().__init__(coordinator, config_entry, "scheduler_enabled", "Scheduler Enabled")
        self._attr_icon = "mdi:power"

    @property
    def is_on(self) -> bool:
        if not self.coordinator.data:
            return False
        return self.coordinator.data.get("enabled", False)


class ZHCManualOverrideSensor(ZHCBinarySensorBase):
    def __init__(self, coordinator: ZHCHeatingCoordinator, config_entry: ConfigEntry) -> None:
        super().__init__(coordinator, config_entry, "manual_override", "Manual Override Active")
        self._attr_icon = "mdi:hand-back-right"

    @property
    def is_on(self) -> bool:
        if not self.coordinator.data:
            return False
        return self.coordinator.data.get("manual_override", False)

    @property
    def extra_state_attributes(self) -> dict:
        if not self.coordinator.data or not self.is_on:
            return {}
        if self.coordinator.manual_override:
            start, end = self.coordinator.manual_override
            return {
                "override_start": start.isoformat(),
                "override_end": end.isoformat(),
            }
        return {}
