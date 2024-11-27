import logging
from datetime import datetime, timedelta, timezone
from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.helpers.update_coordinator import UpdateFailed
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
from collections import defaultdict
from zoneinfo import ZoneInfo

_LOGGER = logging.getLogger("custom_components.homeassistant_edupage")
_LOGGER.debug("CALENDAR Edupage calendar.py is being loaded")

async def async_setup_entry(hass, entry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up Edupage calendar entities."""
    _LOGGER.debug("CALENDAR called async_setup_entry")

    coordinator = hass.data[DOMAIN][entry.entry_id]

    edupage_calendar = EdupageCalendar(coordinator, entry.data)

    async_add_entities([edupage_calendar])

    _LOGGER.debug("CALENDAR async_setup_entry finished.")

async def async_added_to_hass(self) -> None:
    """When entity is added to hass."""
    await super().async_added_to_hass()
    _LOGGER.debug("CALENDAR added to hass")

    if self.coordinator:
        self.async_on_remove(
            self.coordinator.async_add_listener(
                self._handle_coordinator_update, None
            )
        )    

class EdupageCalendar(CoordinatorEntity, CalendarEntity):
    """Representation of an Edupage calendar entity."""

    def __init__(self, coordinator, data):
        super().__init__(coordinator)
        self._data = data 
        self._events = []
        self._attr_name = "Edupage Calendar"
        _LOGGER.debug(f"CALENDAR Initialized EdupageCalendar with data: {data}")

    @property
    def unique_id(self):
        """Return a unique ID for this calendar."""
        student_id = self.coordinator.data.get("student", {}).get("id", "unknown")
        return f"edupage_calendar_{student_id}"

    @property
    def name(self):
        """Return the name of the calendar."""
        student_name = self.coordinator.data.get("student", {}).get("name", "Unknown Student")
        return f"Edupage - {student_name}"
        
    @property
    def extra_state_attributes(self):
        """Return the extra state attributes."""
        return {
            "unique_id": self.unique_id,
            "other_info": "debug info"
        }

    @property
    def available(self) -> bool:
        """Return True if the calendar is available."""
        _LOGGER.debug("CALENDAR Checking availability of Edupage Calendar")
        return True

    @property
    def event(self):
        """Return the next upcoming event or None if no event exists."""
        local_tz = ZoneInfo(self.hass.config.time_zone)
        now = datetime.now(local_tz)
        return CalendarEvent(
            start=now + timedelta(hours=1),
            end=now + timedelta(hours=2),
            summary="Next Dummy Event",
            description="A placeholder event for debugging."
        )

    async def async_get_events(self, hass, start_date: datetime, end_date: datetime):
        """Return events in a specific date range."""
        local_tz = ZoneInfo(self.hass.config.time_zone)
        events = []

        _LOGGER.debug(f"CALENDAR Fetching events between {start_date} and {end_date}")
        timetable = self.coordinator.data.get("timetable", {})
        _LOGGER.debug(f"CALENDAR Coordinator data: {self.coordinator.data}")
        _LOGGER.debug(f"CALENDAR Fetched timetable data: {timetable}")

        if not timetable:
            _LOGGER.warning("CALENDAR Timetable data is missing.")
            return events

        current_date = start_date.date()
        while current_date <= end_date.date():
            day_timetable = timetable.get(current_date)
            if day_timetable:
                for lesson in day_timetable:

                    _LOGGER.debug(f"CALENDAR Lesson attributes: {vars(lesson)}")

                    room = "Unknown"
                    if lesson.classes and lesson.classes[0].homeroom:
                        room = lesson.classes[0].homeroom.name

                    teacher_names = [teacher.name for teacher in lesson.teachers] if lesson.teachers else []

                    teachers = ", ".join(teacher_names) if teacher_names else "Unknown Teacher"

                    start_time = datetime.combine(current_date, lesson.start_time).astimezone(local_tz)
                    end_time = datetime.combine(current_date, lesson.end_time).astimezone(local_tz)
                    events.append(
                        CalendarEvent(
                            start=start_time,
                            end=end_time,
                            summary=lesson.subject.name if lesson.subject else "Unknown Subject",
                            description=f"Room: {room}\nTeacher(s): {teachers}"
                        )
                    )
            current_date += timedelta(days=1)

        _LOGGER.debug(f"CALENDAR Fetched {len(events)} events from {start_date} to {end_date}")
        return events
