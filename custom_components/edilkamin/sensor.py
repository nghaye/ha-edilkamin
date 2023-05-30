"""Edilkamin sensors entities."""

from __future__ import annotations

from .const import DOMAIN

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)

from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from datetime import datetime

# TODO : find other alarm codes
ALARMSTATE = {
    0: "None",
    1: "Unknown code 1",
    2: "Unknown code 2",
    3: "Pellet End",
    4: "Failed Ignition",
    21: "Power Outage"
}


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
            LastAlarm(coordinator, name)
        ],
        update_before_add=False,
    )


class PowerOnsNumber(CoordinatorEntity, SensorEntity):
    """Number of power ons sensor entity"""

    def __init__(
        self,
        coordinator,
        name: str,
    ) -> None:
        """Create the Edilkamin power ons sensor entity."""
        super().__init__(coordinator)

        self._mac_address = coordinator.get_mac()

        self._attr_name = f"{name} Power Ons"
        self._attr_unique_id = f"{self._mac_address}_powerons"
        self._attr_icon = "mdi:counter"

        # Initial value
        self._attr_native_value = (
            self.coordinator.data["nvm"]["total_counters"]["power_ons"]
        )

        self._attr_device_info = {
            "identifiers": {("edilkamin", self._mac_address)}
        }

        self._attr_state_class = SensorStateClass.MEASUREMENT

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = (
            self.coordinator.data["nvm"]["total_counters"]["power_ons"]
        )
        self.async_write_ha_state()


class WorkingTime(CoordinatorEntity, SensorEntity):
    """Working time hours for each power level sensor entity"""

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
        self._counter = f"p{self._power}_working_time"

        self._attr_name = f"{name} Working Time P{power}"
        self._attr_unique_id = f"{self._mac_address}_workingtime_p{power}"

        self._attr_device_class = SensorDeviceClass.DURATION
        self._attr_state_class = SensorStateClass.MEASUREMENT

        self._attr_device_info = {
            "identifiers": {("edilkamin", self._mac_address)}
        }

        # Initial value
        self._attr_native_value = (
            self.coordinator.data["nvm"]["total_counters"][self._counter]
        )
        self._attr_native_unit_of_measurement = "h"

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = (
            self.coordinator.data["nvm"]["total_counters"][self._counter]
        )
        self.async_write_ha_state()


class AlarmState(CoordinatorEntity, SensorEntity):
    """Current alarm sensor entity"""

    def __init__(
        self,
        coordinator,
        name: str,
    ) -> None:
        """Create the Edilkamin alarm state sensor entity."""
        super().__init__(coordinator)

        self._mac_address = coordinator.get_mac()

        self._attr_name = f"{name} Alarm State"
        self._attr_unique_id = f"{self._mac_address}_alarmstate"
        self._attr_icon = "mdi:bell-alert"

        self._attr_device_info = {
            "identifiers": {("edilkamin", self._mac_address)}
        }

        #self._attr_state_class = SensorStateClass.MEASUREMENT

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        state = self.coordinator.data["status"]["state"]["alarm_type"]
        if state in ALARMSTATE:
            self._attr_native_value = ALARMSTATE[state]
        else:
            self._attr_native_value = state
        self.async_write_ha_state()


class LastAlarm(CoordinatorEntity, SensorEntity):
    """Last alarm sensor entity"""

    def __init__(
        self,
        coordinator,
        name: str,
    ) -> None:
        """Create the Edilkamin alarm state sensor entity."""
        super().__init__(coordinator)

        self._mac_address = coordinator.get_mac()

        self._attr_name = f"{name} Last Alarm"
        self._attr_unique_id = f"{self._mac_address}_lastalarm"
        self._attr_icon = "mdi:alert"

        self._attr_device_info = {
            "identifiers": {("edilkamin", self._mac_address)}
        }

        #self._attr_state_class = SensorStateClass.MEASUREMENT

        self._attr_extra_state_attributes = {}

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        i = self.coordinator.data["nvm"]["alarms_log"]["index"]

        # No alarm recorded
        if self.coordinator.data["nvm"]["alarms_log"]["number"] == 0:
            return

        last_alarm = self.coordinator.data["nvm"]["alarms_log"]["alarms"][i-1]
        if last_alarm["type"] in ALARMSTATE:
            self._attr_native_value = ALARMSTATE[last_alarm["type"]]
        else:
            # Error code unknown, shows only the code
            self._attr_native_value = last_alarm["type"]

        self._attr_extra_state_attributes["Alarm Code"] = last_alarm["type"]
        self._attr_extra_state_attributes["Date"] = datetime.fromtimestamp(
            last_alarm["timestamp"])
        self.async_write_ha_state()
