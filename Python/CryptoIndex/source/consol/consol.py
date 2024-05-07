import time
import redis
import sys
from datetime import datetime, timezone,date
import json
from decimal import Decimal
import csv
from pathlib import Path

import os
redis_host=os.environ.get('REDIS_HOST', '192.168.0.3')
redis_port=int(os.environ.get('REDIS_PORT', '6379'))

crypto_asset=os.environ.get('CRYPTO_ASSET','BTC')
exchange_name=os.environ.get('EXCHANGE_NAME','bitfinex')

csv_file_path=f'./data/{exchange_name.lower()}_{crypto_asset.lower()}.csv'
ccix_from_data_channel=f'ccix_{exchange_name.lower()}_{crypto_asset.lower()}_data_channel'
ccix_consol_data_channel=f'ccix_{crypto_asset.lower()}_data_channel'


data_path="./data/"

def get_path_by_time(now):
    folder_partition=get_date_partition(now)
    path=f"{data_path}/{folder_partition}"
    Path(path).mkdir(parents=True, exist_ok=True)
    return path

def setup_csv_file(csv_file_path):
    with open(csv_file_path,mode='a',newline='') as file:
        if file.tell() == 0:
            csv_writer=csv.writer(file)
            csv_writer.writerow(['unit_ts','hkt','tradeid','side','price','quantity'])
            
def write_to_csv(csv_file_path,data_row):
    with open(csv_file_path,mode='a', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(data_row)
        
def get_table_partition(input):
    return int(input/3600)*3600

def get_date_partition(input):
    #return f"GMT{int(input/24/3600)*24*3600-8*3600}"
    return f"{datetime.fromtimestamp(int(input+16*3600), tz=timezone.utc).strftime('%Y%m%d')}"
               

def get_current_time():
    return datetime.fromtimestamp(int(time.time()+8*3600), tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

def endprocess():
    print(f"{get_current_time()}: end process()! ")
    return "OK"

def main_process(exchange,rds):
    now=time.time()
    file_list={}
    
    file_name=f"{exchange}_{crypto_asset.lower()}_{get_table_partition(now)}.csv"
    file_list[str(get_table_partition(now))]=f"{get_path_by_time(now)}/{file_name}"
    setup_csv_file(file_list[str(get_table_partition(now))])
    

    mobile = rds.pubsub()
    mobile.subscribe(ccix_from_data_channel)
    print(f"{get_current_time()}: already subscribed channel {ccix_from_data_channel}")
    
    while True:
        message = mobile.get_message(timeout=5)
        if message:
            current=time.time_ns()
            if message['data']=="SHUTDOWN":
                endprocess()
                exit()
            if message['data']!=1 :
                payload=json.loads(message['data'],parse_float=Decimal)
                price=float(payload["price"])
                volume=float(payload["volume"])
                hr=payload["timestamp_hrs"]
                exchange=payload["exchange"]
                acc_vol=volume;  
                #key=f"{payload['exchange']}_{payload['timestamp_org']}_{payload['from_symbol']}_{payload['to_symbol']}_{payload['side']}_{payload['trade_id']}_{float(payload['price'])}_{float(payload['volume'])}"
                
                key=f"{payload['exchange']}_{payload['timestamp']}_{payload['from_symbol']}_{payload['to_symbol']}_{payload['trade_id']}_{float(payload['price'])}_{float(payload['volume'])}"
                print(key)
                if rds.setnx(key,"1"):
                    rds.expire(key,3600*24)
                    if rds.hget(hr,exchange) :
                        acc_vol=volume+float(rds.hget(hr,exchange))
                    rds.hset(hr,exchange,acc_vol)
                    
                    rds.hset(payload['from_symbol'],exchange,f"{str(payload['timestamp'])}@{price}")
                    rds.publish(ccix_consol_data_channel,message['data'])
                    if str(hr) not in file_list:
                        file_name=f"{exchange}_{crypto_asset.lower()}_{hr}.csv"
                        file_list[str(hr)]=f"{get_path_by_time(hr)}/{file_name}"
                        setup_csv_file(file_list[str(hr)])
                    # csv_writer.writerow(['unit_ts','tradeid','side','price','quantity'])
                    data_row=[payload['timestamp'],payload['timestamp_hkt'],payload['trade_id'],payload['side'],payload['price'],payload['volume']]
                    write_to_csv(file_list[str(hr)],data_row)
                else:
                    rds.publish("duplicated_data_channel",message['data'])

if __name__ == "__main__":
    
    rds = redis.Redis(host=redis_host,port=redis_port, db=0,decode_responses=True)

    main_process(exchange=exchange_name,rds=rds)