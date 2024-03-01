import json
import csv
import threading
from datetime import datetime, timezone, timedelta
from websocket import WebSocketApp

csv_file_path='./coinbase_btc.csv'

lock=threading.Lock()

def write_to_csv(data_row):
    with lock:
        with open(csv_file_path,mode='a', newline='') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(data_row)
            

def process_message(message):
    print(message)
    
def on_message(ws,message):
    print("received a message")
    threading.Thread(target=process_message, args=(message,)).start()
    
def on_error(ws,error):
    print(f"Encountereed an error :{error}")
    
def on_close(ws,close_status_code,close_msg):
    print("closed connection")
    
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
                    on_error=on_error,
                    on_close=on_close)
    ws.run_forever()
    
if __name__ == "__main__":
    get_coinbase_data()
    