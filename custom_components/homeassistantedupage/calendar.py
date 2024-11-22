from homeassistant.components.calendar import CalendarEventDevice
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.util import dt as dt_util
from datetime import datetime, timedelta

# Importiere die EduPage-API-Klassen, falls nötig
# from edupage_api.models import Timetable, Lesson

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the EduPage Calendar platform."""
    if discovery_info is None:
        return

    # Füge eine Instanz des Kalenders hinzu
    async_add_entities([EduPageCalendar(hass, discovery_info["name"], discovery_info["timetable_data"])])


class EduPageCalendar(CalendarEventDevice):
    """Representation of the EduPage Calendar."""

    def __init__(self, hass, name, timetable_data):
        """Initialize the calendar."""
        self._hass = hass
        self._name = name
        self._timetable_data = timetable_data
        self._events = []

    @property
    def name(self):
        """Return the name of the calendar."""
        return self._name

    async def async_get_events(self, hass, start_date, end_date):
        """Return all events in the specified date range."""
        events = []
        for lesson in self._timetable_data.lessons:
            start_time = datetime.combine(start_date, lesson.start_time)
            end_time = datetime.combine(start_date, lesson.end_time)

            # Füge das Event hinzu, wenn es im Zeitfenster liegt
            if start_time >= start_date and end_time <= end_date:
                event = {
                    "title": lesson.subject.name,
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat(),
                    "description": f"Lehrer: {', '.join([t.name for t in lesson.teachers])}",
                }
                events.append(event)

        self._events = events
        return events

    @property
    def extra_state_attributes(self):
        """Extra attributes of the calendar."""
        return {"number_of_events": len(self._events)}

    @property
    def event(self):
        """Return the next upcoming event."""
        now = dt_util.now()
        for event in self._events:
            if datetime.fromisoformat(event["start"]) > now:
                return event
        return None
