# homeassistantedupage
An HomeAssistant integration of the EduPage Schooling System based on the edupage_api library found here https://github.com/EdupageAPI/edupage-api

# IMPORTANT
In this phase of development please remove integration after update and reinstall because there are major changes.

## Installation with HACS
* open HACS
* click 3 dots upper right corner
* select "custom repositories" or something similar
* enter repository URL [https://github.com/rine77/homeassistantedupage](https://github.com/rine77/homeassistantedupage)
* type "integration"
* add
* choose download
* please alway select the last one because its work in progress
* restart HA
* add integration
* look for "edupage" with the nice "E" icon
* use "homeassistantedupage" integration
* enter login, password und (ONLY!) subdomain (no .edupage.com or something)
* now you have to choose the student you want to bind sensors and calendar on
* there will be a lot of sensors, each for the subject of your school
* those subjects with grades have grades as attributes
* furthermore there will be a calendar per student with timetable
* fetched data for timetable is 14 days ahead