from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform
from .const import DOMAIN

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """only ConfigEntry, no configuration.yaml"""

    return True

async def async_setup_entry(hass,entry) -> bool:
    """create ConfigEntry"""

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, Platform.SENSOR)
    )
    
    return True

async def async_unload_entry(hass,entry) -> bool:
    """unload ConfigEntry"""

    return await hass.config_entries.async_forward_entry_unload(entry, 'sensor')
