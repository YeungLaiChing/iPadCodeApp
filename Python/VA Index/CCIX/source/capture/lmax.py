import json
import csv
import threading
from datetime import datetime, timezone, timedelta
from websocket import WebSocketApp
import time
import redis
rds = redis.Redis(host='localhost', port=6379, db=0,decode_responses=True)
ccix_data_channel='ccix_lmax_btc_data_channel'
csv_file_path='./data/lmax_btc.csv'


lock=threading.Lock()
def get_current_time():
    return datetime.fromtimestamp(int(time.time()+8*3600), tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

def write_to_csv(data_row):
    with lock:
        with open(csv_file_path,mode='a', newline='') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(data_row)
            

def process_message(message):
    try:
        data = json.loads(message)
        if data['type'] == 'TICKER':
            original_timestamp = data['timestamp']
            utc_datetime = datetime.fromisoformat(original_timestamp.rstrip('Z')).replace(tzinfo=timezone.utc)
            unix_timestamp=int(utc_datetime.timestamp())
            hkt=timezone(timedelta(hours=8))
            hkt_datetime=utc_datetime.astimezone(hkt)
            hkt_timestamp=hkt_datetime.strftime('%Y-%m-%d %H:%M:%S')
            trade_id=data['trade_id']
            last_price=data['last_price']
            last_quantity=data['last_quantity']
            data_row=[original_timestamp,unix_timestamp,hkt_timestamp,trade_id,last_price,last_quantity]
            payload={
                'exchange':'lmax',
                'timestamp_hrs':int(unix_timestamp/3600)*3600,
                'timestamp':unix_timestamp,
                'timestamp_org':original_timestamp,
                'timestamp_hkt':hkt_timestamp,
                'timestamp_recv':time.time(),
                'trade_id':trade_id,
                'side':'U',
                'from_symbol':'BTC',
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
    
def on_message(ws,message):
    #print("received a message")
    threading.Thread(target=process_message, args=(message,)).start()
    
def on_error(ws,error):
    print(f"{get_current_time()}: Encountereed an error :{error}")
    
def on_close(ws,close_status_code,close_msg):
    print(f"{get_current_time()}: closed connection.code={close_status_code}.msg={close_msg}")
    
def on_ping(ws,msg):
    print(f"{get_current_time()}: Got a ping msg={msg}. A pong reply has already been automatically sent.")    

def on_pong(ws,msg):
    print(f"{get_current_time()}: Got a pong msg={msg}. No need to respond")
    
def on_open(ws):
    subscribe_message = json.dumps({
        "type": "SUBSCRIBE",
        "channels": [{
            "name": "TICKER",
            "instruments": ["btc-usd"]
        }]
    })
    ws.send(subscribe_message)
    print(f"{get_current_time()}: sent subscribe")

def setup_csv_file():
    with open(csv_file_path,mode='a',newline='') as file:
        if file.tell() == 0:
            csv_writer=csv.writer(file)
            csv_writer.writerow(['timestamp','unit_ts','hkt','tradeid','price','quantity'])
            
def get_data():
    setup_csv_file()
    ws=WebSocketApp("wss://public-data-api.london-digital.lmax.com/v1/web-socket",
                    on_open=on_open,
                    on_message=on_message,
                    on_error=on_error,
                    on_ping=on_ping,
                    on_pong=on_pong,
                    on_close=on_close)
    ws.run_forever(ping_interval=60, ping_timeout=10, ping_payload="PING")
    
if __name__ == "__main__":
    get_data()
    