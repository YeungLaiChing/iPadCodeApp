import json
import csv
import threading
from datetime import datetime, timezone, timedelta
from websocket import WebSocketApp
import time
import redis
rds = redis.Redis(host='192.168.0.9', port=6379, db=0,decode_responses=True)
ccix_data_channel='ccix_itbit_btc_data_channel'
csv_file_path='./data/itbit_btc.csv'


lock=threading.Lock()

def write_to_csv(data_row):
    with lock:
        with open(csv_file_path,mode='a', newline='') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(data_row)
            

def process_message(message):
    try:
        data = json.loads(message)
        if data['price'] :
            original_timestamp = data['executed_at']
            #utc_datetime = datetime.fromisoformat(original_timestamp.rstrip('Z'))
            utc_datetime = datetime.strptime(original_timestamp,'%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc)
            unix_timestamp=int(utc_datetime.timestamp())
            hkt=timezone(timedelta(hours=8))
            hkt_datetime=utc_datetime.astimezone(hkt)
            hkt_timestamp=hkt_datetime.strftime('%Y-%m-%d %H:%M:%S')
            trade_id=data['match_number']
            last_price=data['price']
            last_quantity=data['amount']
            data_row=[original_timestamp,unix_timestamp,hkt_timestamp,trade_id,last_price,last_quantity]
            payload={
                'exchange':'itbit',
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
    

def setup_csv_file():
    with open(csv_file_path,mode='a',newline='') as file:
        if file.tell() == 0:
            csv_writer=csv.writer(file)
            csv_writer.writerow(['timestamp','unit_ts','hkt','tradeid','price','quantity'])
            
def get_data():
    setup_csv_file()
    ws=WebSocketApp("wss://ws.paxos.com/executiondata/BTCUSD",
                    on_message=on_message,
                    on_error=on_error,
                    on_close=on_close)
    ws.run_forever()
    
if __name__ == "__main__":
    get_data()
    