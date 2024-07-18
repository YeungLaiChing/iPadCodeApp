
import json
import csv
import threading
import time
from datetime import datetime, timezone, timedelta
from websocket import WebSocketApp
import redis
import os
from pathlib import Path


redis_host=os.environ.get('REDIS_HOST', '192.168.0.3')
redis_port=int(os.environ.get('REDIS_PORT', '6379'))
product_id1=os.environ.get('PROD_ID_1', 'HKEXBTC-USD')
product_id2=os.environ.get('PROD_ID_2', 'HKEXETH-USD')
product_id3=os.environ.get('PROD_ID_3', 'HKEXBTC-USD')
product_id4=os.environ.get('PROD_ID_4', 'HKEXETH-USD')
crypto_asset=os.environ.get('CRYPTO_ASSET','CCHKEX')
exchange_name=os.environ.get('EXCHANGE_NAME','CCDATA')

api_key=os.environ.get('APIKEY','1e0f131269d411f25453ad0820d526e937df1a7c1a929ee46f8b2fbf8cd2d387')

#rds = redis.Redis(host=redis_host, port=redis_port, db=0,decode_responses=True)

data_path="./data/"
file_list={}
def get_date_partition(input):
    return f"{datetime.fromtimestamp(int(input+16*3600), tz=timezone.utc).strftime('%Y%m%d')}"
               
def get_path_by_time(now):
    folder_partition=get_date_partition(now)
    path=f"{data_path}/{folder_partition}"
    Path(path).mkdir(parents=True, exist_ok=True)
    return path

file_name=f'{exchange_name.lower()}_{crypto_asset.lower()}.csv'
ccix_data_channel=f'ccix_{exchange_name.lower()}_{crypto_asset.lower()}_data_channel'


lock=threading.Lock()
def get_current_time():
    return datetime.fromtimestamp(int(time.time()+8*3600), tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

def write_to_csv(csv_file_path,data_row):
    with lock:
        with open(csv_file_path,mode='a', newline='') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(data_row)
            

def process_message(message):
    try:
        data = json.loads(message)
        if data['TYPE'] == '1105':
            instrument=data['INSTRUMENT']
            ccseq=data['CCSEQ']
            
            index_value=data['VALUE']
            last_update_qty=data['LAST_UPDATE_QUANTITY']
            last_update_ccseq=data['LAST_UPDATE_CCSEQ']
            current_hour_vol=data['CURRENT_HOUR_VOLUME']
            current_hour_high=data['CURRENT_HOUR_HIGH']
            current_hour_low=data['CURRENT_HOUR_LOW']
            current_hour_change=data['CURRENT_HOUR_CHANGE']
            current_hour_updates=data['CURRENT_HOUR_TOTAL_INDEX_UPDATES']
            moving_24_hour_vol=data['MOVING_24_HOUR_VOLUME']
            moving_24_hour_high=data['MOVING_24_HOUR_HIGH']
            moving_24_hour_low=data['MOVING_24_HOUR_LOW']
            moving_24_hour_change=data['MOVING_24_HOUR_CHANGE']
            moving_24_hour_updates=data['MOVING_24_HOUR_TOTAL_INDEX_UPDATES']
            
            original_timestamp = int(data['VALUE_LAST_UPDATE_TS'])
            utc_datetime = datetime.fromtimestamp(original_timestamp,tz=timezone.utc)
            unix_timestamp=int(utc_datetime.timestamp())
            hkt=timezone(timedelta(hours=8))
            hkt_datetime=utc_datetime.astimezone(hkt)
            hkt_timestamp=hkt_datetime.strftime('%Y-%m-%d %H:%M:%S')
            timestamp_recv = time.time()
            
            data_row=[original_timestamp,unix_timestamp,hkt_timestamp,timestamp_recv,
            instrument,ccseq,index_value,last_update_qty,last_update_ccseq,
            current_hour_high,current_hour_low,current_hour_change,current_hour_updates,
            moving_24_hour_high,moving_24_hour_low,moving_24_hour_change,moving_24_hour_updates]
            
            payload={
                'instrument':instrument,
                'timestamp_hrs':int(unix_timestamp/3600)*3600,
                'timestamp':unix_timestamp,
                'timestamp_org':original_timestamp,
                'timestamp_hkt':hkt_timestamp,
                'timestamp_recv':timestamp_recv,
                'ccseq':ccseq,
                'index_value':index_value
            }
            #rds.publish(ccix_data_channel,json.dumps(payload))
            global file_list
            partition=get_date_partition(unix_timestamp)
            if partition not in file_list:
                file_list[partition]=f"{get_path_by_time(unix_timestamp)}/{file_name}"
                setup_csv_file(file_list[partition])
                
            write_to_csv(file_list[partition],data_row)
            #print(f"saved data to csv: {data_row}")
        else:
            print(data)
    except json.JSONDecodeError as e:
        print(f"{get_current_time()}: JSON decode error: {e}")
    except IOError as e:
        print(f"{get_current_time()}: IOError: {e}")
    
def on_message(ws,message):
    #print("received a message")
    threading.Thread(target=process_message, args=(message,)).start()
    
def on_error(ws,error):
    print(f"{get_current_time()}: Encountereed an error :{error}")
    
def on_close(ws,close_status_code,close_msg):
    print(f"{get_current_time()}: closed connection.code={close_status_code}.msg={close_msg}")
    
def on_ping(ws,msg):
    if msg=='hello':
        print(f"Got a ping msg={msg}. A pong reply has already been automatically sent.")    

def on_pong(ws,msg):
    if msg=='hello':
        print(f"Got a pong msg={msg}. No need to respond")

    
def on_open(ws):
    subscribe_message = json.dumps({
        "action": "SUBSCRIBE",
        "type": "index_cc_v1_latest_tick",
        "groups": ["VALUE","LAST_UPDATE","CURRENT_HOUR","MOVING_24_HOUR"],
        "market": "cchkex",
        "instruments": [product_id1,product_id2,product_id3,product_id4]
    })
    ws.send(subscribe_message)
    print(f"{get_current_time()}: sent subscribe")

def setup_csv_file(csv_file_path):
    with open(csv_file_path,mode='a',newline='') as file:
        if file.tell() == 0:
            csv_writer=csv.writer(file)
            csv_writer.writerow(
            ['timestamp',
            'unit_ts',
            'hkt',
            'recv_ts',
            'instrument',
            'ccseq',
            'index_value',
            'last_update_qty',
            'last_update_ccseq',
            'current_hour_high',
            'current_hour_low','current_hour_change','current_hour_updates',
            'moving_24_hour_high','moving_24_hour_low','moving_24_hour_change',
            'moving_24_hour_updates'])      
def get_ccdata_data():
    now=time.time()
    global file_list
    file_list[get_date_partition(now)]=f"{get_path_by_time(now)}/{file_name}"
    setup_csv_file(file_list[get_date_partition(now)])
   
    ws=WebSocketApp(f"wss://data-streamer.cryptocompare.com/?api_key={api_key}",
                    on_open=on_open,
                    on_message=on_message,
                    on_ping=on_ping,
                    on_pong=on_pong,
                    on_error=on_error,
                    on_close=on_close)
    ws.run_forever(ping_interval=60, ping_timeout=10, ping_payload="PING")
    
if __name__ == "__main__":
    get_ccdata_data()



