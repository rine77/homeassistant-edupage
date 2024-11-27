import logging
import asyncio
from datetime import datetime, timedelta
from edupage_api import Edupage as EdupageApi
from edupage_api.exceptions import BadCredentialsException, CaptchaException, SecondFactorFailedException
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .homeassistant_edupage import Edupage
from edupage_api.classes import Class
from edupage_api.people import EduTeacher
from edupage_api.people import Gender
from edupage_api.classrooms import Classroom
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from .const import DOMAIN, CONF_PHPSESSID, CONF_SUBDOMAIN, CONF_STUDENT_ID, CONF_STUDENT_NAME

_LOGGER = logging.getLogger("custom_components.homeassistant_edupage")

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """only ConfigEntry supported, no configuration.yaml yet"""
    _LOGGER.debug("INIT called async_setup")
    return True

def login_wrapper(edupage: Edupage, username: str, password: str, subdomain: str):
    #TODO hier ist noch was unsauber bzgl async und await
    edupage.login(username=username, password=password, subdomain=subdomain)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """initializin EduPage-integration and validate API-login"""
    _LOGGER.debug("INIT called async_setup_entry")
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {} 

    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]
    subdomain = entry.data[CONF_SUBDOMAIN]
    PHPSESSID = entry.data[CONF_PHPSESSID]
    student_id = entry.data[CONF_STUDENT_ID]
    edupage = Edupage(hass=hass, sessionid=PHPSESSID)
    coordinator = None

    try:        
        login_success = await hass.async_add_executor_job(
           login_wrapper, edupage, username, password, subdomain
        )
        _LOGGER.debug("INIT login_success")

    except BadCredentialsException as e:
        _LOGGER.error("INIT login failed: bad credentials. %s", e)
        return False

    except CaptchaException as e:
        _LOGGER.error("INIT login failed: CAPTCHA needed. %s", e)
        return False  

    except Exception as e:
        _LOGGER.error("INIT unexpected login error: %s", e.with_traceback(None))
        return False  

    fetch_lock = asyncio.Lock() 

    async def fetch_data():
        """Function to fetch timetable data for the selected student."""
        _LOGGER.debug("INIT called fetch_data")

        async with fetch_lock:
            try:
                await edupage.login(username, password, subdomain)

                students = await edupage.get_students()
                student = next((s for s in students if s.person_id == student_id), None)
                _LOGGER.debug("INIT Student: %s", student)

                if not student:
                    _LOGGER.error("INIT No matching student found with ID: %s", student_id)
                    return {"timetable": {}}

                _LOGGER.debug("INIT Found EduStudent: %s", vars(student))

                grades = await edupage.get_grades()
                subjects = await edupage.get_subjects()

                timetable_data = {}
                today = datetime.now().date()
                for offset in range(14):
                    current_date = today + timedelta(days=offset)
                    timetable = await edupage.get_timetable(student, current_date)
                    if timetable:
                        _LOGGER.debug(f"Timetable for {current_date}: {timetable}")
                        timetable_data[current_date] = timetable
                    else:
                        _LOGGER.warning(f"INIT No timetable found for {current_date}")

                return_data = {
                    "student": {"id": student.person_id, "name": student.name},
                    "grades": grades,
                    "subjects": subjects,
                    "timetable": timetable_data,
                }
                _LOGGER.debug(f"INIT Coordinator fetch_data returning: {return_data}")
                return return_data

            except Exception as e:
                _LOGGER.error("INIT Failed to fetch timetable: %s", e)
                return {"timetable": {}}

    try:
        coordinator = DataUpdateCoordinator(
            hass,
            _LOGGER,
            name="Edupage",
            update_method=fetch_data,
            update_interval=timedelta(minutes=30),
        )
        hass.data[DOMAIN][entry.entry_id] = coordinator

        await coordinator.async_config_entry_first_refresh()
        _LOGGER.debug("INIT Coordinator successfully initialized")

    except Exception as e:
        _LOGGER.error(f"INIT Error during async_setup_entry: {e}")

        if entry.entry_id in hass.data[DOMAIN]:
            del hass.data[DOMAIN][entry.entry_id]

        return False

    await asyncio.sleep(1)
    await coordinator.async_config_entry_first_refresh()
    _LOGGER.debug(f"INIT Coordinator first fetch!")

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, ["calendar", "sensor"])
    _LOGGER.debug(f"INIT forwarded")    
    _LOGGER.debug(f"INIT Coordinator data: {coordinator.data}")

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload ConfigEntry."""
    _LOGGER.debug("INIT called async_unload_entry")
    
    unload_calendar = await hass.config_entries.async_forward_entry_unload(entry, "calendar")
    unload_sensor = await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    
    unload_ok = unload_calendar and unload_sensor
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok
