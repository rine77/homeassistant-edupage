from edupage_api import Edupage as APIEdupage
from datetime import datetime

class Edupage:
    def __init__(self,hass):
        self.hass = hass
        self.api = APIEdupage()

    def login(self, username, password, subdomain):

        return self.api.login(username, password, subdomain)

    async def get_grades(self):

        grades = await self.hass.async_add_executor_job(self.api.get_grades)
        return grades

    async def get_timetable(self, dateTT: datetime):

        timetable = await self.hass.aync_add_executor_job(self.api.get_timetable(dateTT))
        return timetable

    async def async_update(self):

        pass
