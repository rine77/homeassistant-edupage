import logging
import asyncio
from edupage_api import Login
from edupage_api import Edupage as APIEdupage
from edupage_api.classes import Class
from edupage_api.people import EduTeacher
from edupage_api.people import Gender
from edupage_api.classrooms import Classroom
from zoneinfo import ZoneInfo
from edupage_api.exceptions import BadCredentialsException, CaptchaException, SecondFactorFailedException


from datetime import datetime
from datetime import date
from homeassistant.helpers.update_coordinator import UpdateFailed
from concurrent.futures import ThreadPoolExecutor

_LOGGER = logging.getLogger(__name__)

class Edupage:
    def __init__(self,hass, sessionid = ''):
        self.hass = hass
        self.sessionid = sessionid
        self.api = APIEdupage()

    async def login(self, username: str, password: str, subdomain: str):
        """Perform login asynchronously."""
        try:
            result = True
            login = Login(self.api)
            await asyncio.to_thread(
                login.reload_data, subdomain, self.sessionid, username
            )
            if not self.api.is_logged_in:
                #TODO: how to handle 2FA at this point?!
                result = await asyncio.to_thread(self.api.login, username, password, subdomain)
            _LOGGER.debug(f"EDUPAGE Login successful, result: {result}")
            return result
        except BadCredentialsException as e:
            _LOGGER.error("EDUPAGE login failed: bad credentials. %s", e)
            return False

        except CaptchaException as e:
            _LOGGER.error("EDUPAGE login failed: CAPTCHA needed. %s", e)
            return False 

        except SecondFactorFailedException as e:
            #TODO hier müsste man dann irgendwie abfangen, falls die session mal abgelaufen ist. und dies dann auch irgendwie via HA sauber zum Nutzer bringen!?
            _LOGGER.error("EDUPAGE login failed: 2FA error. %s", e)
            return False  

        except Exception as e:
            _LOGGER.error("EDUPAGE unexpected login error: %s", e)
            return False  

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

    async def get_classrooms(self):

        try:
            all_classrooms = await self.hass.async_add_executor_job(self.api.get_classrooms)
            return all_classrooms
        except Exception as e:
            raise UpdateFailed(F"EDUPAGE error updating get_classrooms data from API: {e}")
    
    async def get_teachers(self):

        try:
            all_teachers = await self.hass.async_add_executor_job(self.api.get_teachers)
            return all_teachers
        except Exception as e:
            raise UpdateFailed(F"EDUPAGE error updating get_teachers data from API: {e}")

    async def get_timetable(self, EduStudent, date):
        try:
            timetable_data = await self.hass.async_add_executor_job(self.api.get_timetable, EduStudent, date)
            if timetable_data is None:
                _LOGGER.debug("EDUPAGE timetable is None")
            else:
                _LOGGER.debug(f"EDUPAGE timetable_data for {date}: {timetable_data}")
                return timetable_data
        except Exception as e:
            _LOGGER.error(f"EDUPAGE error updating get_timetable() data for {date}: {e}")
            raise UpdateFailed(f"EDUPAGE error updating get_timetable() data for {date}: {e}")

    async def async_update(self):

        pass
