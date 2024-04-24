import time
import redis
import sys
from datetime import date, timedelta
import json

exchange = ''
if len(sys.argv) > 1:
    exchange=sys.argv[2]
ccix_from_data_channel=f'ccix_{exchange}_btc_data_channel'
ccix_consol_data_channel='ccix_btc_data_channel'

rds = redis.Redis(host='192.168.0.9', port=6379, db=0,decode_responses=True)

mobile = rds.pubsub()
mobile.subscribe(ccix_from_data_channel)
print(f"already subscribed channel {ccix_from_data_channel}")

def endprocess():
    target_date = date.today() 

    #new_file_path = Path(__file__).with_name(f"config.json")
    #f = open(new_file_path, 'w', encoding='utf-8')
    #json.dump(index_config, f, ensure_ascii=False, indent=4)
    #f.close()

    return "OK"

while True:
    message = mobile.get_message()
    if message:
        current=time.time_ns()
        if message['data']=="SHUTDOWN":
            endprocess()
            exit()
        if message['data']!=1 :
            payload=json.loads(message['data'])
            rds.publish(ccix_consol_data_channel,json.dumps(payload))