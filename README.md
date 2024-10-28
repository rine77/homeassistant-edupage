# homeassistant-edupage
An HomeAssistant integration of the EduPage Schooling System based on the edupage_api library found here https://github.com/EdupageAPI/edupage-api

## Installation without HACS
* Extract files in /custom_components/homeassistant-edupage to your installation.
* restart Home Assistant
* Add new integration and search for "Edupage"
* enter Username, Password and Subdomain (w/o ".edupage.org")
* based on your subjects you should find more or less sensors now, named bei the subject with grade-counts
* data is to be found as "attributes", see screenshot

## Installation with HACS
* get HACS up and running
* add custom repository (3 dots upper right corner)
* URL: [https://github.com/rine77/homeassistant-edupage](https://github.com/rine77/homeassistant-edupage)

![screenshot of sensors](./img/edupage_subjects_grades.jpg)

![screenshot of sensor with attributes](./img/edupage_subjects_grades_attribues.jpg)
