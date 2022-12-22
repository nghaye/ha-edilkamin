"""Edilkamin sensors entity."""

from __future__ import annotations

import edilkamin
from .const import *

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)

from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from homeassistant.components.bluetooth import async_discovered_service_info
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

ALARMSTATE = {
    0: "None",
    1: "Unknown code 1",
    2: "Unknown code 2",
    3: "Pellet End",
    4: "Failed Ignition"
}

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
            PowerOnsNumber(coordinator, name),
            WorkingTime(coordinator, name, 1),
            WorkingTime(coordinator, name, 2),
            WorkingTime(coordinator, name, 3),
            WorkingTime(coordinator, name, 4),
            WorkingTime(coordinator, name, 5),
            AlarmState(coordinator, name),
        ],
        update_before_add=False,
    )

class PowerOnsNumber(CoordinatorEntity, SensorEntity):
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
            self._attr_name = f"{name} Power Ons"
        else :
            self._attr_name = f"Stove Power Ons"
        self._attr_unique_id = f"{self._mac_address}_powerons"
        
        # Initial value
        self._attr_native_value = self.coordinator.data["nvm"]["total_counters"]["power_ons"]

        self._attr_device_info = {
            "identifiers": {("edilkamin", self._mac_address)}
		}

        #self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_state_class = SensorStateClass.MEASUREMENT

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.data["nvm"]["total_counters"]["power_ons"]

class WorkingTime(CoordinatorEntity, SensorEntity):
    """Number of power ons"""

    def __init__(
        self,
        coordinator,
        name: str,
        power,
    ) -> None:
        """Create the Edilkamin working time sensor entity."""
        super().__init__(coordinator)
        
        self._mac_address = coordinator.get_mac()
        self._power = power

        if name : 
            self._attr_name = f"{name} Working Time P{power}"
        else :
            self._attr_name = f"Stove  Working Time P{power}"
        self._attr_unique_id = f"{self._mac_address}_workingtime_p{power}"

        self._attr_device_class = SensorDeviceClass.DURATION
        self._attr_state_class = SensorStateClass.MEASUREMENT

        self._attr_device_info = {
            "identifiers": {("edilkamin", self._mac_address)}
		}
        
        # Initial value
        self._attr_native_value = self.coordinator.data["nvm"]["total_counters"][f"p{self._power}_working_time"]
        self._attr_native_unit_of_measurement = "h"


    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.data["nvm"]["total_counters"][f"p{self._power}_working_time"]


class AlarmState(CoordinatorEntity, SensorEntity):
    """Number of power ons"""

    def __init__(
        self,
        coordinator,
        name: str,
    ) -> None:
        """Create the Edilkamin alarm state sensor entity."""
        super().__init__(coordinator)
        
        self._mac_address = coordinator.get_mac()

        if name : 
            self._attr_name = f"{name} Alarm State"
        else :
            self._attr_name = f"Stove Alarm State"
        self._attr_unique_id = f"{self._mac_address}_alarmstate"
        
        # Initial value
        state = self.coordinator.data["status"]["state"]["alarm_type"]
        self._attr_native_value = ALARMSTATE[state]

        self._attr_device_info = {
            "identifiers": {("edilkamin", self._mac_address)}
		}

        #self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_state_class = SensorStateClass.MEASUREMENT

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        state = self.coordinator.data["status"]["state"]["alarm_type"]
        self._attr_native_value = ALARMSTATE[state]