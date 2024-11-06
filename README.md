# homeassistantedupage
An HomeAssistant integration of the EduPage Schooling System based on the edupage_api library found here https://github.com/EdupageAPI/edupage-api

## Installation without HACS
* Extract files in /custom_components/homeassistantedupage to your installation.
* restart Home Assistant
* Add new integration and search for "Edupage"
* enter Username, Password and Subdomain (w/o ".edupage.org")
* based on your subjects you should find more or less sensors now, named bei the subject with grade-counts
* data is to be found as "attributes", see screenshot

## Installation with HACS
* open HACS
* click 3 dots upper right corner
* select "custom repositories" or something similar
* enter repository URL [https://github.com/rine77/homeassistantedupage](https://github.com/rine77/homeassistantedupage)
* type "integration"
* add
* choose download
* please alway select at least a release with "HACS" in releasename
* restart HA
* add integration
* look for "edupage"
* use "homeassistantedupage" integration
* enter login, password und (ONLY!) subdomain (no .edupage.com or something)
* if there are grades in your account there should spawn one ore more entities

![screenshot of sensors](./img/edupage_subjects_grades.jpg)

![screenshot of sensor with attributes](./img/edupage_subjects_grades_attribues.jpg)
