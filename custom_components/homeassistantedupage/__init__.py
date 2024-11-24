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
    student_id = entry.data["student_id"]
    edupage = Edupage(hass)

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
        """Function to fetch timetable data for the selected student."""
        _LOGGER.info("INIT called fetch_data")

        async with fetch_lock:
            try:
                await edupage.login(username, password, subdomain)

                students = await edupage.get_students()
                student = next((s for s in students if s.person_id == student_id), None)
                _LOGGER.info("INIT Student: %s", student)

                if not student:
                    _LOGGER.error("No matching student found with ID: %s", student_id)
                    return {"timetable": {}}

                _LOGGER.debug("Found EduStudent: %s", vars(student))

                timetable_data = {}
                today = datetime.now().date()
                for offset in range(14):
                    current_date = today + timedelta(days=offset)
                    timetable = await edupage.get_timetable(student, current_date)
                    if timetable:
                        _LOGGER.debug(f"Timetable for {current_date}: {timetable}")
                        timetable_data[current_date] = timetable
                    else:
                        _LOGGER.warning(f"No timetable found for {current_date}")

                return {
                    "student": {"id": student.person_id, "name": student.name},
                    "timetable": timetable_data,
                }

            except Exception as e:
                _LOGGER.error("Failed to fetch timetable: %s", e)
                return {"timetable": {}}


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
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, "calendar")
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

