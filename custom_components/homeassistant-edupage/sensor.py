import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .edupage import Edupage
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    # config data from config_flow
    username = entry.data["username"]
    password = entry.data["password"]
    subdomain = entry.data["subdomain"]

    edupage = Edupage()
    unique_id = f"edupage_{username}_sensor"
    await hass.async_add_executor_job(edupage.login, username, password, subdomain)

    async_add_entities([EdupageSensor(edupage, unique_id)], True)

class EdupageSensor(SensorEntity):
    def __init__(self, edupage: Edupage, unique_id: str):
        self.edupage = edupage
        self._attr_unique_id = unique_id
        self._state = None

    @property
    def name(self):
        """return the name of the sensor"""
        return "Edupage Sensor"

    @property
    def state(self):
        """return state of the sensor"""
        return self._state

    @property
    def unique_id(self):
        """return unique_id of the sensor"""
        return self._attr_unique_id

    async def async_update(self):
        """updates data"""
        pass