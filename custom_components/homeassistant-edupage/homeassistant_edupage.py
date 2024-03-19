from edupage_api import Edupage as APIEdupage

class Edupage:
    def __init__(self):
        self.api = APIEdupage()

    def login(self, username, password, subdomain):
        """login to website"""
        # giving credentials directly
        return self.api.login(username, password, subdomain)

    async def async_update(self):
        """update data"""
        # polling for new data here
        pass
