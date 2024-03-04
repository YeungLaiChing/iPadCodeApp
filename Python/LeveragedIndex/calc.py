import redis
import time
from datetime import datetime
import json
from pathlib import Path
file_path = Path(__file__).with_name("config.json")

f = open (file_path, "r")
hs_tech_leverage_index_config = json.loads(f.read())
f.close()


def calculateLeveragedIndex(underly_index_current):
    result=0
    
    K=float(hs_tech_leverage_index_config["leverage_ratio"])
    DayCount=float(hs_tech_leverage_index_config["number_calendar_days"])
    N=float(365)
    StampDuty=float(hs_tech_leverage_index_config["stamp_duty_pct"])
    Interest=float(hs_tech_leverage_index_config["overnight_interest_pct"])
    UnderlyIndexClose=float(hs_tech_leverage_index_config["underly_index_previous"])
    IndexClose=float(hs_tech_leverage_index_config["this_index_previous"])
    UnderlyIndexCode=hs_tech_leverage_index_config["underly_index_code"]
    
    AmplifiedReturn = K * (underly_index_current / UnderlyIndexClose -1 )
    InterestExpense=(K-1)*(Interest/100/N)*DayCount
    StampDutyExpense = K * (K-1) * abs(underly_index_current / UnderlyIndexClose -1)*(StampDuty/100)
    LeveragedIndexReturn = AmplifiedReturn - InterestExpense - StampDutyExpense
    CurrentIndex  = round(IndexClose * (1 + LeveragedIndexReturn),2)
    return CurrentIndex

def calculateLeveragedIndex2(underly_index_current):
    result=0
    
    K=float(hs_tech_leverage_index_config["leverage_ratio"])
    DayCount=float(hs_tech_leverage_index_config["number_calendar_days"])
    N=float(365)
    StampDuty=float(hs_tech_leverage_index_config["stamp_duty_pct"])
    Interest=float(hs_tech_leverage_index_config["overnight_interest_pct"])
    UnderlyIndexClose=float(hs_tech_leverage_index_config["underly_index_previous"])
    IndexClose=float(hs_tech_leverage_index_config["this_index_previous"])
    UnderlyIndexCode=hs_tech_leverage_index_config["underly_index_code"]
    
    AmplifiedReturn = round(K * round(round(underly_index_current / UnderlyIndexClose,9) -1 ,9),9)
    InterestExpense=round(round((K-1)*round(Interest/100/N,9),9)*DayCount,9)
    StampDutyExpense = round(round(K * (K-1),9) * abs(round(round(underly_index_current / UnderlyIndexClose,9) -1,9))*(StampDuty/100),9)
    LeveragedIndexReturn = AmplifiedReturn - InterestExpense - StampDutyExpense
    CurrentIndex  = round(IndexClose * (1 + LeveragedIndexReturn),2)
    return CurrentIndex

def getFormattedTime(ns):
    dt = datetime.fromtimestamp(ns//1000000000)
    formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
    nanoseconds_part = str(int(ns % 1_000_000_000)).zfill(9)
    formatted_time += '.' + nanoseconds_part
    return formatted_time

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
mobile.subscribe('index_capture_stream')
 
# .listen() returns a generator over which you can iterate and listen for messages from publisher

#for message in mobile.listen():
while True:
    message = mobile.get_message()
    if message:
        current=time.time_ns()
        if message['data']!=1 :
            payload=json.loads(message['data'])
            code=payload['code']
            ns=int(payload['ns']) # <-- you can literally do any thing with this message i am just printing it
            diff_ns=current-ns
            diff_ms=diff_ns / 1000000
            if code == hs_tech_leverage_index_config["underly_index_code"]:
                price=payload['last_price']
                result=calculateLeveragedIndex(price)
                print(f"{payload['data_time']} : {payload['code']} = {payload['last_price']} , index = {result}. Captured @ {getFormattedTime(ns)}. Processed @ {diff_ms} ms")
    
