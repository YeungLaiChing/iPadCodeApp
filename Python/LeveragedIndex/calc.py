import redis
import time
from datetime import datetime
import json
from pathlib import Path
import logging.config
from futu import *
from datetime import date, timedelta
import requests


file_path = Path(__file__).with_name("config.json")

f = open (file_path, "r")
hs_tech_leverage_index_config = json.loads(f.read())
f.close()


date_format = "%Y-%m-%d"

# create logger with 'spam_application'
logger = logging.getLogger('calc.application')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler(f"./log/calc.{time.strftime('%Y%m%d_%H%M%S')}.log")
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)


DayCount=(datetime.today()-datetime.strptime(hs_tech_leverage_index_config["last_calc_date"], date_format)).days
if DayCount==0:
    logger.info("Cannot restart after upagain")
    exit()

if date.today().strftime('%Y-%m-%d') in hs_tech_leverage_index_config["holiday_list"] :
    logger.info("Today is holiday")
    exit()
    
def calculateLeveragedIndex(underly_index_current):
    result=0
    
    K=float(hs_tech_leverage_index_config["leverage_ratio"])
    DayCount=float(hs_tech_leverage_index_config["number_calendar_days"])

    DayCount=(datetime.today()-datetime.strptime(hs_tech_leverage_index_config["last_calc_date"], date_format)).days
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
    
    DayCount=(datetime.today()-datetime.strptime(hs_tech_leverage_index_config["last_calc_date"], date_format)).days
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
def endprocess():
    target_date = date.today() 

    resp = requests.get(f'https://www.hkab.org.hk/api/hibor?year={target_date.year}&month={target_date.month}&day={target_date.day}').json()
    hs_tech_leverage_index_config["overnight_interest_pct"]=str(resp["Overnight"]);


    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

    ret_sub, err_message = quote_ctx.subscribe(['HK.800700','HK.800868'], [SubType.QUOTE], subscribe_push=False)
    # Subscribe to the K line type first. After the subscription is successful, Futu OpenD will continue to receive pushes from the server, False means that there is no need to push to the script temporarily
    if ret_sub == RET_OK: # Subscription successful
        ret, data = quote_ctx.get_stock_quote(['HK.800700']) # Get real-time data of subscription stock quotes
        if ret == RET_OK:
            hs_tech_leverage_index_config["underly_index_previous"]=str(data['last_price'][0])
            hs_tech_leverage_index_config["last_calc_date"]=str(data['data_date'][0])
        else:
            print('error:', data)
            
        ret, data = quote_ctx.get_stock_quote(['HK.800868']) # Get real-time data of subscription stock quotes
        if ret == RET_OK:
            hs_tech_leverage_index_config["this_index_previous"]=str(data['last_price'][0])
            hs_tech_leverage_index_config["last_calc_date"]=str(data['data_date'][0])
        else:
            print('error:', data)
    else:
        print('subscription failed', err_message)
    quote_ctx.close() # Close the current connection, Futu OpenD will automatically cancel the corresponding type of subscription for the corresponding stock after 1 minute


    new_file_path = Path(__file__).with_name(f"config.json")
    f = open(new_file_path, 'w', encoding='utf-8')
    json.dump(hs_tech_leverage_index_config, f, ensure_ascii=False, indent=4)
    f.close()

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
mobile.subscribe('index_capture_stream')
 
# .listen() returns a generator over which you can iterate and listen for messages from publisher

#for message in mobile.listen():
processed_time=''
processed_price=''
name='TECH2LSim'
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
            ns=int(payload['ns']) # <-- you can literally do any thing with this message i am just printing it
            diff_ns=current-ns
            diff_ms=diff_ns / 1000000
            if code == hs_tech_leverage_index_config["underly_index_code"]:
                if processed_time != payload['data_time'] or processed_price != payload['last_price'] :
                    price=payload['last_price']
                    result=calculateLeveragedIndex(price)
                    processed_time=payload['data_time']
                    processed_price=payload['last_price']
                    output = {'indexNam': name, 'exchangeTime' : getFormattedTime(current), 'indexValue' : result}
                    r.publish("index-distribution",json.dumps(output))
                    logger.info(f"{payload['data_time']} : {payload['code']} = {payload['last_price']} , index = {result}. Captured @ {getFormattedTime(ns)}. Processed @ {diff_ms} ms")
                    logger.info(f"RESULT @ {payload['data_date']} {payload['data_time']} : index = {result} . Completed @ {getFormattedTime(current)}. Processed @ {diff_ms} ms")
        
    