import logging
import asyncio
import async_timeout
from homeassistant.components.remote import RemoteEntity
from homeassistant.const import CONF_NAME, CONF_HOST, CONF_DEVICE_ID, CONF_ACCESS_TOKEN

_LOGGER = logging.getLogger(__name__)

# Ustawiamy timeout na 3 sekundy, żeby HA nie wisiał w nieskończoność
CONNECTION_TIMEOUT = 3.0

class TuyaRemote(RemoteEntity):
    def __init__(self, device, name):
        self._device = device
        self._name = name
        self._available = True
        self._state = False

    @property
    def name(self):
        return self._name

    @property
    def is_on(self):
        return self._state

    @property
    def available(self) -> bool:
        """Zwraca dostępność urządzenia. Jeśli False, HA wyszarzy encję."""
        return self._available

    async def async_turn_on(self, **kwargs):
        self._state = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        self._state = False
        self.async_write_ha_state()

    async def async_update(self):
        """Cykliczne sprawdzanie statusu urządzenia (Health Check)."""
        try:
            # Używamy executor_job, by operacja sieciowa nie blokowała pętli głównej
            async with async_timeout.timeout(CONNECTION_TIMEOUT):
                await self.hass.async_add_executor_job(self._device.status)
                self._available = True
        except (asyncio.TimeoutError, Exception):
            if self._available:
                _LOGGER.warning("Kontroler Tuya IR '%s' przestał odpowiadać (Timeout).", self._name)
            self._available = False

    async def async_send_command(self, command, **kwargs):
        """Wysyłanie kodów IR z zabezpieczeniem przed zamarznięciem."""
        if not self._available:
            _LOGGER.error("Nie można wysłać komendy do '%s' - urządzenie jest OFFLINE.", self._name)
            return

        for cmd in command:
            try:
                _LOGGER.debug("Wysyłanie kodu IR do %s: %s", self._name, cmd)
                # Kluczowe: async_add_executor_job zapobiega zamrożeniu interfejsu
                async with async_timeout.timeout(CONNECTION_TIMEOUT):
                    await self.hass.async_add_executor_job(self._device.send_command, cmd)
            except asyncio.TimeoutError:
                _LOGGER.error("Timeout przy wysyłaniu komendy do '%s'. Oznaczam jako niedostępne.", self._name)
                self._available = False
                break
            except Exception as e:
                _LOGGER.error("Błąd wysyłania komendy do '%s': %s", self._name, e)
                break
        
        self.async_write_ha_state()
