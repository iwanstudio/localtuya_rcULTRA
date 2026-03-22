import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_DEVICE_ID, CONF_ACCESS_TOKEN, CONF_NAME
from .__init__ import DOMAIN

class LocalTuyaUltraConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Obsługa formularza konfiguracji ULTRA."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            # Tutaj można dodać walidację połączenia przed zapisem
            return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_NAME): str,
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_DEVICE_ID): str,
                vol.Required(CONF_ACCESS_TOKEN): str,
            }),
            errors=errors,
        )
