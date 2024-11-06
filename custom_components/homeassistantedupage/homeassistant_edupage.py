import logging
from edupage_api import Edupage as APIEdupage
from datetime import datetime
from homeassistant.helpers.update_coordinator import UpdateFailed

_LOGGER = logging.getLogger(__name__)
class Edupage:
    def __init__(self,hass):
        self.hass = hass
        self.api = APIEdupage()

    def login(self, username, password, subdomain):

        return self.api.login(username, password, subdomain)

    async def get_grades(self):

        try:
            grades = await self.hass.async_add_executor_job(self.api.get_grades)
            _LOGGER.debug("get_grades() successful from API")
            return grades
        except Exception as e:
            raise UpdateFailed(F"error updating get_grades() data from API: {e}")

    async def get_timetable(self, dateTT: datetime):

        try:
            timetable = await self.hass.aync_add_executor_job(self.api.get_timetable())
            _LOGGER.debug("get_timetable() successful from API")
            return timetable
        except Exception as e:
            raise UpdateFailed(F"error updating get_timetable() data from API: {e}")

    async def async_update(self):

        pass
