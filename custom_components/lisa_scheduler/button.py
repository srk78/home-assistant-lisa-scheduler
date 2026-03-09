"""Button platform for LISA Scheduler."""
from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
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
    async_add_entities([LISARefreshButton(coordinator, config_entry)])


class LISARefreshButton(CoordinatorEntity, ButtonEntity):
    """Button that triggers an immediate schedule refresh."""

    def __init__(
        self,
        coordinator: LISASchedulerCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_refresh_schedule"
        self._attr_name = "Refresh Schedule"
        self._attr_has_entity_name = True
        self._attr_icon = "mdi:refresh"
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

    async def async_press(self) -> None:
        """Trigger an immediate schedule refresh."""
        _LOGGER.info("Refresh Schedule button pressed")
        await self.coordinator.async_refresh()
