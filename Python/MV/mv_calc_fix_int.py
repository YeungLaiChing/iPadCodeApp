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

topic_name="Trigger_Index_2s"

date_format = "%Y-%m-%d"

# create logger with 'spam_application'
logger = logging.getLogger('calc.application')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler(f"./log/fix.calc.{time.strftime('%Y%m%d_%H%M%S')}.log")
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


def calcIndexMVByStockChange(stockCode,price):
    global current_index_mv
    global df
    old_stock_mv= df.loc[stockCode,'stock_cap_mv']
    new_stock_mv=int(price*df.loc[stockCode,'wgt'])
    current_index_mv=current_index_mv-old_stock_mv+new_stock_mv
    df.loc[stockCode,'price'] = price
    df.loc[stockCode,'stock_cap_mv']=new_stock_mv
    return current_index_mv
            

def calcIndexMVByAllStock(stockCode,price):
    global current_index_mv
    global df
    df.loc[stockCode,'price'] = price
    df["stock_cap_mv"]=(df["price"]*df["wgt"]).astype(int)
    current_index_mv=df['stock_cap_mv'].sum()
    return current_index_mv
        
            
def calcIndexbyMV(mv):
    global current_index_value
    current_index_value=round(mv / yest_index_mv * yest_index_value,2)
    return current_index_value
        
def calcIndexbyDivisor(mv):
    global current_index_value
    current_index_value=round(mv / divisor,2)
    return current_index_value



        

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
mv=0
name='TECH_Sim_2s'
#for message in mobile.listen():
while True:
    message = mobile.get_message()
    if message:
        current=time.time_ns()
        if message['data']=="SHUTDOWN":
            endprocess()
            exit()
        if message['data']!=1 :
            payload=json.loads(message['data'])
            indexTime=payload['IndexTime']
            ns=int(payload['ns']) # <-- you can literally do any thing with this message i am just printing it
            diff_ns=current-ns
            diff_ms=diff_ns / 1000000
            
            for code in df.index:
                obj=json.loads(r.get(f"{code}_quote"))
                price=float(obj['last_price'])
                if price > 0 and price != df.loc[code,'price'] :
                    mv=calcIndexMVByStockChange(code,price)
                    #mv=calcIndexMVByAllStock(code,price)
            result=calcIndexbyMV(mv)
            output = {'indexName': name, 'exchangeTime' : getFormattedTime(current), 'indexValue' : result}
            r.publish("index-distribution",json.dumps(output))
                    
            logger.info(f"RESULT @ {indexTime}  : Index = {result} . MV = {mv} . trigger at : {getFormattedTime(ns)}. complete at : {getFormattedTime(current)}. Elapse time {diff_ms} ms")
    
    