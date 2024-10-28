from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up EduPage sensors based on subjects in the data."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    subjects = {}

    # Sortiere Noten nach Fächern
    for grade in coordinator.data:
        subject = grade.subject_name
        if subject not in subjects:
            subjects[subject] = []
        subjects[subject].append(grade)

    # Erstelle für jedes Fach einen Sensor
    sensors = [EduPageSubjectSensor(coordinator, subject, grades) for subject, grades in subjects.items()]
    async_add_entities(sensors, True)

class EduPageSubjectSensor(CoordinatorEntity, SensorEntity):
    """Sensor-Entität für ein bestimmtes Unterrichtsfach."""

    def __init__(self, coordinator, subject_name, grades):
        """Initialisierung des Fach-Sensors."""
        super().__init__(coordinator)
        self._subject_name = subject_name
        self._grades = grades
        self._attr_name = f"EduPage Noten - {subject_name}"  # Name des Sensors basierend auf dem Fach
        self._attr_unique_id = f"edupage_grades_{subject_name.lower().replace(' ', '_')}"

    @property
    def state(self):
        """Gibt die Anzahl der Noten für dieses Fach zurück."""
        return len(self._grades)

    @property
    def extra_state_attributes(self):
        """Rückgabe zusätzlicher Attribute für den Sensor."""
        attributes = {}
        for i, grade in enumerate(self._grades):
            attributes[f"grade_{i+1}_title"] = grade.title
            attributes[f"grade_{i+1}_grade_n"] = grade.grade_n
            attributes[f"grade_{i+1}_date"] = grade.date.strftime("%Y-%m-%d %H:%M:%S")
        return attributes
