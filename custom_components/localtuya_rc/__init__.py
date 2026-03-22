import logging
import asyncio
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .tuya_face import TuyaFace
from homeassistant.const import CONF_HOST, CONF_DEVICE_ID, CONF_ACCESS_TOKEN, CONF_NAME

_LOGGER = logging.getLogger(__name__)
DOMAIN = "localtuya_ultra" # Zmieniona domena

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Konfiguracja integracji ULTRA."""
    host = entry.data[CONF_HOST]
    device_id = entry.data[CONF_DEVICE_ID]
    local_key = entry.data[CONF_ACCESS_TOKEN]
    
    try:
        # Inicjalizacja urządzenia w sposób bezpieczny
        device = TuyaFace(host, device_id, local_key)
        hass.data.setdefault(DOMAIN, {})[entry.entry_id] = device
        
        # Rejestracja platformy remote
        await hass.config_entries.async_forward_entry_setups(entry, ["remote"])
        return True
    except Exception as e:
        _LOGGER.error("Błąd startu LocalTuya ULTRA (%s): %s", host, e)
        return False

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Rozładowanie integracji."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["remote"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
