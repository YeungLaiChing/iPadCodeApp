import time
import redis
import sys
from datetime import date, timedelta
import json

topic = 'ccix_index_channel'
if len(sys.argv) > 1:
    topic=sys.argv[1]


rds = redis.Redis(host='192.168.0.3', port=6379, db=0,decode_responses=True)

mobile = rds.pubsub()
mobile.subscribe(topic)
print(f"already subscribed channel {topic}")

def endprocess():
    target_date = date.today() 

    #new_file_path = Path(__file__).with_name(f"config.json")
    #f = open(new_file_path, 'w', encoding='utf-8')
    #json.dump(index_config, f, ensure_ascii=False, indent=4)
    #f.close()

    return "OK"

while True:
    message = mobile.get_message(timeout=5)
    if message:
        current=time.time_ns()
        if message['data']=="SHUTDOWN":
            endprocess()
            exit()
        if message['data']!=1 :
            print(message['data'])
            