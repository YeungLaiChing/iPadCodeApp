from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import json
import csv
import threading
from datetime import datetime, timezone, timedelta
from websocket import WebSocketApp
import time
import redis
import os
from pathlib import Path

redis_host=os.environ.get('REDIS_HOST', '192.168.0.3')
redis_port=int(os.environ.get('REDIS_PORT', '6379'))
product_ids=os.environ.get('PROD_ID', "BTC-USD")
crypto_asset=os.environ.get('CRYPTO_ASSET','BTC')
exchange_name=os.environ.get('EXCHANGE_NAME','cexio')

rds = redis.Redis(host=redis_host, port=redis_port, db=0,decode_responses=True)


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
        
        if data['e']=='tradeUpdate':
           
            original_timestamp = data['data']['dateISO']
            utc_datetime = datetime.strptime(original_timestamp,'%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc)
            unix_timestamp=int(utc_datetime.timestamp())
            hkt=timezone(timedelta(hours=8))
            hkt_datetime=utc_datetime.astimezone(hkt)
            hkt_timestamp=hkt_datetime.strftime('%Y-%m-%d %H:%M:%S')
            trade_id=data['data']['tradeId']
            last_price=data['data']['price']
            last_quantity=data['data']['amount']
            side='U'
            if str(data['data']['side']) == 'BUY':
                side='B'
            if str(data['data']['side']) == 'SELL':
                side='S'
            data_row=[original_timestamp,unix_timestamp,hkt_timestamp,trade_id,last_price,last_quantity]
            payload={
                'exchange':'cexio',
                'timestamp_hrs':int(unix_timestamp/3600)*3600,
                'timestamp':unix_timestamp,
                'timestamp_org':original_timestamp,
                'timestamp_hkt':hkt_timestamp,
                'timestamp_recv':time.time(),
                'trade_id':trade_id,
                'side':side,
                'from_symbol':'BTC',
                'to_symbol':'USD',
                'price':last_price,
                'volume':last_quantity,
                'source':'WebSocket'
            }
            rds.publish(ccix_data_channel,json.dumps(payload))
            global file_list
            partition=get_date_partition(unix_timestamp)
            if partition not in file_list:
                file_list[partition]=f"{get_path_by_time(unix_timestamp)}/{file_name}"
                setup_csv_file(file_list[partition])
                
            write_to_csv(file_list[partition],data_row)
            print(f"saved data to csv: {data_row}")
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
    except IOError as e:
        print(f"IOError: {e}")
    
def on_message(ws,message):
    #print("received a message")
    threading.Thread(target=process_message, args=(message,)).start()
    
def on_error(ws,error):
    print(f"Encountereed an error :{error}")
    
def on_close(ws,close_status_code,close_msg):
    print(f"closed connection.code={close_status_code}.msg={close_msg}")
    
def on_ping(ws,msg):
    
    print(f"A pong reply has already been automatically sent.")    

def on_pong(ws,msg):
    print(f"Got a pong msg={msg}. ")    
    
def on_open(ws):
    subscribe_message = json.dumps({
        "e": "trade_subscribe",
        "oid": "72955210375_trade_subscribe",
        "data": {
            "pair": product_ids
        }
    })
    ws.send(subscribe_message)
    print("sent subscribe")

def setup_csv_file(csv_file_path):
    with open(csv_file_path,mode='a',newline='') as file:
        if file.tell() == 0:
            csv_writer=csv.writer(file)
            csv_writer.writerow(['timestamp','unit_ts','hkt','tradeid','price','quantity'])
            
def trigger_job(ws):
    #print('trigger_job in fixed interval')
    pingPayload=json.dumps({"e":"ping"})
    ws.send(pingPayload)
    
                
def get_data():
    now=time.time()
    global file_list
    file_list[get_date_partition(now)]=f"{get_path_by_time(now)}/{file_name}"
    setup_csv_file(file_list[get_date_partition(now)])
    ws=WebSocketApp("wss://trade.cex.io/api/spot/ws-public",
                    on_open=on_open,
                    on_message=on_message,
                    on_error=on_error,
                    on_ping=on_ping,
                    on_pong=on_pong,
                    on_close=on_close)
    
    
    sched = BackgroundScheduler(timezone='UTC')
    
    trigger = CronTrigger(
        year="*", month="*", day="*", hour="*", minute="*", second="0,5,10,15,20,25,30,35,40,45,50,55"
    )
    sched.add_job(
        trigger_job,
        trigger=trigger,
        args=[ws],
        name="trigger job",
    )  
    #sched.add_job(job2,'interval',id='2_sec',seconds=15)
    time.sleep(5)
    sched.start()
    
    ws.run_forever()
    
    
if __name__ == "__main__":
    get_data()
    