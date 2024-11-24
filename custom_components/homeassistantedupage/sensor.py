import logging
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
    _LOGGER.info("SENSOR called async_setup_entry")

    coordinator = hass.data[DOMAIN][entry.entry_id]
    student = coordinator.data.get("student", {})
    subjects = coordinator.data.get("subjects", [])
    grades = coordinator.data.get("grades", [])

    # group grades based on subject_id
    grades_by_subject = group_grades_by_subject(grades)

    sensors = []
    for subject in subjects:
        # get grades per subject based on subject_id
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
        self._student_name = student_name
        self._subject_name = subject_name
        self._grades = grades or [] 
        self._attr_name = f"{student_name} - {subject_name}"
        self._attr_unique_id = f"edupage_grades_{student_id}_{subject_name.lower().replace(' ', '_')}"

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
        for i, grade in enumerate(self._grades):
            attributes[f"grade_{i+1}_title"] = grade.title
            attributes[f"grade_{i+1}_grade_n"] = grade.grade_n
            attributes[f"grade_{i+1}_date"] = grade.date.strftime("%Y-%m-%d %H:%M:%S")
            attributes[f"grade_{i+1}_teacher"] = grade.teacher.name
        return attributes


