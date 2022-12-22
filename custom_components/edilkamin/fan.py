"""Edilkamin integration entity."""
from __future__ import annotations

import edilkamin
from .const import *

from homeassistant.components.fan import (
    FanEntity,
    FanEntityFeature
)

from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from homeassistant.components.bluetooth import async_discovered_service_info
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

    await coordinator.async_request_refresh()
    fan_number = coordinator.data["nvm"]["installer_parameters"]["fans_number"]

    if fan_number == 1 :
        return
    else :  
        entities = [
            EdilkaminFan(coordinator, i, name)
            for i in range(2, fan_number +1)
        ]
        async_add_entities(entities, True)


class EdilkaminFan(CoordinatorEntity, FanEntity):
    """Representation of a stove fan."""

    _attr_supported_features = FanEntityFeature.SET_SPEED | FanEntityFeature.PRESET_MODE
    _attr_preset_modes = ["auto", "none"]
    _attr_speed_count = 5


    def __init__(
        self,
        coordinator,
        fan_index: int,
        name: str,
    ) -> None:
        """
        Create the Edilkamin Fan entity.

        Use:
        - the username/password to login
        - the MAC address that identifies the stove
        """
        super().__init__(coordinator)
        
        self._mac_address = coordinator.get_mac()

        if name : 
            self._attr_name = f"{name} Fan {fan_index}"
        else :
            self._attr_name = f"Stove Fan {fan_index} ({self._mac_address})"
        self._attr_unique_id = f"{self._mac_address}_fan{fan_index}"
        self._device_info = {}
        self._fan_index = fan_index
        self._mqtt_command = f"fan_{self._fan_index}_speed"
        self._device_info = self.coordinator.data

        self._attr_device_info = {
            "identifiers": {("edilkamin", self._mac_address)}
		}

        self._stove_power = 0

        self._attr_extra_state_attributes = {}

    #@callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._device_info = self.coordinator.data

        if not self._device_info :
            return

        speed = self._device_info["nvm"]["user_parameters"][f"fan_{self._fan_index}_ventilation"]  
        if speed == 6 :
            self._attr_preset_mode = "auto"

        else :
            self._attr_preset_mode = "none"
            self._attr_percentage = FAN_SPEED_PERCENTAGE[speed]
        self._attr_extra_state_attributes["actual_speed"] = self._device_info["status"]["fans"][f"fan_{self._fan_index}_speed"]  

        power = edilkamin.device_info_get_power(self._device_info)
        if power == edilkamin.Power.OFF :
            self._attr_is_on = False
        else :
            if self._attr_percentage == 0 :
                self._attr_is_on = False
            else : 
                self._attr_is_on = True

        self.async_write_ha_state()

    def set_percentage(self, percentage: int) -> None:
        """Set the speed percentage of the fan."""
        LOGGER.debug("Setting async percentage: %s", percentage)

        fan_speed = FAN_PERCENTAGE_SPEED[percentage]
        token = self.coordinator.get_token()
        payload = {"name" :"fan_2_speed", "value" : fan_speed}
        edilkamin.mqtt_command(token, self._mac_address, payload)
        self._attr_percentage = percentage

    def set_preset_mode(self, preset_mode: str) -> None:
        """Set the speed percentage of the fan."""
        LOGGER.debug("Setting async fan mode: %s", preset_mode)

        token = self.coordinator.get_token()
        if preset_mode == "auto" :
            payload = {"name" : self._mqtt_command, "value" : 2}
        else :
            fan_speed = FAN_PERCENTAGE_SPEED[self._attr_percentage]
            payload = {"name" : self._mqtt_command, "value" : fan_speed}
        edilkamin.mqtt_command(token, self._mac_address, payload)

        self._attr_preset_mode = preset_mode

    def turn_on(self, speed = None, percentage = None, preset_mode = None, **kwargs) -> None:
        token = self.coordinator.get_token()
        if preset_mode == "auto" or self._attr_preset_mode == "auto" :
            payload = {"name" : self._mqtt_command, "value" : 6}
        else :
            if percentage :
                fan_speed = FAN_PERCENTAGE_SPEED[percentage]
            else :
                fan_speed = FAN_PERCENTAGE_SPEED[self._attr_percentage]
            payload = {"name" : self._mqtt_command, "value" : fan_speed}

        edilkamin.mqtt_command(token, self._mac_address, payload)

    def turn_off(self, **kwargs) -> None:
        """Turn the fan off."""
        
        token = self.coordinator.get_token()
        payload = {"name" : self._mqtt_command, "value" : 0}
        edilkamin.mqtt_command(token, self._mac_address, payload)
        self._attr_percentage = 0