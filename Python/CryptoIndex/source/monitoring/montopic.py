import time
import redis
import sys
from datetime import date, timedelta,datetime,timezone
import json

topic = 'ccix_btc_data_channel'
ip='192.168.0.3'
if len(sys.argv) > 1:
    ip='redis-va'


rds = redis.Redis(host=ip, port=6379, db=0,decode_responses=True)

mobile = rds.pubsub()
mobile.subscribe(topic)
print(f"already subscribed channel {topic}")
def get_current_time():
    return datetime.fromtimestamp(int(time.time()+8*3600), tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')


def endprocess():
    target_date = date.today() 

    #new_file_path = Path(__file__).with_name(f"config.json")
    #f = open(new_file_path, 'w', encoding='utf-8')
    #json.dump(index_config, f, ensure_ascii=False, indent=4)
    #f.close()

    return "OK"
current_count=0
last_count=0
last_time=0
while True:
    message = mobile.get_message(timeout=5)
    if message:
        current=time.time_ns()
        if message['data']=="SHUTDOWN":
            endprocess()
            exit()
        if message['data']!=1 :
            current_count=current_count+1
            current_time=time.time()
            if int(current_time/10)*10==int(current_time) and int(current_time)>int(last_time):
                print(f"{get_current_time()}: {round((current_count-last_count)/(current_time-last_time),2)} processed in every sec! total = {current_count} since started!")
                last_count=current_count
                last_time=current_time
            #print(message['data'])