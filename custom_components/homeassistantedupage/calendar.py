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
_LOGGER.info("CALENDAR - Edupage calendar.py is being loaded")

async def async_setup_entry(hass, entry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up Edupage calendar entities."""
    _LOGGER.info("CALENDAR called async_setup_entry")

    coordinator = hass.data[DOMAIN][entry.entry_id]

    edupage_calendar = EdupageCalendar(coordinator, entry.data)

    async_add_entities([edupage_calendar])

    _LOGGER.info("CALENDAR async_setup_entry finished.")


async def async_added_to_hass(self) -> None:
    """When entity is added to hass."""
    await super().async_added_to_hass()
    _LOGGER.info("CALENDAR added to hass")

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
        self.coordinator = coordinator
        self._data = data
        self._events = []
        self._attr_name = F"EdupageCal"
        _LOGGER.info(f"CALENDAR Initialized EdupageCalendar with data: {data}")

    @property
    def name(self):
        return "Edupage Calendar"

    @property
    def unique_id(self):
        """Return a unique ID for this calendar."""
        return f"edupage_calendar_{self._data.get('subdomain', 'default')}"

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

        _LOGGER.info(f"CALENDAR Fetching events from {start_date} to {end_date}")

        # Prüfen, ob 'timetable' im Coordinator existiert
        timetable = self.coordinator.data.get("timetable")
        if not timetable:
            _LOGGER.warning("CALENDAR Timetable data is missing.")
            return events

        # Iteriere über alle Tage im Zeitraum
        current_date = start_date.date()
        while current_date <= end_date.date():
            day_timetable = timetable.get(current_date)
            if day_timetable and day_timetable.lessons:
                # Iteriere über alle Lektionen des Tages
                for lesson in day_timetable.lessons:
                    start = datetime.combine(current_date, lesson.start_time).replace(tzinfo=local_tz)
                    end = datetime.combine(current_date, lesson.end_time).replace(tzinfo=local_tz)

                    # Generiere CalendarEvent
                    events.append(
                        CalendarEvent(
                            start=start,
                            end=end,
                            summary=lesson.subject.name if lesson.subject else "Unbekanntes Fach",
                            description=(
                                f"Lehrer: {', '.join([t.name for t in lesson.teachers])} | "
                                f"Raum: {', '.join([c.name for c in (lesson.classrooms or [])])}"
                                if lesson.teachers and lesson.classrooms
                                else "Keine Details verfügbar"
                            ),
                        )
                    )
            else:
                _LOGGER.debug(f"CALENDAR No lessons found for {current_date}")

            # Gehe zum nächsten Tag
            current_date += timedelta(days=1)

        _LOGGER.info(f"CALENDAR Fetched {len(events)} events from {start_date} to {end_date}")
        return events
