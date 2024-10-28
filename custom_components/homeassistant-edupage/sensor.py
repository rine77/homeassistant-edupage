from datetime import datetime
import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

_LOGGER = logging.getLogger("custom_components.homeassistant_edupage")

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up EduPage sensor based on a config entry."""
    # access coordinator via hass.data
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([EduPageSensor(coordinator, entry)], True)

class EduPageSensor(CoordinatorEntity, SensorEntity):
    """Sensor-Entity for EduPage-grades."""

    def __init__(self, coordinator, entry):
        """initializing sensor."""
        super().__init__(coordinator)
        self.entry = entry
        self._attr_name = "EduPage Grade Sensor"  # sensor name
        self._attr_unique_id = f"edupage_{entry.data['username']}_gradesensor" # uniqueID

    @property
    def state(self):
        """returns grade count as sensor state"""
        data = self.coordinator.data
        
        if isinstance(data, list):
            return len(data)  # Anzahl der Einträge in der Liste
        return 0  # Fallback-Wert, falls data keine Liste ist

