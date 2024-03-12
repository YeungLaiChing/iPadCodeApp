import redis
import time
from datetime import datetime
import json
from pathlib import Path
import logging.config
from datetime import date, timedelta
import requests
import pandas as pd



from pathlib import Path
file_path = Path(__file__).with_name("config.json")
f = open (file_path, "r")
index_config = json.loads(f.read())
f.close()

topic_name="mv_capture_stream"

date_format = "%Y-%m-%d"

# create logger with 'spam_application'
logger = logging.getLogger('calc.application')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler(f"calc.{time.strftime('%Y%m%d_%H%M%S')}.log")
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)

logger.info(index_config)

DayCount=(datetime.today()-datetime.strptime(index_config["last_calc_date"], date_format)).days
if DayCount==0:
    logger.info("Cannot restart after upagain")
    exit()

if date.today().strftime('%Y-%m-%d') in index_config["holiday_list"] :
    logger.info("Today is holiday")
    exit()

df=pd.DataFrame.from_dict((index_config["list"]),orient="index")
df[["cf", "faf","is","pre_close"]] = df[["cf", "faf","is","pre_close"]].apply(pd.to_numeric)
df["wgt"]=(df["cf"]*df["faf"]*df["is"]).astype(int)
df["price"]=df["pre_close"]
df["stock_cap_mv"]=(df["price"]*df["wgt"]).astype(int)
current_index_mv=df['stock_cap_mv'].sum()
yest_index_mv=int(index_config["yest_mv"])
yest_index_value=float(index_config["yest_index"])
divisor=float(index_config["divisor"])
current_index_value=0



r = redis.Redis(
    host='192.168.0.5',
    port=6379,
    decode_responses=True
)

#for message in mobile.listen():
r=json.loads(r.get('HK.00700_quote'))
print(r['last_price'])    
    