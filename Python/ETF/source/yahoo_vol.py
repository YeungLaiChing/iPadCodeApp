import yfinance as yf
from datetime import datetime, timezone, timedelta
import time
import pymongo
import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

mongodb_url=os.environ.get('CONFIG_MONGODB_URL', 'mongodb://testing:testing@192.168.0.9:27017/')

client=pymongo.MongoClient(mongodb_url)

db=client["etf_db"]
table=db["etf_vol_table"]

latest_table=db["etf_latest_vol_table"]

codes=["3008","9008","3009","9009","3042","83042","9042","3046","83046","9046","3439","9439","3179","9179","3066","3068","3135"]


def get_stock_vol(stock_code):
    trade_date=datetime.fromtimestamp(int(time.time())).strftime('%Y%m%d')
    result={
        "Date":trade_date,
        "Stock":stock_code,
        "UpdatedTime":trade_date,
        "Price":0,
        "Vol":0
        
    }
    key={
        "Date":trade_date,
        "Stock":stock_code
    }
    

    #result=table.update_many(key,{"$set": result},upsert=True)    
    
    
    stock = yf.Ticker(f"{stock_code}.HK")
    data=stock.history_metadata
    trade_date=datetime.fromtimestamp(int(data["regularMarketTime"])+8*3600).strftime('%Y%m%d')
    result={
        "Date":trade_date,
        "Stock":stock_code,
        "UpdatedTime":datetime.fromtimestamp(int(data["regularMarketTime"])+8*3600).strftime('%Y%m%d %H:%M:%S'),
        "Price":data["regularMarketPrice"],
        "Vol":data["regularMarketVolume"]
    }
    key={
        "Date":trade_date,
        "Stock":stock_code
    }
    print(result)

    table.update_many(key,{"$set": result},upsert=True)
    update_latest_key={
        "Stock":stock_code
    }
    
    result={
        "Date":trade_date,
        "Stock":stock_code,
        "UpdatedTime":datetime.fromtimestamp(int(data["regularMarketTime"])+8*3600).strftime('%Y%m%d %H:%M:%S'),
        "Price":data["regularMarketPrice"],
        "Vol":data["regularMarketVolume"]
    }
    latest_table.update_many(update_latest_key,{"$set": result},upsert=True)
    

def trigger_job():

    for stock in codes:
        get_stock_vol(stock)
        time.sleep(2)
    

if __name__ == "__main__":
    
    sched = BackgroundScheduler(
        timezone='UTC',
        job_defaults={'misfire_grace_time': 15*60}
        )
        
    trigger = CronTrigger(
        ## HKT 16,17,18,19,23
        year="*", month="*", day="*", hour="8,9,10,11,15", minute="30", second="0"
    )
    sched.add_job(
        trigger_job,
        trigger=trigger,
        args=[],
        name="trigger job",
    )  
    #sched.add_job(job2,'interval',id='2_sec',seconds=15)
    time.sleep(5)
    sched.start()
    while True:
        time.sleep(10000)
    