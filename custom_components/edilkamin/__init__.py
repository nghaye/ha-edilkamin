"""The edilkamin integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform, CONF_PASSWORD, CONF_USERNAME, CONF_MAC, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN
from .coordinator import EdilkaminCoordinator

PLATFORMS: list[Platform] = [Platform.CLIMATE, Platform.FAN, Platform.SENSOR]
#PLATFORMS: list[Platform] = [Platform.FAN]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up edilkamin from a config entry."""

    mac_address = entry.data[CONF_MAC]

    coordinator = EdilkaminCoordinator(hass, entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD], mac_address)
    await coordinator.async_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data
    hass.data[DOMAIN]["coordinator"] = coordinator
    register_device(hass, entry, mac_address)
    #hass.config_entries.async_setup_platforms(entry, PLATFORMS)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

async def update_listener(hass, config_entry):
    """Handle options update."""
    await hass.config_entries.async_reload(config_entry.entry_id)

def register_device(hass, config_entry, mac_address):
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=config_entry.entry_id,
        identifiers={("edilkamin", mac_address)},
        manufacturer="EdilKamin",
        name=config_entry.data.get(CONF_NAME),
        model="The Mind",
        #sw_version=device_info.get("softwareVersion", DEFAULT_VERSION)
    )
