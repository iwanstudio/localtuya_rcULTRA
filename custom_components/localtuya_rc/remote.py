import logging
import asyncio
import async_timeout
from homeassistant.components.remote import RemoteEntity
from .__init__ import DOMAIN

_LOGGER = logging.getLogger(__name__)
CONNECTION_TIMEOUT = 3.0 # Maksymalny czas czekania na pilota

class TuyaRemote(RemoteEntity):
    def __init__(self, device, name, entry_id):
        self._device = device
        self._name = name
        self._attr_unique_id = f"{entry_id}_remote"
        self._available = True
        self._state = False

    @property
    def name(self):
        return self._name

    @property
    def available(self) -> bool:
        return self._available

    @property
    def is_on(self):
        return self._state

    async def async_turn_on(self, **kwargs):
        self._state = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        self._state = False
        self.async_write_ha_state()

    async def async_update(self):
        """Sprawdzanie czy pilot żyje bez mrożenia HA."""
        try:
            async with async_timeout.timeout(CONNECTION_TIMEOUT):
                # Wykonujemy status w osobnym wątku
                await self.hass.async_add_executor_job(self._device.status)
                self._available = True
        except Exception:
            if self._available:
                _LOGGER.warning("Pilot ULTRA '%s' nie odpowiada - przechodzę w tryb offline.", self._name)
            self._available = False

    async def async_send_command(self, command, **kwargs):
        """Bezpieczne wysyłanie komend IR."""
        if not self._available:
            _LOGGER.error("Pilot '%s' jest offline. Komenda zignorowana.", self._name)
            return

        for cmd in command:
            try:
                async with async_timeout.timeout(CONNECTION_TIMEOUT):
                    await self.hass.async_add_executor_job(self._device.send_command, cmd)
            except asyncio.TimeoutError:
                _LOGGER.error("Timeout podczas wysyłania IR do '%s'. System HA działa dalej.", self._name)
                self._available = False
                break
            except Exception as e:
                _LOGGER.error("Błąd krytyczny pilota '%s': %s", self._name, e)
                break
        self.async_write_ha_state()
