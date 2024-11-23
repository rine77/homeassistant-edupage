import logging
import asyncio
from datetime import datetime, timedelta
from edupage_api.exceptions import BadCredentialsException, CaptchaException
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .homeassistant_edupage import Edupage
from edupage_api.classes import Class
from edupage_api.people import EduTeacher
from edupage_api.people import Gender
from edupage_api.classrooms import Classroom
from .const import DOMAIN

_LOGGER = logging.getLogger("custom_components.homeassistant_edupage")

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """only ConfigEntry supported, no configuration.yaml yet"""
    _LOGGER.info("INIT called async_setup")
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """initializin EduPage-integration and validate API-login"""
    _LOGGER.info("INIT called async_setup_entry")

    username = entry.data["username"]
    password = entry.data["password"]
    subdomain = entry.data["subdomain"]
    edupage = Edupage(hass)

    try:
        # _LOGGER.debug("Begin creating first teacher instance")
        teacher1 = EduTeacher(
            person_id=-17,
            name="Anka Kehr",
            gender=Gender.FEMALE,
            in_school_since=None,
            classroom_name="Haus 1 R 08",
            teacher_to=None
        )
        # _LOGGER.debug("First teacher instance created: %s", teacher1)

        teacher2 = EduTeacher(
            person_id=-25,
            name="Christiane Koch",
            gender=Gender.FEMALE,
            in_school_since=None,
            classroom_name="Haus 1 R 08",
            teacher_to=None
        )
        # _LOGGER.debug("Teacher2 created successfully: %s", teacher2)

        classroom = Classroom(
            classroom_id=-12,
            name="Haus 1 R 08",
            short="H1 R08"
        )
        # _LOGGER.debug("Classroom created successfully: %s", classroom)

        class_instance = Class(
            class_id=-28,
            name="4b",
            short="4b",
            homeroom_teachers=[teacher1, teacher2],
            homeroom=classroom,
            grade=None
        )
        # _LOGGER.debug("Class instance created successfully: %s", class_instance)

    except Exception as e:
        _LOGGER.error("INIT Error during instantiation: %s", e)

    try:
        login_success = await hass.async_add_executor_job(
            edupage.login, username, password, subdomain
        )
        _LOGGER.info("INIT login_success")

    except BadCredentialsException as e:
        _LOGGER.error("INIT login failed: bad credentials. %s", e)
        return False

    except CaptchaException as e:
        _LOGGER.error("INIT login failed: CAPTCHA needed. %s", e)
        return False  

    except Exception as e:
        _LOGGER.error("INIT unexpected login error: %s", e)
        return False  

    fetch_lock = asyncio.Lock() 

    async def fetch_data():
        """Function to fetch grade and timetable data."""
        _LOGGER.info("INIT called fetch_data")    

        async with fetch_lock:
            try:
                # Daten abrufen
                classes_data = await edupage.get_classes()
                grades_data = await edupage.get_grades()
                userid = await edupage.get_user_id()
                subjects_data = await edupage.get_subjects()
                students_data = await edupage.get_students()
                teachers_data = await edupage.get_teachers()
                classrooms_data = await edupage.get_classrooms()

                # Stundenplan für die nächsten 14 Tage abrufen
                today = datetime.now().date()
                timetable_data = {}
                for offset in range(14):
                    current_date = today + timedelta(days=offset)
                    timetable_data[current_date] = await edupage.get_timetable(class_instance, current_date)

                _LOGGER.info("INIT got timetables before return")

                # Daten zusammenstellen
                return {
                    "classes": classes_data,
                    "grades": grades_data,
                    "user_id": userid,
                    "subjects": subjects_data,
                    "students": students_data,
                    "teachers": teachers_data,
                    "classrooms": classrooms_data,
                    "timetable": timetable_data,
                }

            except Exception as e:
                _LOGGER.error("INIT Failed to fetch Edupage data: %s", e)
                return False

    try:
        coordinator = DataUpdateCoordinator(
            hass,
            _LOGGER,
            name="EduPage Data",
            update_method=fetch_data,
            update_interval=timedelta(minutes=60),
        )
        _LOGGER.info("INIT coordinator instantiated")
    except Exception as e:
        _LOGGER.info("INIT coordinator not instantiated")

    # First data fetch
    await asyncio.sleep(1)
    await coordinator.async_config_entry_first_refresh()

    # Save coordinator
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Forward platforms
    _LOGGER.info(f"INIT Forwarding entry for platforms: calendar")
    #await hass.config_entries.async_forward_entry_setups(entry, [Platform.CALENDAR])
    await hass.config_entries.async_forward_entry_setups(entry, ["calendar"])
    _LOGGER.info(f"INIT forwarded")    
    _LOGGER.debug(f"INIT Coordinator data: {coordinator.data}")

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload ConfigEntry."""
    _LOGGER.info("INIT called async_unload_entry")    
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, ["calendar"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

