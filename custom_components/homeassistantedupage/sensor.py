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
    """Group grades based on subject_id."""
    grouped = defaultdict(list)
    for grade in grades:
        grouped[grade.subject_id].append(grade)
    return grouped


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up EduPage sensors based on subjects and their grades."""
    _LOGGER.info("SENSOR called async_setup_entry")

    coordinator = hass.data[DOMAIN][entry.entry_id]
    subjects = coordinator.data.get("subjects", [])
    grades = coordinator.data.get("grades", [])

    # Group grades based on subject_id
    grades_by_subject = group_grades_by_subject(grades)

    sensors = []
    for subject in subjects:
        # Get grades per subject based on subject_id
        subject_grades = grades_by_subject.get(subject.subject_id, [])
        sensor = EduPageSubjectSensor(
            coordinator,
            subject.name,
            subject_grades
        )
        sensors.append(sensor)

    async_add_entities(sensors, True)


class EduPageSubjectSensor(CoordinatorEntity, SensorEntity):
    """Subject sensor entity."""

    def __init__(self, coordinator, subject_name, grades=None):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._subject_name = subject_name
        self._grades = grades or []
        self._attr_name = f"EduPage subject - {subject_name}"
        self._attr_unique_id = f"edupage_grades_{subject_name.lower().replace(' ', '_')}"

    @property
    def state(self):
        """Return grade count."""
        return len(self._grades)

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        if not self._grades:
            return {"info": "no grades yet"}

        attributes = {}
        for i, grade in enumerate(self._grades):
            attributes[f"grade_{i+1}_title"] = grade.title
            attributes[f"grade_{i+1}_grade_n"] = grade.grade_n
            attributes[f"grade_{i+1}_date"] = grade.date.strftime("%Y-%m-%d %H:%M:%S")

            # Check if teacher exists before accessing name
            if grade.teacher:
                attributes[f"grade_{i+1}_teacher"] = grade.teacher.name
            else:
                attributes[f"grade_{i+1}_teacher"] = None  # Optional: Log warning
                _LOGGER.warning(f"Teacher information missing for grade {i+1} in subject {self._subject_name}.")
                
        return attributes
