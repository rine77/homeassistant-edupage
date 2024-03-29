import logging
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.core import HomeAssistant
from .homeassistant_edupage import Edupage
from .subjects import subject_long

SCAN_INTERVAL = timedelta(minutes=3)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):

    username = entry.data["username"]
    password = entry.data["password"]
    subdomain = entry.data["subdomain"]

    edupage = Edupage(hass)
    
    unique_id_sensorGrade = f"edupage_{username}_gradesensor"
    await hass.async_add_executor_job(edupage.login, username, password, subdomain)

    async def async_update_data():
        _LOGGER.debug("Attempting to update grades data.")
        try:
            data = await edupage.get_grades()
            _LOGGER.debug("Grades data successfully updated")
            grades_list = [{"Fach": subject_long(grade.subject_name), "Thema": grade.title, "Note": grade.grade_n} for grade in data]
            return grades_list
        except Exception as e:
            _LOGGER.error(f"error updating data: {e}")
            raise UpdateFailed(F"error updating data: {e}")

    coordinator = DataUpdateCoordinator(
        hass,
        logger=_LOGGER,
        name="grades",
        update_method=async_update_data,
        update_interval=timedelta(minutes=10),
    )

    await coordinator.async_config_entry_first_refresh()
    async_add_entities([GradesSensor(edupage, unique_id_sensorGrade, coordinator)], True)

class GradesSensor(SensorEntity):
    def __init__(self, edupage: Edupage, unique_id: str, coordinator):
        self.edupage = edupage
        self._attr_unique_id = unique_id
        self.coordinator = coordinator

    @property
    def name(self):
        return "Edupage Grades"

    @property
    def state(self):

        return len(self.coordinator.data) if self.coordinator.data else "N/A"

    @property
    def extra_state_attributes(self):

        return {"grades": self.coordinator.data}

    def get_grades(self):

        return {"grades": self.coordinator.data}
    