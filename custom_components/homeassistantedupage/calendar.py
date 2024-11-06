import voluptuous as vol
import logging
from datetime import datetime, timedelta
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.core import HomeAssistant
from .homeassistant_edupage import Edupage

from homeassistant.components.calendar import CalendarEntity

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):

    username = entry.data["username"]
    password = entry.data["password"]
    subdomain = entry.data["subdomain"]

    edupage = Edupage(hass)
    unique_id = f"edupage_{username}_calendar"
    await hass.async_add_executor_job(edupage.login, username, password, subdomain)

    async def async_update_data():

        today = datetime.now().date()
        try:
            return await edupage.get_timetable(today)
        except Exception as e:
            _LOGGER.error(f"error updating data: {e}")
            raise UpdateFailed(F"error updating data: {e}")

    async_add_entities([TimetableCalendar(edupage, unique_id)], True)

class TimetableCalendar(CalendarEntity):
    def __init__(self, edupage, unique_id):
        self.edupage = edupage
        self._attr_unique_id = unique_id
     
    @property
    def name(self):
        """return name of calendar"""
        return self._name
    
    async def async_get_events(self, today: datetime):
        timetable = self.get_timetable(today)
        # Konvertieren Sie 'timetable' in eine Liste von Ereignissen, die von dieser Methode zurückgegeben werden
        return timetable #dict
