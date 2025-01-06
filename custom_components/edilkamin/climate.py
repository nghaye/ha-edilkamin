"""The edilkamin climate integration."""
from __future__ import annotations

import edilkamin as ek

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
    FAN_AUTO
)

from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import LOGGER, FAN_SPEED_TO_MODE, DOMAIN, FAN_MODES

PRESET_AUTO = "Auto"
PRESET_1 = "Manual P1"
PRESET_2 = "Manual P2"
PRESET_3 = "Manual P3"
PRESET_4 = "Manual P4"
PRESET_5 = "Manual P5"

PRESET_MODES = [PRESET_AUTO, PRESET_1, PRESET_2, PRESET_3, PRESET_4, PRESET_5]
PRESET_MODE_TO_POWER = {
    "Manual P1": 1,
    "Manual P2": 2,
    "Manual P3": 3,
    "Manual P4": 4,
    "Manual P5": 5
}

PREHEAT = "Preheat"
EXTINCTION = "Extinction"
OFF = "Off"
HEATING = "Heating"

OPERATIONAL_PHASE = {
    0: OFF,
    1: PREHEAT,
    2: HEATING,
    3: EXTINCTION,
    4: OFF
}

power_to_hvac = {
    ek.Power.OFF: HVACMode.OFF,
    ek.Power.ON: HVACMode.HEAT,
}
hvac_mode_to_power = {hvac: power for (power, hvac) in power_to_hvac.items()}

fan_mode_to_speed = {
    mode: speed for (speed, mode) in FAN_SPEED_TO_MODE.items()}


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

    _attr_hvac_modes = [HVACMode.HEAT, HVACMode.OFF]
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_supported_features = (ClimateEntityFeature.TARGET_TEMPERATURE |
                                ClimateEntityFeature.FAN_MODE |
                                ClimateEntityFeature.PRESET_MODE)
    _attr_fan_modes = FAN_MODES
    _attr_preset_modes = PRESET_MODES

    # Initial values
    _attr_hvac_mode = HVACMode.OFF
    _attr_preset_mode = PRESET_AUTO
    _attr_current_temperature = 20.0
    _attr_fan_mode = FAN_AUTO

    def __init__(
        self,
        coordinator,
        name: str,
    ) -> None:
        """Create the Edilkamin Climate entity."""
        super().__init__(coordinator)

        self._mac_address = coordinator.get_mac()
        self._attr_name = name
        self._attr_unique_id = self._mac_address + "_stove"
        self._device_info = {}

        self._attr_device_info = {
            "identifiers": {("edilkamin", self._mac_address)}
        }

        self._attr_extra_state_attributes = {}

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._device_info = self.coordinator.data

        if not self._device_info:
            return

        power = ek.device_info_get_power(self._device_info)
        self._attr_hvac_mode = power_to_hvac[power]
        self._attr_target_temperature = \
            ek.device_info_get_target_temperature(self._device_info)
        self._attr_current_temperature = (
            ek.device_info_get_environment_temperature(self._device_info)
        )

        fan_speed = \
            self._device_info["nvm"]["user_parameters"]["fan_1_ventilation"]
        self._attr_fan_mode = FAN_SPEED_TO_MODE[fan_speed]

        actual_power = self._device_info["status"]["state"]["actual_power"]
        self._attr_extra_state_attributes["actual_power"] = actual_power
        if self._device_info["nvm"]["user_parameters"]["is_auto"]:
            self._attr_preset_mode = PRESET_AUTO
        else:
            manual_power = \
                self._device_info["nvm"]["user_parameters"]["manual_power"]
            self._attr_preset_mode = PRESET_MODES[manual_power]

        op_phase = self._device_info["status"]["state"]["operational_phase"]
        self._attr_extra_state_attributes["operational_phase"] = \
            OPERATIONAL_PHASE[op_phase]
        self._attr_extra_state_attributes["fan_actual_speed"] = \
            self._device_info["status"]["fans"]["fan_1_speed"]

        self.async_write_ha_state()

    async def async_set_temperature(self, **kwargs) -> None:
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if not temperature:
            return
        token = self.coordinator.get_token()
        await self.hass.async_add_executor_job(
            ek.set_target_temperature,
            token,
            self._mac_address,
            temperature)
        await self.coordinator.async_refresh()

    async def async_set_hvac_mode(self, hvac_mode) -> None:
        """Set new target hvac mode."""
        LOGGER.debug("Setting async hvac mode: %s", hvac_mode)
        if hvac_mode not in hvac_mode_to_power:
            LOGGER.warning("Unsupported mode: %s", hvac_mode)
            return
        power = hvac_mode_to_power[hvac_mode]
        token = self.coordinator.get_token()

        await self.hass.async_add_executor_job(
            ek.set_power,
            token,
            self._mac_address,
            power)
        await self.coordinator.async_refresh()

    async def async_set_fan_mode(self, fan_mode) -> None:
        """Set new target fan mode."""
        LOGGER.debug("Setting async hvac mode: %s", fan_mode)

        fan_speed = fan_mode_to_speed[fan_mode]
        token = self.coordinator.get_token()
        payload = {"name": "fan_1_speed", "value": fan_speed}

        await self.hass.async_add_executor_job(
            ek.mqtt_command,
            token,
            self._mac_address,
            payload)
        await self.coordinator.async_refresh()

    async def async_set_preset_mode(self, preset_mode) -> None:
        """Set new target preset mode."""
        token = self.coordinator.get_token()
        if preset_mode == PRESET_AUTO:
            payload = {"name": "auto_mode", "value": True}
            await self.hass.async_add_executor_job(
                ek.mqtt_command,
                token,
                self._mac_address,
                payload)
        else:
            payload = {"name": "auto_mode", "value": False}
            await self.hass.async_add_executor_job(
                ek.mqtt_command,
                token,
                self._mac_address,
                payload)
            await self.hass.async_add_executor_job(
                ek.set_manual_power_level,
                token,
                self._mac_address,
                PRESET_MODE_TO_POWER[preset_mode]
            )

        await self.coordinator.async_refresh()
