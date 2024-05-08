import json
import csv
import threading
from datetime import datetime, timezone, timedelta
import time
import redis

import requests

import os
redis_host=os.environ.get('REDIS_HOST', '192.168.0.3')
redis_port=int(os.environ.get('REDIS_PORT', '6379'))
product_ids=os.environ.get('PROD_ID', "XBTUSD")
crypto_asset=os.environ.get('CRYPTO_ASSET','BTC')
exchange_name=os.environ.get('EXCHANGE_NAME','kraken')

rds = redis.Redis(host=redis_host, port=redis_port, db=0,decode_responses=True)


csv_file_path=f'./data/{exchange_name.lower()}_{crypto_asset.lower()}.csv'
ccix_data_channel=f'ccix_{exchange_name.lower()}_{crypto_asset.lower()}_data_channel'

lock=threading.Lock()
def get_current_time():
    return datetime.fromtimestamp(int(time.time()+8*3600), tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

def write_to_csv(data_row):
    with lock:
        with open(csv_file_path,mode='a', newline='') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(data_row)
            

def process_message(trades):
    #print("received a message:",trades)
    try:
        #print(trades)
        for data in trades:
            original_timestamp = float(data[2])
            utc_datetime = datetime.fromtimestamp((original_timestamp), tz=timezone.utc)
            unix_timestamp=int(utc_datetime.timestamp())
            hkt=timezone(timedelta(hours=8))
            hkt_datetime=utc_datetime.astimezone(hkt)
            hkt_timestamp=hkt_datetime.strftime('%Y-%m-%d %H:%M:%S')
            trade_id=data[6]
            last_price=data[0]
            last_quantity=data[1]
            side='U'
            if str(data[3]) == 'b':
                side='B'
            if str(data[3]) == 's':
                side='S'
            data_row=[original_timestamp,unix_timestamp,hkt_timestamp,trade_id,last_price,last_quantity]
            payload={
                'exchange':exchange_name.lower(),
                'timestamp_hrs':int(unix_timestamp/3600)*3600,
                'timestamp':unix_timestamp,
                'timestamp_org':original_timestamp,
                'timestamp_hkt':hkt_timestamp,
                'timestamp_recv':time.time(),
                'trade_id':trade_id,
                'side':side,
                'from_symbol':crypto_asset.upper(),
                'to_symbol':'USD',
                'price':last_price,
                'volume':last_quantity
            }
            rds.publish(ccix_data_channel,json.dumps(payload))
            write_to_csv(data_row )
            #print(f"saved data to csv: {data_row}")
    except json.JSONDecodeError as e:
        print(f"{get_current_time()}: JSON decode error: {e}")
    except IOError as e:
        print(f"{get_current_time()}: IOError: {e}")

def setup_csv_file():
    with open(csv_file_path,mode='a',newline='') as file:
        if file.tell() == 0:
            csv_writer=csv.writer(file)
            csv_writer.writerow(['timestamp','unit_ts','hkt','tradeid','price','quantity'])
            
def get_data():
    setup_csv_file()
    last=0
    print(f"X{product_ids[0:3]}Z{product_ids[3:6]}")
    while True:
        if last==0:
            resp = requests.get(f'https://api.kraken.com/0/public/Trades?pair={product_ids}')
        else:
            resp = requests.get(f'https://api.kraken.com/0/public/Trades?pair={product_ids}&since={last}')
        if resp.status_code==200 :
            content=resp.json()
            
            if len(content["error"])==0:
                process_message(content["result"][f"X{product_ids[0:3]}Z{product_ids[3:6]}"])
                last=content["result"]["last"]
            else:
                #print(f"Returned error {content["error"][0]}")
                exit()
            time.sleep(60)
        else:
            print(f"Reponse Status error {resp.status_code}")
            exit()
        
    
if __name__ == "__main__":
    get_data()
    