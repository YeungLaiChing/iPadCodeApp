from datetime import datetime, timezone, timedelta
import time
import requests
from bs4 import BeautifulSoup
import time
import openpyxl
import pymongo
import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

mongodb_url=os.environ.get('CONFIG_MONGODB_URL', 'mongodb://testing:testing@192.168.0.9:27017/')

client=pymongo.MongoClient(mongodb_url)
db=client["etf_db"]
table=db["etf_ccass_table"]
latest_table=db["etf_latest_ccass_table"]

codes=["03008","09008","03009","09009","03042","83042","09042","03046","83046","09046","03439","09439","03179","09179","03066","03068","03135"]

def extract_content(stock_code,to_date):
    site="https://www3.hkexnews.hk/"
    URL=f"{site}/sdw/search/searchsdw.aspx?__EVENTTARGET=btnSearch&txtShareholdingDate={to_date}&txtStockCode={stock_code}"
    print(URL)
    
    page=requests.get(URL)
    soup=BeautifulSoup(page.content,"html.parser")
    
    search_stock=soup.find(id="txtStockName")

    
    if search_stock.get("value"):

        search_date=soup.find(id="txtShareholdingDate").get("value").replace("/","")
        total_issued_shares=soup.find("div",class_="summary-value").text.replace(",","")
        holdings=soup.find("div",class_="ccass-search-total").find("div",class_="value").text.replace(",","")
        
        print(f"{stock_code} {search_date} {holdings} {total_issued_shares}")
        
        result={
                    "Date":search_date,
                    "Stock":int(stock_code),
                    "Holdings":holdings,
                    "IssuedShares":total_issued_shares
                    
                }
        key={
                    "Date":search_date,
                    "Stock":int(stock_code)
                }
        update_latest_key={
                    "Stock":int(stock_code)
                }
        table.update_many(key,{"$set": result},upsert=True)
        latest_table.update_many(update_latest_key,{"$set": result},upsert=True)
                
    
    else:
        print(f"no search result for {stock_code} for {to_date}")




def trigger_job():
    to_date=datetime.fromtimestamp(int(time.time())).strftime('%Y%m%d')

    for stock in codes:
        extract_content(stock,to_date)
        time.sleep(5)
    

if __name__ == "__main__":
    sched = BackgroundScheduler(
        timezone='UTC',
        job_defaults={'misfire_grace_time': 15*60}
        )
    
    trigger = CronTrigger(
        ### HKT 16,17,19,23,7
        year="*", month="*", day="*", hour="8,9,11,15,23", minute="25", second="0"
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
    