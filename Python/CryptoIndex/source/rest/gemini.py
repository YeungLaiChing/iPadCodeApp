import json
import csv
import threading
from datetime import datetime, timezone, timedelta
import requests
import time
import redis
import os

redis_host=os.environ.get('REDIS_HOST', '192.168.0.3')
redis_port=int(os.environ.get('REDIS_PORT', '6379'))
product_ids=os.environ.get('PROD_ID', 'BTCUSD')
crypto_asset=os.environ.get('CRYPTO_ASSET','BTC')
exchange_name=os.environ.get('EXCHANGE_NAME','gemini')

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
            

def process_message(message,last):
    last_id=last
    try:
         for data in message:
            original_timestamp = data['timestamp']
            if int(original_timestamp) > int(last_id):
                last_id=original_timestamp
            utc_datetime = datetime.fromtimestamp(int(original_timestamp), tz=timezone.utc)
            #utc_datetime = datetime.fromisoformat(original_timestamp.rstrip('Z'))
            #utc_datetime = datetime.strptime(original_timestamp,'%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc)
            #utc_datetime = datetime.strptime(original_timestamp[0:19],'%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone.utc)
            unix_timestamp=int(utc_datetime.timestamp())
            hkt=timezone(timedelta(hours=8))
            hkt_datetime=utc_datetime.astimezone(hkt)
            hkt_timestamp=hkt_datetime.strftime('%Y-%m-%d %H:%M:%S')
            trade_id=data['tid']
            last_price=data['price']
            last_quantity=data['amount']
            side='U'
            if data['type']=='buy':
                side='B'
            if data['type']=='sell':
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
                'volume':last_quantity,
                'source':'REST'
            }
            rds.publish(ccix_data_channel,json.dumps(payload))
            #write_to_csv(data_row )
            #print(f"saved data to csv: {data_row}")
    except json.JSONDecodeError as e:
        print(f"{get_current_time()}: JSON decode error: {e}")
    except IOError as e:
        print(f"{get_current_time()}: IOError: {e}")
    return last_id

def setup_csv_file():
    with open(csv_file_path,mode='a',newline='') as file:
        if file.tell() == 0:
            csv_writer=csv.writer(file)
            csv_writer.writerow(['timestamp','unit_ts','hkt','tradeid','price','quantity'])
            
def get_data():
    setup_csv_file()
    last=0
    
    while True:
        if last==0:
           resp = requests.get(f'https://api.gemini.com/v1/trades/{product_ids}')
        else :
           resp = requests.get(f'https://api.gemini.com/v1/trades/{product_ids}?timestamp={last}')
        if resp.status_code==200 :
            content=resp.json()
            
            last=process_message(content,last)
            time.sleep(60)
        else:
            print(f"Reponse Status error {resp.status_code}")
            
            exit()
    
    
if __name__ == "__main__":
    get_data()
