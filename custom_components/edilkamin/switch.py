"""Edilkamin switch entities."""

from __future__ import annotations

import edilkamin
from .const import DOMAIN

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


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the stove switche with config flow."""
    name = entry.data[CONF_NAME]
    coordinator = hass.data[DOMAIN]["coordinator"]

    async_add_entities(
        [
            RelaxSwitch(coordinator, name),
            StandbySwitch(coordinator, name),
            ChronoSwitch(coordinator, name),
            AirkareSwitch(coordinator, name)
        ],
        update_before_add=False,
    )


class RelaxSwitch(CoordinatorEntity, SwitchEntity):
    """Relax Mode switch entity"""

    def __init__(
        self,
        coordinator,
        name: str,
    ) -> None:
        """Create the Edilkamin power ons sensor entity."""
        super().__init__(coordinator)

        self._mac_address = coordinator.get_mac()

        self._attr_name = f"{name} Relax Mode"
        self._attr_unique_id = f"{self._mac_address}_relaxmode"
        self._attr_icon = "mdi:volume-off"

        self._attr_device_info = {
            "identifiers": {("edilkamin", self._mac_address)}
        }

    @property
    def is_on(self) -> bool:
        """Return if relax mode is on."""
        return edilkamin.device_info_get_relax_mode(self.coordinator.data)

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the entity on."""
        token = self.coordinator.get_token()
        await self.hass.async_add_executor_job(
            edilkamin.set_relax_mode,
            token,
            self._mac_address,
            True)
        await self.coordinator.async_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the entity off."""
        token = self.coordinator.get_token()
        await self.hass.async_add_executor_job(
            edilkamin.set_relax_mode,
            token,
            self._mac_address,
            False)
        await self.coordinator.async_refresh()


class StandbySwitch(CoordinatorEntity, SwitchEntity):
    """Standby Mode Entity"""

    def __init__(
        self,
        coordinator,
        name: str,
    ) -> None:
        """Create the Edilkamin power ons sensor entity."""
        super().__init__(coordinator)

        self._mac_address = coordinator.get_mac()

        self._attr_name = f"{name} Standby Mode"
        self._attr_unique_id = f"{self._mac_address}_standbymode"
        self._attr_icon = "mdi:pause-circle-outline"

        self._attr_device_info = {
            "identifiers": {("edilkamin", self._mac_address)}
        }

    @property
    def is_on(self) -> bool:
        """Return if standby mode is on."""
        return edilkamin.device_info_get_standby_mode(self.coordinator.data)

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the entity on."""
        token = self.coordinator.get_token()
        await self.hass.async_add_executor_job(
            edilkamin.set_standby_mode,
            token,
            self._mac_address,
            True)
        await self.coordinator.async_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the entity off."""
        token = self.coordinator.get_token()
        await self.hass.async_add_executor_job(
            edilkamin.set_standby_mode,
            token,
            self._mac_address,
            False)
        await self.coordinator.async_refresh()


class ChronoSwitch(CoordinatorEntity, SwitchEntity):
    """Chrono Mode Entity"""

    def __init__(
        self,
        coordinator,
        name: str,
    ) -> None:
        """Create the Edilkamin chrono switch."""
        super().__init__(coordinator)

        self._mac_address = coordinator.get_mac()

        self._attr_name = f"{name} Chrono Mode"
        self._attr_unique_id = f"{self._mac_address}_chronomode"
        self._attr_icon = "mdi:update"

        self._attr_device_info = {
            "identifiers": {("edilkamin", self._mac_address)}
        }

    @property
    def is_on(self) -> bool:
        """Return if standby mode is on."""
        return self.coordinator.data["status"]["flags"]["is_crono_active"]

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the entity on."""
        token = self.coordinator.get_token()
        payload = {"name": "chrono_mode", "value": True}
        await self.hass.async_add_executor_job(
            edilkamin.mqtt_command,
            token,
            self._mac_address,
            payload)
        await self.coordinator.async_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the entity off."""
        token = self.coordinator.get_token()
        payload = {"name": "chrono_mode", "value": False}
        await self.hass.async_add_executor_job(
            edilkamin.mqtt_command,
            token,
            self._mac_address,
            payload)
        await self.coordinator.async_refresh()


class AirkareSwitch(CoordinatorEntity, SwitchEntity):
    """Airkare Mode Entity"""

    def __init__(
        self,
        coordinator,
        name: str,
    ) -> None:
        """Create the Edilkamin airkare switch."""
        super().__init__(coordinator)

        self._mac_address = coordinator.get_mac()

        self._attr_name = f"{name} Airkare"
        self._attr_unique_id = f"{self._mac_address}_airkare"
        self._attr_icon = "mdi:air-filter"

        self._attr_device_info = {
            "identifiers": {("edilkamin", self._mac_address)}
        }

    @property
    def is_on(self) -> bool:
        """Return if airkare mode is on."""
        return edilkamin.device_info_get_airkare(self.coordinator.data)

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the entity on."""
        token = self.coordinator.get_token()
        await self.hass.async_add_executor_job(
            edilkamin.set_airkare,
            token,
            self._mac_address,
            True)
        await self.coordinator.async_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the entity off."""
        token = self.coordinator.get_token()
        await self.hass.async_add_executor_job(
            edilkamin.set_airkare,
            token,
            self._mac_address,
            False)
        await self.coordinator.async_refresh()
