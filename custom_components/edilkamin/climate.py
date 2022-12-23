"""The edilkamin integration."""
from __future__ import annotations

import edilkamin

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, ATTR_TEMPERATURE, TEMP_CELSIUS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)

from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import *

power_to_hvac = {
    edilkamin.Power.OFF: HVACMode.OFF,
    edilkamin.Power.ON: HVACMode.AUTO,
}
hvac_mode_to_power = {hvac: power for (power, hvac) in power_to_hvac.items()}

fan_mode_to_speed = {mode: speed for (speed, mode) in FAN_SPEED_TO_MODE.items()}

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the stove with config flow."""

    name = entry.data[CONF_NAME]
    coordinator = hass.data[DOMAIN]["coordinator"]

    async_add_entities([EdilkaminClimate(coordinator, name)], True)

class EdilkaminClimate(CoordinatorEntity, ClimateEntity):
    """Representation of a stove."""

    _attr_hvac_modes = [HVACMode.HEAT, HVACMode.OFF, HVACMode.AUTO]
    _attr_temperature_unit = TEMP_CELSIUS
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.FAN_MODE | ClimateEntityFeature.PRESET_MODE
    _attr_fan_modes = FAN_MODES
    _attr_preset_modes = PRESET_MODES

    def __init__(
        self,
        coordinator,
        name: str,
    ) -> None:
        """
        Create the Edilkamin entity.

        Use:
        - the username/password to login
        - the MAC address that identifies the stove
        """
        super().__init__(coordinator)

        self._mac_address = coordinator.get_mac()
        if name :
            self._attr_name = name
        else :
            self._attr_name = f"Stove ({self._mac_address})"
        self._attr_unique_id = self._mac_address + "_stove"
        self._device_info = {}

        # Initial Values
        self._device_info = self.coordinator.data   

        power = edilkamin.device_info_get_power(self._device_info)
        self._attr_hvac_mode = power_to_hvac[power]
        self._attr_target_temperature = edilkamin.device_info_get_target_temperature(
            self._device_info
        )
        self._attr_current_temperature = (
            edilkamin.device_info_get_environment_temperature(self._device_info)
        )

        fan_speed =  self._device_info["nvm"]["user_parameters"]["fan_1_ventilation"]       
        self._attr_fan_mode = FAN_SPEED_TO_MODE[fan_speed]

        actual_power = self._device_info["status"]["state"]["actual_power"]
        self._attr_preset_mode = PRESET_MODES[actual_power - 1]

        self._attr_device_info = {
            "identifiers": {("edilkamin", self._mac_address)}
		}

        self._attr_extra_state_attributes = {}

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._device_info = self.coordinator.data

        if not self._device_info :
            return

        power = edilkamin.device_info_get_power(self._device_info)
        self._attr_hvac_mode = power_to_hvac[power]
        self._attr_target_temperature = edilkamin.device_info_get_target_temperature(
            self._device_info
        )
        self._attr_current_temperature = (
            edilkamin.device_info_get_environment_temperature(self._device_info)
        )

        fan_speed =  self._device_info["nvm"]["user_parameters"]["fan_1_ventilation"]       
        self._attr_fan_mode = FAN_SPEED_TO_MODE[fan_speed]

        actual_power = self._device_info["status"]["state"]["actual_power"]
        self._attr_extra_state_attributes["actual_power"] = actual_power
        self._attr_preset_mode = PRESET_MODES[actual_power - 1]

        #self._attr_extra_state_attributes["relax_mode"] = self._device_info["nvm"]["user_parameters"]["is_relax_active"]
        op_phase = self._device_info["status"]["state"]["operational_phase"]
        self._attr_extra_state_attributes["operational_phase"] = OPERATIONAL_PHASE[op_phase]
        self._attr_extra_state_attributes["fan_actual_speed"] = self._device_info["status"]["fans"]["fan_1_speed"] 

        self.async_write_ha_state()


    def set_temperature(self, **kwargs) -> None:
        """Set new target temperature."""
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is None:
            return
        token = self.coordinator.get_token()
        edilkamin.set_target_temperature(token, self._mac_address, temperature)

    def set_hvac_mode(self, hvac_mode):
        """Set new target hvac mode."""
        LOGGER.debug("Setting async hvac mode: %s", hvac_mode)
        if hvac_mode not in hvac_mode_to_power:
            LOGGER.warning("Unsupported mode: %s", hvac_mode)
            return
        power = hvac_mode_to_power[hvac_mode]
        token = self.coordinator.get_token()
        edilkamin.set_power(token, self._mac_address, power)

    def set_fan_mode(self, fan_mode):
        """Set new target fan mode."""
        LOGGER.debug("Setting async hvac mode: %s", fan_mode)

        fan_speed = fan_mode_to_speed[fan_mode]
        token = self.coordinator.get_token()
        payload = {"name" :"fan_1_speed", "value" : fan_speed}
        edilkamin.mqtt_command(token, self._mac_address, payload)

    def set_preset_mode(self, preset_mode):
        """Set new target preset mode."""
        token = self.coordinator.get_token()
        #edilkamin.set_power(token, self._mac_address, power)
        return