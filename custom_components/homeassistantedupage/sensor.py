import logging
import re
from unidecode import unidecode
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
from collections import defaultdict

_LOGGER = logging.getLogger("custom_components.homeassistant_edupage")

def group_grades_by_subject(grades):
    """grouping grades based on subject_id."""
    grouped = defaultdict(list)
    for grade in grades:
        grouped[grade.subject_id].append(grade)
    return grouped

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up EduPage sensors for each student and their grades."""
    _LOGGER.debug("SENSOR called async_setup_entry")

    coordinator = hass.data[DOMAIN][entry.entry_id]
    student = coordinator.data.get("student", {})
    subjects = coordinator.data.get("subjects", [])
    grades = coordinator.data.get("grades", [])

    grades_by_subject = group_grades_by_subject(grades)

    sensors = []
    for subject in subjects:
        subject_grades = grades_by_subject.get(subject.subject_id, [])
        sensor = EduPageSubjectSensor(
            coordinator,
            student.get("id"),
            student.get("name"),
            subject.name,
            subject_grades
        )
        sensors.append(sensor)

    async_add_entities(sensors, True)

class EduPageSubjectSensor(CoordinatorEntity, SensorEntity):
    """Subject sensor entity for a specific student."""

    def __init__(self, coordinator, student_id, student_name, subject_name, grades=None):
        """Initialize the sensor."""
        super().__init__(coordinator)

        self._student_id = student_id
        self._student_name = unidecode(student_name).replace(' ', '_').lower()
        self._subject_name = unidecode(subject_name).replace(' ', '_').lower()
        self._grades = grades or []

        self._attr_name = f"{student_name} - {subject_name}"
        self._name = self._attr_name

        self._unique_id = f"edupage_subject_{self._student_id}_{self._student_name}_{self._subject_name}"

        _LOGGER.info("SENSOR unique_id %s", self._unique_id)

    @property
    def unique_id(self):
        """Return a unique identifier for this sensor."""
        return self._unique_id

    @property
    def state(self):
        """Return the grade count."""
        return len(self._grades)

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        if not self._grades:
            return {"info": "no grades yet"}

        attributes = {"student": self._student_name}
        attributes = {"unique_id": self._unique_id}
        for i, grade in enumerate(self._grades):
            attributes[f"grade_{i+1}_title"] = grade.title
            attributes[f"grade_{i+1}_grade_n"] = grade.grade_n
            attributes[f"grade_{i+1}_date"] = grade.date.strftime("%Y-%m-%d %H:%M:%S")

            teacher_name = grade.teacher.name if grade.teacher else "unknown"
            attributes[f"grade_{i+1}_teacher"] = teacher_name

        return attributes
