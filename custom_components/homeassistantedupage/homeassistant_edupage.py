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

    async def get_classes(self):

        try:
            classes_data = await self.hass.async_add_executor_job(self.api.get_classes)
            return classes_data
        except Exception as e:
            raise UpdateFailed(F"EDUPAGE error updating get_classes() data from API: {e}")

    async def get_grades(self):

        try:
            grades = await self.hass.async_add_executor_job(self.api.get_grades)
            return grades
        except Exception as e:
            raise UpdateFailed(F"EDUPAGE error updating get_grades() data from API: {e}")

    async def get_subjects(self):

        try:
            all_subjects = await self.hass.async_add_executor_job(self.api.get_subjects)
            return all_subjects
        except Exception as e:
            raise UpdateFailed(F"EDUPAGE error updating get_subjects() data from API: {e}")

    async def get_students(self):

        try:
            all_students = await self.hass.async_add_executor_job(self.api.get_students)
            return all_students
        except Exception as e:
            raise UpdateFailed(F"EDUPAGE error updating get_students() data from API: {e}")

    async def get_user_id(self):

        try:
            user_id_data = await self.hass.async_add_executor_job(self.api.get_user_id)
            return user_id_data
        except Exception as e:
            raise UpdateFailed(F"EDUPAGE error updating get_user_id() data from API: {e}")

    async def async_update(self):

        pass
