import pandas as pd
import time 
import numpy as np
import redis
import json
import sys

topic = 'ccix_btc_data_channel'
if len(sys.argv) > 1:
    topic=sys.argv[1]

rds = redis.Redis(host='192.168.0.3', port=6379, db=0,decode_responses=True)

def apply_time_penalty_factor(value):
    if value < 300:
        return 1
    if 300 <= value < 600:
        return 0.8
    elif 600 <= value < 900:
        return 0.6
    elif 900 <= value < 1200:
        return 0.4
    elif 1200 <= value < 1500:
        return 0.2
    elif value >= 1500:
        return 0.001


exchange_list=['bitstamp','coinbase','itbit','kraken','lmax']

df = pd.DataFrame(exchange_list, columns=['exchange']).set_index("exchange")

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


last_index=64773
threshold=0.1



for index,row in df.iterrows():
    if rds.hget("BTC",index):
        vals=rds.hget("BTC",index).split("@")
        df.loc[index,'last_update_time']=int(vals[0])
        df.loc[index,'current_price']=float(vals[1])
        
df['calc_time']=int(current)
df['time_diff']=df['calc_time']-df['last_update_time']
df['time_penalty_factor']= df['time_diff'].map(apply_time_penalty_factor)
df['price_diff'] =abs(df['current_price']/last_index-1)
df.loc[df['price_diff'] < threshold, 'outlier_penalty_factor'] = 1
df.loc[df['price_diff'] >= threshold, 'outlier_penalty_factor'] = 0

df=df.astype({"last_update_time": int})
          


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

last_index=64773
last_index_time=64773

if rds.hget("BTC","last_index"):
    last_index=rds.hget("BTC","last_index")
    
if rds.hget("BTC","last_index_time"):
    last_index_time=rds.hget("BTC","last_index_time")

while True:
    message = mobile.get_message(timeout=5)
    if message:
        current=time.time_ns()
        if message['data']=="SHUTDOWN":
            endprocess()
            exit()
        if message['data']!=1 :
            payload=json.loads(message['data'])
            exchange=payload["exchange"]
            if exchange in exchange_list:
                if rds.hget("BTC","last_index"):
                    last_index=float(rds.hget("BTC","last_index"))
                    
                price=float(payload["price"])
                volume=float(payload["volume"])
                hr=payload["timestamp_hrs"]
                
                
                if hr not in df2['timestamp_hrs'].values:
                    print(f"find it {hrs}")
                    i=len(df2.index)
                    df2.loc[i,"timestamp_hrs"]=hr
                    for ex in exchange_list :
                        if rds.hget(hr,ex) :
                            df2.loc[i,ex]=float(rds.hget(hr,ex))
                    print(f"Weighting table init for new hour {hr}")
                    
                    print(df2)
                    
                current=int(payload["timestamp"])
                
                df3=df2[(df2.timestamp_hrs < current) & (df2.timestamp_hrs >= int(int(current/3600)*3600-3600*(23)))].drop(columns=['timestamp_hrs']).T
                if current == int(current/3600)*3600:
                    df3=df2[(df2.timestamp_hrs < current) & (df2.timestamp_hrs >= int(int(current/3600)*3600-3600*(24)))].drop(columns=['timestamp_hrs']).T


                df3['24hr_vol']=df3.sum(axis=1)
                

                df['calc_time']=int(payload["timestamp"])
             
                df.loc[exchange,'last_update_time']=int(payload["timestamp"])
                df.loc[exchange,'current_price']=float(payload["price"])
                
                df['time_diff']=df['calc_time']-df['last_update_time']
                df['time_penalty_factor']= df['time_diff'].map(apply_time_penalty_factor)
                
                if last_index > 0 :
                    df['price_diff'] =abs(df['current_price']/last_index-1)
                    df.loc[df['price_diff'] < threshold, 'outlier_penalty_factor'] = 1
                    df.loc[df['price_diff'] >= threshold, 'outlier_penalty_factor'] = 1
                else :
                    df['price_diff']=df['current_price']
                    df['outlier_penalty_factor']=1
                    
                for ex in exchange_list :
                    #df.loc[ex,'weights']=df3.loc[ex,'weights']
                    df.loc[ex,'24hr_vol']=df3.loc[ex,'24hr_vol']
                
                df['adj_vol']=df['time_penalty_factor']*df['24hr_vol']*df['outlier_penalty_factor']
                df['weights']= df['adj_vol'].div(df['adj_vol'].sum())
                df['adj_price']=df['current_price']*df['weights']
             
                print(df[['time_diff','time_penalty_factor','current_price','outlier_penalty_factor','24hr_vol','weights','adj_price']].rename(columns={'time_penalty_factor':'tpf','outlier_penalty_factor':'opf','current_price':'price'}))
                last_index=round(df['adj_price'].sum(),2)
      

                if int(payload['timestamp']) > int(last_index_time) or 1==1:
                    rds.hset("BTC","last_index",last_index)
                    rds.hset("BTC","last_index_time",payload['timestamp'])
                    last_index_time=payload['timestamp']
                    pl={
                        'index':'BTCIndex',
                        'exchange':payload["exchange"],
                        'timestamp_hkt':payload["timestamp_hkt"],
                        'indexValue':last_index
                    }
                    rds.publish("ccix_index_channel",json.dumps(pl))
                    print(pl)
            else:
                print(f"SKIP! {exchange} is not an eligible exchange!")
