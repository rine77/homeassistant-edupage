import logging
from edupage_api import Edupage as APIEdupage
from edupage_api.classes import Class
from edupage_api.people import EduTeacher
from edupage_api.people import Gender
from edupage_api.classrooms import Classroom

from datetime import datetime
from datetime import date
from homeassistant.helpers.update_coordinator import UpdateFailed
from concurrent.futures import ThreadPoolExecutor

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

    async def get_timetable(self):
        try:
            _LOGGER.debug("Begin creating first teacher instance")
            teacher1 = EduTeacher(
                person_id=-17,
                name="Anka Kehr",
                gender=Gender.FEMALE,
                in_school_since=None,
                classroom_name="Haus 1 R 08",
                teacher_to=None
            )
            _LOGGER.debug("First teacher instance created: %s", teacher1)

            teacher2 = EduTeacher(
                person_id=-25,
                name="Christiane Koch",
                gender=Gender.FEMALE,
                in_school_since=None,
                classroom_name="Haus 1 R 08",
                teacher_to=None
            )
            _LOGGER.debug("Teacher2 created successfully: %s", teacher2)

            classroom = Classroom(
                classroom_id=-12,
                name="Haus 1 R 08",
                short="H1 R08"
            )
            _LOGGER.debug("Classroom created successfully: %s", classroom)

            class_instance = Class(
                class_id=-28,
                name="4b",
                short="4b",
                homeroom_teachers=[teacher1, teacher2],
                homeroom=classroom,
                grade=None
            )
            _LOGGER.debug("Class instance created successfully: %s", class_instance)

        except Exception as e:
            _LOGGER.error("Error during instantiation: %s", e)

        try:
            executor = ThreadPoolExecutor(max_workers=5)
            timetable_data = await self.hass.async_add_executor_job(self.api.get_timetable, class_instance, date.today())
            if timetable_data is None:
                _LOGGER.info("EDUPAGE timetable is None")
            else:
                _LOGGER.info("EDUPAGE timetable_data: $s", timetable_data)
                return timetable_data
        except Exception as e:
            raise UpdateFailed(F"EDUPAGE error updating get_timetable() data from API: {e}")

    async def async_update(self):

        pass
