import redis
import time
from datetime import datetime
import json
from pathlib import Path
import logging.config
from futu import *
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
fh = logging.FileHandler(f"./log/calc.{time.strftime('%Y%m%d_%H%M%S')}.log")
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)


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
current_index_Value=0


def calcIndexMVByStockChange(stockCode,price):
    old_stock_mv= df.loc[stockCode,'stock_cap_mv']
    new_stock_mv=int(price*df.loc[stockCode,'wgt'])
    current_index_mv=current_index_mv-old_stock_mv+new_stock_mv
    df.loc[stockCode,'price'] = price
    df.loc[stockCode,'stock_cap_mv']=new_stock_mv
    return current_index_mv
            

def calcIndexMVByAllStock(stockCode,price):
    df.loc[stockCode,'price'] = price
    df["stock_cap_mv"]=(df["price"]*df["wgt"]).astype(int)
    current_index_mv=df['stock_cap_mv'].sum()
    return current_index_mv
        
            
def calcIndexbyMV(mv):
    result=0
    result=round(mv / yest_index_mv * yest_index_value,2)
    return result
        
def calcIndexbyDivisor(mv):
    result=0
    result=round(mv / divisor,2)
    return result



        

def getFormattedTime(ns):
    dt = datetime.fromtimestamp(ns//1000000000)
    formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
    nanoseconds_part = str(int(ns % 1_000_000_000)).zfill(9)
    formatted_time += '.' + nanoseconds_part
    return formatted_time

def endprocess():
    target_date = date.today() 

    #new_file_path = Path(__file__).with_name(f"config.json")
    #f = open(new_file_path, 'w', encoding='utf-8')
    #json.dump(index_config, f, ensure_ascii=False, indent=4)
    #f.close()

    return "OK"



r = redis.Redis(
    host='192.168.0.5',
    port=6379,
    decode_responses=True
)

# pubsub() method creates the pubsub object
# but why i named it mobile 🧐
# just kidding 😂 think of it as the waki taki that listens for incomming messages
mobile = r.pubsub()

# use .subscribe() method to subscribe to topic on which you want to listen for messages
mobile.subscribe(topic_name)
 
# .listen() returns a generator over which you can iterate and listen for messages from publisher

#for message in mobile.listen():
processed_time=''
processed_price=''

while True:
    message = mobile.get_message()
    if message:
        current=time.time_ns()
        if message['data']=="SHUTDOWN":
            endprocess()
            exit()
        if message['data']!=1 :
            payload=json.loads(message['data'])
            code=payload['code']
            price=float(payload["last_price"])
            ns=int(payload['ns']) # <-- you can literally do any thing with this message i am just printing it
            diff_ns=current-ns
            diff_ms=diff_ns / 1000000
            
            if code in df.index:
                if price != df.loc[code,'price'] :
                    mv=calcIndexMVByStockChange(code,price)
                    #mv=calcIndexMVByAllStock(code,price)
                    result=calcIndexbyMV(mv)
                    processed_time=payload['data_time']
                    logger.info(f"RESULT @ {payload['data_date']} {payload['data_time']} : index = {result} . Completed @ {getFormattedTime(current)}. Processed @ {diff_ms} ms")
        
    