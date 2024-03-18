import logging
import voluptuous as vol
from edupage_api import Edupage
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from .const import DOMAIN 

_LOGGER = logging.getLogger(__name__)

CONF_SUBDOMAIN = "subdomain"

class EdupageConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for edupage_api."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # validate this and that - later
            return self.async_create_entry(title="Edupage", data=user_input)

        # data schema for user input
        data_schema = vol.Schema({
            vol.Required(CONF_USERNAME): str,
            vol.Required(CONF_PASSWORD): str,
            vol.Required(CONF_SUBDOMAIN): str,
        })

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )
