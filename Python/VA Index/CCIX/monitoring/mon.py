import pandas as pd
import time 
import numpy as np
import redis
import sys

topic = 'ccix_index_channel'
if len(sys.argv) > 1:
    topic=sys.argv[1]

rds = redis.Redis(host='192.168.0.3', port=6379, db=0,decode_responses=True)

exchange_list=['bitstamp','coinbase','itbit','kraken','lmax']

mobile = rds.pubsub()
mobile.subscribe(topic)
print(f"already subscribed channel {topic}")

def endprocess():

    #new_file_path = Path(__file__).with_name(f"config.json")
    #f = open(new_file_path, 'w', encoding='utf-8')
    #json.dump(index_config, f, ensure_ascii=False, indent=4)
    #f.close()

    return "OK"

for i in range(10):
    message = mobile.get_message(timeout=5)
    if message:
        current=time.time_ns()
        if message['data']=="SHUTDOWN":
            endprocess()
            exit()
        if message['data']!=1 :
            current=int(time.time())

            df2 = pd.DataFrame(columns=exchange_list)
            df2["timestamp_hrs"]=str(current/3600)*3600
            for i in range(25):
                hrs=int(int(current/3600)*3600-3600*(i))
                df2.loc[i,"timestamp_hrs"]=hrs
                for exchange in exchange_list :
                    if rds.hget(hrs,exchange) :
                        df2.loc[i,exchange]=float(rds.hget(hrs,exchange))
                        

            df3=df2[(df2.timestamp_hrs < current) & (df2.timestamp_hrs >= int(int(current/3600)*3600-3600*(23)))].drop(columns=['timestamp_hrs']).T
            if current == int(current/3600)*3600:
                df3=df2[(df2.timestamp_hrs < current) & (df2.timestamp_hrs >= int(int(current/3600)*3600-3600*(24)))].drop(columns=['timestamp_hrs']).T


            df3['24hr_vol']=df3.sum(axis=1)
            print(f"Current Time is {current}")
            print(df3)
                    
            print(message['data'])
            time.sleep(2)