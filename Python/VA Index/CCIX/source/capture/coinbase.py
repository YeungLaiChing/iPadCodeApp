import json
import csv
import threading
import time
from datetime import datetime, timezone, timedelta
from websocket import WebSocketApp

import redis
rds = redis.Redis(host='localhost', port=6379, db=0,decode_responses=True)
csv_file_path='./data/coinbase_btc.csv'
ccix_data_channel='ccix_coinbase_btc_data_channel'


lock=threading.Lock()

def write_to_csv(data_row):
    with lock:
        with open(csv_file_path,mode='a', newline='') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(data_row)
            

def process_message(message):
    try:
        data = json.loads(message)
        if data['type'] == 'ticker':
            original_timestamp = data['time']
            utc_datetime = datetime.strptime(original_timestamp,'%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc)
            unix_timestamp=int(utc_datetime.timestamp())
            hkt=timezone(timedelta(hours=8))
            hkt_datetime=utc_datetime.astimezone(hkt)
            hkt_timestamp=hkt_datetime.strftime('%Y-%m-%d %H:%M:%S')
            trade_id=data['trade_id']
            last_price=data['price']
            last_quantity=data['last_size']
            side='U'
            if str(data['side']) == 'buy':
                side='B'
            if str(data['side']) == 'sell':
                side='S'
            data_row=[original_timestamp,unix_timestamp,hkt_timestamp,trade_id,last_price,last_quantity]
            payload={
                'exchange':'coinbase',
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
                'volume':last_quantity
            }
            rds.publish(ccix_data_channel,json.dumps(payload))
            write_to_csv(data_row )
            #print(f"saved data to csv: {data_row}")
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
    if msg=='hello':
        print(f"Got a ping msg={msg}. A pong reply has already been automatically sent.")    

def on_pong(ws,msg):
    if msg=='hello':
        print(f"Got a pong msg={msg}. No need to respond")

    
def on_open(ws):
    subscribe_message = json.dumps({
        "type": "subscribe",
        "product_ids": ["BTC-USD"],
        "channels": ["ticker"]
    })
    ws.send(subscribe_message)
    print("sent subscribe")

def setup_csv_file():
    with open(csv_file_path,mode='a',newline='') as file:
        if file.tell() == 0:
            csv_writer=csv.writer(file)
            csv_writer.writerow(['timestamp','unit_ts','hkt','tradeid','price','quantity'])
            
def get_coinbase_data():
    setup_csv_file()
    ws=WebSocketApp("wss://ws-feed.pro.coinbase.com",
                    on_open=on_open,
                    on_message=on_message,
                    on_ping=on_ping,
                    on_pong=on_pong,
                    on_error=on_error,
                    on_close=on_close)
    ws.run_forever(ping_interval=60, ping_timeout=10, ping_payload="PING")
    
if __name__ == "__main__":
    get_coinbase_data()
    