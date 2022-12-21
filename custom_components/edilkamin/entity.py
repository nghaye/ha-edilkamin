"""Edilkamin integration entity."""
import logging

import edilkamin
from .const import *

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.const import ATTR_TEMPERATURE, TEMP_CELSIUS

_LOGGER = logging.getLogger(__name__)

power_to_hvac = {
    edilkamin.Power.OFF: HVACMode.OFF,
    edilkamin.Power.ON: HVACMode.AUTO,
}
hvac_mode_to_power = {hvac: power for (power, hvac) in power_to_hvac.items()}

fan_mode_to_speed = {mode: speed for (speed, mode) in FAN_SPEED_TO_MODE.items()}


class EdilkaminEntity(ClimateEntity):
    """Representation of a stove."""

    _attr_hvac_modes = [HVACMode.HEAT, HVACMode.OFF, HVACMode.AUTO]
    _attr_temperature_unit = TEMP_CELSIUS
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.FAN_MODE | ClimateEntityFeature.PRESET_MODE
    _attr_fan_modes = FAN_MODES
    _attr_preset_modes = PRESET_MODES

    def __init__(
        self,
        username: str,
        password: str,
        mac_address: str,
        name: str,
    ) -> None:
        """
        Create the Edilkamin entity.

        Use:
        - the username/password to login
        - the MAC address that identifies the stove
        """
        if name :
            self._attr_name = name
        else :
            self._attr_name = f"Stove ({mac_address})"
        self._attr_unique_id = mac_address + "_stove"
        self._username = username
        self._password = password
        self._mac_address = mac_address
        self._device_info = None

        self._attr_extra_state_attributes = {}

    def refresh_token(self) -> str:
        """Login to refresh the token."""
        return edilkamin.sign_in(self._username, self._password)

    def update(self) -> None:
        """Get the latest data and update the relevant Entity attributes."""
        try :
            token = self.refresh_token()
            self._device_info = edilkamin.device_info(token, self._mac_address)
        except:
            _LOGGER.error("Unable to update edilkamin device")
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

        self._attr_extra_state_attributes["relax_mode"] = self._device_info["nvm"]["user_parameters"]["is_relax_active"]
        op_phase = self._device_info["status"]["state"]["operational_phase"]
        self._attr_extra_state_attributes["operational_phase"] = OPERATIONAL_PHASE[op_phase]
        self._attr_extra_state_attributes["fan_actual_speed"] = self._device_info["status"]["fans"][f"fan_1_speed"] 
        #self._attr_hvac_action = OPERATIONNAL_PHASE[op_phase]

        #self._attr_preset_mode = PRESET_AUTO


    def set_temperature(self, **kwargs) -> None:
        """Set new target temperature."""
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is None:
            return
        token = self.refresh_token()
        edilkamin.set_target_temperature(token, self._mac_address, temperature)

    def set_hvac_mode(self, hvac_mode):
        """Set new target hvac mode."""
        _LOGGER.debug("Setting async hvac mode: %s", hvac_mode)
        if hvac_mode not in hvac_mode_to_power:
            _LOGGER.warning("Unsupported mode: %s", hvac_mode)
            return
        power = hvac_mode_to_power[hvac_mode]
        token = self.refresh_token()
        edilkamin.set_power(token, self._mac_address, power)

    def set_fan_mode(self, fan_mode):
        """Set new target fan mode."""
        _LOGGER.debug("Setting async hvac mode: %s", fan_mode)

        fan_speed = fan_mode_to_speed[fan_mode]
        token = self.refresh_token()
        payload = {"name" :"fan_1_speed", "value" : fan_speed}
        edilkamin.mqtt_command(token, self._mac_address, payload)

    def set_preset_mode(self, preset_mode):
        """Set new target preset mode."""
        return