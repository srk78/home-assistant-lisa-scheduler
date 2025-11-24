"""Binary sensor platform for ZHC Heating Scheduler."""
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
    """Set up ZHC Heating Scheduler binary sensors."""
    coordinator: ZHCHeatingCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    sensors = [
        ZHCHeatingActiveSensor(coordinator, config_entry),
        ZHCSchedulerEnabledSensor(coordinator, config_entry),
        ZHCManualOverrideSensor(coordinator, config_entry),
    ]

    async_add_entities(sensors)


class ZHCBinarySensorBase(CoordinatorEntity, BinarySensorEntity):
    """Base class for ZHC Heating Scheduler binary sensors."""

    def __init__(
        self,
        coordinator: ZHCHeatingCoordinator,
        config_entry: ConfigEntry,
        sensor_type: str,
        name: str,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{config_entry.entry_id}_{sensor_type}"
        self._attr_name = f"ZHC {name}"
        self._attr_has_entity_name = True


class ZHCHeatingActiveSensor(ZHCBinarySensorBase):
    """Binary sensor indicating if heating should be active."""

    def __init__(
        self, coordinator: ZHCHeatingCoordinator, config_entry: ConfigEntry
    ) -> None:
        """Initialize the sensor."""
        super().__init__(
            coordinator, config_entry, "heating_active", "Heating Active"
        )
        self._attr_device_class = BinarySensorDeviceClass.HEAT
        self._attr_icon = "mdi:radiator"

    @property
    def is_on(self) -> bool:
        """Return true if heating should be active."""
        if not self.coordinator.data:
            return False

        return self.coordinator.data.get("is_heating", False)

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes."""
        if not self.coordinator.data:
            return {}

        summary = self.coordinator.data.get("summary", {})
        
        attributes = {
            "next_state_change": summary.get("next_state_change"),
            "next_state_heating": summary.get("next_state_heating", False),
        }

        # Add current window info if heating
        if self.is_on:
            current_window = summary.get("current_window")
            if current_window:
                attributes["current_window_end"] = current_window.get("end_time")
                attributes["current_window_events"] = current_window.get("event_count", 0)

        return attributes


class ZHCSchedulerEnabledSensor(ZHCBinarySensorBase):
    """Binary sensor indicating if the scheduler is enabled."""

    def __init__(
        self, coordinator: ZHCHeatingCoordinator, config_entry: ConfigEntry
    ) -> None:
        """Initialize the sensor."""
        super().__init__(
            coordinator, config_entry, "scheduler_enabled", "Scheduler Enabled"
        )
        self._attr_icon = "mdi:power"

    @property
    def is_on(self) -> bool:
        """Return true if scheduler is enabled."""
        if not self.coordinator.data:
            return False

        return self.coordinator.data.get("enabled", False)


class ZHCManualOverrideSensor(ZHCBinarySensorBase):
    """Binary sensor indicating if manual override is active."""

    def __init__(
        self, coordinator: ZHCHeatingCoordinator, config_entry: ConfigEntry
    ) -> None:
        """Initialize the sensor."""
        super().__init__(
            coordinator, config_entry, "manual_override", "Manual Override Active"
        )
        self._attr_icon = "mdi:hand-back-right"

    @property
    def is_on(self) -> bool:
        """Return true if manual override is active."""
        if not self.coordinator.data:
            return False

        return self.coordinator.data.get("manual_override", False)

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes."""
        if not self.coordinator.data or not self.is_on:
            return {}

        if self.coordinator.manual_override:
            start, end = self.coordinator.manual_override
            return {
                "override_start": start.isoformat(),
                "override_end": end.isoformat(),
            }

        return {}

