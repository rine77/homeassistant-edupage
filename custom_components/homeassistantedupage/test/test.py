import datetime

from edupage_api import Edupage

edupage = Edupage()
edupage.login_auto("rene@familie-lange.digital", "hXbxb$@$6fhyYMhB")

# My timetable
date = datetime.date(2024, 11, 1)
timetable = edupage.get_my_timetable(date)

print(f"My timetable from {date}:")

print()