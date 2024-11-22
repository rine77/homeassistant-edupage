import logging
import asyncio
from datetime import timedelta
import datetime
from edupage_api.exceptions import BadCredentialsException, CaptchaException
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .homeassistant_edupage import Edupage
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
    unique_id_sensorGrade = f"edupage_{username}_gradesensor"

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
                # request classes
                classes_data = await edupage.get_classes()
#                _LOGGER.info("INIT classes count: " + str(len(classes_data)))
                    
                # request grades
                grades_data = await edupage.get_grades()
#                _LOGGER.info("INIT grade count: " + str(len(grades_data)))

                # request user_id
                userid = await edupage.get_user_id()
#                _LOGGER.info("INIT user_id: "+str(userid))

                # request all possible subjects
                subjects_data = await edupage.get_subjects()
#                _LOGGER.info("INIT subject count: " + str(len(subjects_data)))

                # request all possible students
                students_data = await edupage.get_students()
#                _LOGGER.info("INIT students count: " + str(len(students_data)))

                return {
                    "grades": grades_data,
#                    "timetable": timetable_data,
                    "user_id": userid,
                    "subjects": subjects_data
                }

            except Exception as e:
                _LOGGER.error("INIT error fetching data: %s", e)
                return False

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="EduPage Data",
        update_method=fetch_data,
        update_interval=timedelta(minutes=5),
    )

    # First data fetch
    await asyncio.sleep(1)
    await coordinator.async_config_entry_first_refresh()

    # Save coordinator
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Forward platforms
    await hass.config_entries.async_forward_entry_setups(entry, [Platform.SENSOR])

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload ConfigEntry."""
    _LOGGER.info("INIT called async_unload_entry")    
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, Platform.SENSOR)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
