import requests

from datetime import date, timedelta
target_date = date.today() - timedelta(1)
print (target_date)


resp = requests.get(f'https://www.hkab.org.hk/api/hibor?year={target_date.year}&month={target_date.month}&day={target_date.day}').json()

print(f"{resp["Overnight"]} , {resp["isHoliday"]}")


