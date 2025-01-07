"""Binary sensor platform for Edilkamin."""
from __future__ import annotations

from .const import DOMAIN

import logging

from homeassistant.components.binary_sensor import (
#    BinarySensorDeviceClass,
    BinarySensorEntity,
)

from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the stove with config flow."""
    name = entry.data[CONF_NAME]
    coordinator = hass.data[DOMAIN]["coordinator"]

    async_add_entities(
        [
            PelletReserve(coordinator, name)
        ],
        update_before_add=False,
    )


class PelletReserve(CoordinatorEntity, BinarySensorEntity):
    """Pellet in Reserve Binary sensor entity"""

    def __init__(
        self,
        coordinator,
        name: str,
    ) -> None:
        """Create the Edilkamin Pellet in Reserve binary sensor entity."""
        super().__init__(coordinator)

        self._mac_address = coordinator.get_mac()

        self._attr_name = f"{name} Pellet in Reserve"
        self._attr_unique_id = f"{self._mac_address}_pelletinreserve"
        self._attr_icon = "mdi:storage-tank"

        # Initial value
        self._attr_is_on = (
            self.coordinator.data["status"]["flags"]["is_pellet_in_reserve"]
        )

        self._attr_device_info = {
            "identifiers": {("edilkamin", self._mac_address)}
        }

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_is_on = (
            self.coordinator.data["status"]["flags"]["is_pellet_in_reserve"]
        )
        self.async_write_ha_state()