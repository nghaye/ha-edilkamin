from datetime import timedelta

import async_timeout
import edilkamin

from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import LOGGER

class EdilkaminCoordinator(DataUpdateCoordinator):
    """My custom coordinator."""

    def __init__(self, 
        hass, 
        username: str,
        password: str,
        mac_address: str,):
        """Initialize my coordinator."""
        super().__init__(
            hass,
            LOGGER,
            # Name of the data. For logging purposes.
            name="Edilkamin updater",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=60),
        )
        self._username = username
        self._password = password 
        self._mac_address = mac_address 

        self._token = None
        self._device_info = {}

    async def refresh_token(self) -> str:
        """Login to refresh the token."""
        return await self.hass.async_add_executor_job(edilkamin.sign_in, self._username, self._password)
        #return edilkamin.sign_in(self._username, self._password)

    async def update(self) -> None:
        """Get the latest data and update the relevant Entity attributes."""
        self._token = await self.refresh_token()
        return await self.hass.async_add_executor_job(edilkamin.device_info, self._token, self._mac_address)
        #return self._device_info

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            # Note: asyncio.TimeoutError and aiohttp.ClientError are already
            # handled by the data update coordinator.
            async with async_timeout.timeout(10):
                return await self.update()
        except :
            raise UpdateFailed(f"Error communicating with API")

    def get_token(self):
        return self._token

    def get_mac(self):
        return self._mac_address