from datetime import datetime, timezone,date
import time

now=1714809600

hk = datetime.fromtimestamp(int(now+8*3600), tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
target = datetime.fromtimestamp(int(now+16*3600), tz=timezone.utc).strftime('%Y%m%d')


print(hk)
print(target)