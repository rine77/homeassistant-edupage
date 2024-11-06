import logging
import asyncio
from datetime import timedelta
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
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """create ConfigEntry an DataUpdateCoordinator"""
    _LOGGER.info("called async_setup_entry")

    username = entry.data["username"]
    password = entry.data["password"]
    subdomain = entry.data["subdomain"]
    edupage = Edupage(hass)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """initializin EduPage-integration and validate API-login"""
    username = entry.data["username"]
    password = entry.data["password"]
    subdomain = entry.data["subdomain"]
    edupage = Edupage(hass)
    unique_id_sensorGrade = f"edupage_{username}_gradesensor"

    try:
        login_success = await hass.async_add_executor_job(
            edupage.login, username, password, subdomain
        )

    except BadCredentialsException as e:
        _LOGGER.error("login failed: bad credentials. %s", e)
        return False  # stop initialization on any exception

    except CaptchaException as e:
        _LOGGER.error("login failed: CAPTCHA needed. %s", e)
        return False  

    except Exception as e:
        _LOGGER.error("unexpected login error: %s", e)
        return False  

    fetch_lock = asyncio.Lock() 

    async def fetch_data():
        """function to fetch grade data."""
        async with fetch_lock:

            try:
                grades_data = await edupage.get_grades()
                _LOGGER.debug("grades_data: %s", grades_data)  # Zeigt die Daten im Log
                return grades_data 
            except Exception as e:
                _LOGGER.error("error fetching grades data: %s", e)
                return []

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="EduPage Data",
        update_method=fetch_data,
        update_interval=timedelta(minutes=5),
    )

    # first data fetch
    await asyncio.sleep(1)
    await coordinator.async_config_entry_first_refresh()
    #await coordinator.async_request_refresh()

    # save coordinator
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # platforms forward
    await hass.config_entries.async_forward_entry_setups(entry, [Platform.SENSOR])

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload ConfigEntry."""
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, Platform.SENSOR)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
