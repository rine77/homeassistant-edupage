import logging
import voluptuous as vol
from edupage_api import Edupage
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME

_LOGGER = logging.getLogger(__name__)

CONF_SUBDOMAIN = "subdomain"  # Lokal definiert

class EdupageConfigFlow(config_entries.ConfigFlow, domain="homeassistantedupage"):
    """Handle a config flow for Edupage."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            _LOGGER.info("User input received: %s", user_input)
            api = Edupage()

            try:
                # Login ausführen
                _LOGGER.debug("Starting login process")
                await self.hass.async_add_executor_job(
                    api.login, 
                    user_input[CONF_USERNAME],
                    user_input[CONF_PASSWORD],
                    user_input[CONF_SUBDOMAIN]
                )
                _LOGGER.debug("Login successful")

                # Schülerliste abrufen
                students = await self.hass.async_add_executor_job(api.get_students)
                _LOGGER.debug("Students retrieved: %s", students)

                if not students:
                    errors["base"] = "no_students_found"
                else:
                    # Speichere Benutzer-Eingaben
                    self.user_data = user_input
                    self.students = {student.person_id: student.name for student in students}

                    # Weiter zur Schülerauswahl
                    return await self.async_step_select_student()

            except Exception as e:
                _LOGGER.error("Exception during API call: %s", e)
                errors["base"] = "cannot_connect"

        # Formular anzeigen
        data_schema = vol.Schema({
            vol.Required(CONF_USERNAME): str,
            vol.Required(CONF_PASSWORD): str,
            vol.Required(CONF_SUBDOMAIN): str,
        })

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )


    async def async_step_select_student(self, user_input=None):
        """Handle the selection of a student."""
        errors = {}

        if user_input is not None:
            student_id = user_input.get("student")
            _LOGGER.info("Selected student ID: %s", student_id)

            # Erstelle den Config-Entry mit allen Daten
            return self.async_create_entry(
                title=f"Edupage ({self.students[student_id]})",
                data={
                    **self.user_data,  # Login-Daten hinzufügen
                    "student_id": student_id,
                    "student_name": self.students[student_id],
                },
            )

        # Dropdown-Formular für Schülerauswahl
        student_schema = vol.Schema({
            vol.Required("student"): vol.In(self.students),
        })

        return self.async_show_form(
            step_id="select_student",
            data_schema=student_schema,
            errors=errors
        )
