import json
import csv
import threading
from datetime import datetime, timezone, timedelta
from websocket import WebSocketApp
import time
csv_file_path='./kraken_btc.csv'

lock=threading.Lock()

def write_to_csv(data_row):
    with lock:
        with open(csv_file_path,mode='a', newline='') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(data_row)
            

def process_message(message):
    print("received a message:",message)
    try:
        trade_data = json.loads(message)
        if isinstance(trade_data,list) and trade_data[2] == 'trade':
            trades = trade_data[1]
            for data in trades:
                original_timestamp = float(data[2])
                utc_datetime = datetime.fromtimestamp((original_timestamp), tz=timezone.utc)
                unix_timestamp=int(utc_datetime.timestamp())
                hkt=timezone(timedelta(hours=8))
                hkt_datetime=utc_datetime.astimezone(hkt)
                hkt_timestamp=hkt_datetime.strftime('%Y-%m-%d %H:%M:%S')
                trade_id=str(time.time_ns())
                last_price=data[0]
                last_quantity=data[1]
                data_row=[original_timestamp,unix_timestamp,hkt_timestamp,trade_id,last_price,last_quantity]
                write_to_csv(data_row )
                print(f"saved data to csv: {data_row}")
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
    except IOError as e:
        print(f"IOError: {e}")
    
def on_message(ws,message):
    print("received a message")
    threading.Thread(target=process_message, args=(message,)).start()
    
def on_error(ws,error):
    print(f"Encountereed an error :{error}")
    
def on_close(ws,close_status_code,close_msg):
    print("closed connection")
    
def on_open(ws):
    subscribe_message = json.dumps({
        "event": "subscribe",
        "pair": ["XBT/USD"],
        "subscription": {
            "name": "trade"
        }
    })
    ws.send(subscribe_message)
    print("sent subscribe")

def setup_csv_file():
    with open(csv_file_path,mode='a',newline='') as file:
        if file.tell() == 0:
            csv_writer=csv.writer(file)
            csv_writer.writerow(['timestamp','unit_ts','hkt','tradeid','price','quantity'])
            
def get_data():
    setup_csv_file()
    ws=WebSocketApp("wss://ws.kraken.com/",
                    on_open=on_open,
                    on_message=on_message,
                    on_error=on_error,
                    on_close=on_close)
    ws.run_forever()
    
if __name__ == "__main__":
    get_data()
    