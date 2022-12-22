"""Edilkamin sensors entity."""

from __future__ import annotations

import edilkamin
from .const import *

from homeassistant.components.switch import (
    SwitchEntity,
)

from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback


_LOGGER = logging.getLogger(__name__)

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
            RelaxSwitch(coordinator, name),
        ],
        update_before_add=False,
    )

class RelaxSwitch(CoordinatorEntity, SwitchEntity):
    """Number of power ons"""

    def __init__(
        self,
        coordinator,
        name: str,
    ) -> None:
        """Create the Edilkamin power ons sensor entity."""
        super().__init__(coordinator)
        
        self._mac_address = coordinator.get_mac()

        if name : 
            self._attr_name = f"{name} Relax Mode"
        else :
            self._attr_name = f"Stove Relax Mode"
        self._attr_unique_id = f"{self._mac_address}_relaxmode"
        
        # Initial value
        relax_mode = edilkamin.device_info_get_relax_mode(self.coordinator.data)
        if relax_mode :
            self._attr_state = "on"
        else :
            self._attr_state = "off"

        self._attr_device_info = {
            "identifiers": {("edilkamin", self._mac_address)}
		}

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        relax_mode = edilkamin.device_info_get_relax_mode(self.coordinator.data)
        if relax_mode :
            self._attr_state = "on"
        else :
            self._attr_state = "off"

    def turn_on(self, **kwargs) -> None:
        """Turn the entity on."""
        edilkamin.set_relax_mode(self.coordinator.get_token(), self._mac_address, True)
        self._attr_state = "on"

    def turn_off(self, **kwargs) -> None:
        """Turn the entity off."""
        edilkamin.set_relax_mode(self.coordinator.get_token(), self._mac_address, False)
        self._attr_state = "off"