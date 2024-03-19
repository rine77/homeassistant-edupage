from edupage_api import Edupage as APIEdupage

class Edupage:
    def __init__(self,hass):
        self.hass = hass
        self.api = APIEdupage()

    def login(self, username, password, subdomain):

        return self.api.login(username, password, subdomain)

    async def get_grades(self):

        grades = await self.hass.async_add_executor_job(self.api.get_grades)
        return grades

    async def async_update(self):

        pass
