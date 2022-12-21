"""Edilkamin integration entity."""
from __future__ import annotations

import edilkamin
from .const import *

from homeassistant.components.fan import (
    FanEntity,
    FanEntityFeature
)

from homeassistant.components.bluetooth import async_discovered_service_info
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, CONF_NAME, CONF_MAC
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the stove with config flow."""
    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]
    name = entry.data[CONF_NAME]
    if entry.data[CONF_MAC] :
        mac_addresses = (entry.data[CONF_MAC])
    else :
        ble_devices = tuple(
            {"name": discovery_info.name, "address": discovery_info.address}
            for discovery_info in async_discovered_service_info(hass, False)
        )
        mac_addresses = edilkamin.discover_devices_helper(ble_devices)
    for mac_address in mac_addresses :
        entities = []
        entities.append(EdilkaminFan(username, password, mac_address, 2, name))

    async_add_entities(entities, True)


class EdilkaminFan(FanEntity):
    """Representation of a stove fan."""

    _attr_supported_features = FanEntityFeature.SET_SPEED | FanEntityFeature.PRESET_MODE
    _attr_preset_modes = ["auto", "none"]
    _attr_speed_count = 5


    def __init__(
        self,
        username: str,
        password: str,
        mac_address: str,
        fan_index: int,
        name: str,
    ) -> None:
        """
        Create the Edilkamin Fan entity.

        Use:
        - the username/password to login
        - the MAC address that identifies the stove
        """
        if name : 
            self._attr_name = f"{name} Fan {fan_index}"
        else :
            self._attr_name = f"Stove Fan {fan_index} ({mac_address})"
        self._attr_unique_id = f"{mac_address}_fan{fan_index}"
        self._username = username
        self._password = password
        self._mac_address = mac_address
        self._device_info = None
        self._fan_index = fan_index
        self._mqtt_command = f"fan_{self._fan_index}_speed"

        self._stove_power = 0

        self._attr_extra_state_attributes = {}

    def refresh_token(self) -> str:
        """Login to refresh the token."""
        return edilkamin.sign_in(self._username, self._password)

    def update(self) -> None:
        """Get the latest data and update the relevant Entity attributes."""
        token = self.refresh_token()
        self._device_info = edilkamin.device_info(token, self._mac_address)

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

    def set_percentage(self, percentage: int) -> None:
        """Set the speed percentage of the fan."""
        LOGGER.debug("Setting async percentage: %s", percentage)

        fan_speed = FAN_PERCENTAGE_SPEED[percentage]
        token = self.refresh_token()
        payload = {"name" :"fan_2_speed", "value" : fan_speed}
        edilkamin.mqtt_command(token, self._mac_address, payload)
        self._attr_percentage = percentage

    def set_preset_mode(self, preset_mode: str) -> None:
        """Set the speed percentage of the fan."""
        LOGGER.debug("Setting async fan mode: %s", preset_mode)

        token = self.refresh_token()
        if preset_mode == "auto" :
            payload = {"name" : self._mqtt_command, "value" : 2}
        else :
            fan_speed = FAN_PERCENTAGE_SPEED[self._attr_percentage]
            payload = {"name" : self._mqtt_command, "value" : fan_speed}
        edilkamin.mqtt_command(token, self._mac_address, payload)

        self._attr_preset_mode = preset_mode

    def turn_on(self, speed = None, percentage = None, preset_mode = None, **kwargs) -> None:
        token = self.refresh_token()
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
        
        token = self.refresh_token()
        payload = {"name" : self._mqtt_command, "value" : 0}
        edilkamin.mqtt_command(token, self._mac_address, payload)
        self._attr_percentage = 0