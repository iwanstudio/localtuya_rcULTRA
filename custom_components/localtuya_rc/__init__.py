import logging
from .tuya_face import TuyaFace
from homeassistant.const import CONF_HOST, CONF_DEVICE_ID, CONF_ACCESS_TOKEN, CONF_NAME

_LOGGER = logging.getLogger(__name__)
DOMAIN = "localtuya_rc"

async def async_setup_entry(hass, entry):
    """Konfiguracja integracji z poziomu UI (Config Flow)."""
    host = entry.data[CONF_HOST]
    device_id = entry.data[CONF_DEVICE_ID]
    local_key = entry.data[CONF_ACCESS_TOKEN]
    name = entry.data[CONF_NAME]

    try:
        # Inicjalizacja biblioteki komunikacyjnej
        device = TuyaFace(host, device_id, local_key)
        
        # Dodanie encji do HA
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, "remote")
        )
        
        # Przechowywanie obiektu urządzenia w hass.data
        hass.data.setdefault(DOMAIN, {})[entry.entry_id] = device
        return True
    except Exception as e:
        _LOGGER.error("Błąd podczas łączenia z Tuya IR %s: %s", host, e)
        return False
