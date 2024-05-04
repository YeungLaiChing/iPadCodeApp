import time
import redis
import sys
from datetime import datetime, timezone,date
import json
from decimal import Decimal

def get_current_time():
    return datetime.fromtimestamp(int(time.time()+8*3600), tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

def endprocess():
    print(f"{get_current_time()}: end process()! ")
    return "OK"

def main_process(exchange,rds):

    ccix_from_data_channel=str(f'ccix_{exchange}_btc_data_channel')

    ccix_consol_data_channel='ccix_btc_data_channel'

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
        
                key=f"{payload['exchange']}_{payload['timestamp_org']}_{payload['from_symbol']}_{payload['to_symbol']}_{payload['side']}_{payload['trade_id']}_{payload['price']}_{payload['volume']}"
                #print(key)
                if rds.setnx(key,"1"):
                    rds.expire(key,3600*24)
                    if rds.hget(hr,exchange) :
                        acc_vol=volume+float(rds.hget(hr,exchange))
                    rds.hset(hr,exchange,acc_vol)
                    
                    rds.hset(payload['from_symbol'],exchange,f"{str(payload['timestamp'])}@{price}")
                    rds.publish(ccix_consol_data_channel,message['data'])
                    
                else:
                    rds.publish("duplicated_data_channel",message['data'])

if __name__ == "__main__":
    
    if len(sys.argv) > 1:
        
        file_path=sys.argv[1]
        f = open (file_path, "r")
        config = json.loads(f.read())
        f.close()
        
        exchange = config['exchange_name']
        rds = redis.Redis(
            host=config['redis_ip'], 
            port=config['redis_port'], 
            db=0,
            decode_responses=True)

    else:
        exchange = 'coinbase'
        rds = redis.Redis(host='192.168.0.3', port=6379, db=0,decode_responses=True)

    main_process(exchange=exchange,rds=rds)