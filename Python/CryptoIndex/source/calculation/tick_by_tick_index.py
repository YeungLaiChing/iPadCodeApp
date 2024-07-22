import pandas as pd
import time 
import numpy as np
import csv
import threading
from datetime import datetime, timezone, timedelta
from pathlib import Path
import redis
import json
import sys
import os

crypto_asset=os.environ.get('CRYPTO_ASSET','ETH')
redis_host=os.environ.get('REDIS_HOST', '192.168.0.55')
redis_port=int(os.environ.get('REDIS_PORT', '6379'))
topic=os.environ.get('DATA_CHANNEL',f'ccix_{crypto_asset.lower()}_data_channel')
dissem_topic = os.environ.get('INDEX_CHANNEL',f'ccix_{crypto_asset.lower()}_index_channel')
exchange_list= os.environ.get('EXCHANGE_LIST',"bitstamp,coinbase,itbit,kraken,lmax").split(",")

rds = redis.Redis(host=redis_host,port=redis_port, db=0,decode_responses=True)
data_path="./data/"
file_list={}
last_acc_vol_list={}
file_name=f'{crypto_asset.lower()}_index.csv'
lock=threading.Lock()

def get_date_partition(input):
    return f"{datetime.fromtimestamp(int(input+16*3600), tz=timezone.utc).strftime('%Y%m%d')}"
               
def get_path_by_time(now):
    folder_partition=get_date_partition(now)
    path=f"{data_path}/{folder_partition}"
    Path(path).mkdir(parents=True, exist_ok=True)
    return path

def get_table_partition(input):
    return int(input/3600)*3600

def get_current_time():
    return get_format_hkt(time.time())

def get_format_hkt(ts):
    return datetime.fromtimestamp(int(ts+8*3600), tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

def write_to_csv(csv_file_path,data_row):
    with lock:
        with open(csv_file_path,mode='a', newline='') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(data_row)
            

def setup_csv_file(csv_file_path):
    with open(csv_file_path,mode='a',newline='') as file:
        if file.tell() == 0:
            csv_writer=csv.writer(file)
            csv_writer.writerow(
            ['Ticker',
            'Timestamp',
            'Timestamp_HKT',
            'Index_Value',
            'Last_Update_Exchange',
            'Last_Update_Trade_Id',
            'Last_Update_Timestamp',
            'Last_Update_Time_Penalty',
            'Last_Update_Price',
            'Last_Update_Volume',
            'Last_Update_Hourly_Volume',
            'Last_Update_24Hour_Volume']
            )
            
            
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


def endprocess():
    #target_date = date.today() 

    #new_file_path = Path(__file__).with_name(f"config.json")
    #f = open(new_file_path, 'w', encoding='utf-8')
    #json.dump(index_config, f, ensure_ascii=False, indent=4)
    #f.close()

    return "OK"


def start():
    current=int(time.time())
    current_hkt=get_format_hkt(current)
    current_hr=get_table_partition(current)

    df = pd.DataFrame(exchange_list, columns=['exchange']).set_index("exchange")
    df2 = pd.DataFrame(columns=exchange_list)
    df2["timestamp_hrs"]=str(current/3600)*3600
    
    global file_list
    global last_acc_vol_list
    
    file_list[str(current_hr)]=f"{get_path_by_time(current_hr)}/{crypto_asset.lower()}_{current_hr}.csv"
    setup_csv_file(file_list[str(current_hr)])
    
    for i in range(25):
        hrs=int(int(current/3600)*3600-3600*(i))
        df2.loc[i,"timestamp_hrs"]=hrs
        for exchange in exchange_list :
            acc_vol_key=f"{exchange}_{crypto_asset}"
            if rds.hget(hrs,acc_vol_key) :
                df2.loc[i,exchange]=float(rds.hget(hrs,acc_vol_key))
                last_acc_vol_list[f"{exchange}_{hrs}"]=df2.loc[i,exchange]
                

    df3=df2[(df2.timestamp_hrs < current) & (df2.timestamp_hrs >= int(int(current/3600)*3600-3600*(23)))].drop(columns=['timestamp_hrs']).T
    if current == int(current/3600)*3600:
        df3=df2[(df2.timestamp_hrs < current) & (df2.timestamp_hrs >= int(int(current/3600)*3600-3600*(24)))].drop(columns=['timestamp_hrs']).T


    df3['24hr_vol']=df3.sum(axis=1)


    last_index=64773
    threshold=0.1



    for index,row in df.iterrows():
        if rds.hget(crypto_asset,index):
            vals=rds.hget(crypto_asset,index).split("@")
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



    last_index=64773
    last_index_time=64773

    if rds.hget(crypto_asset,"last_index"):
        last_index=rds.hget(crypto_asset,"last_index")
        
    if rds.hget(crypto_asset,"last_index_time"):
        last_index_time=rds.hget(crypto_asset,"last_index_time")

    while True:
        message = mobile.get_message(timeout=5)
        if message:
            current=int(time.time())
            current_hkt=get_format_hkt(current)
            current_hr=get_table_partition(current)

            if message['data']=="SHUTDOWN":
                endprocess()
                exit()
            if message['data']!=1 :
                payload=json.loads(message['data'])
                
                exchange=payload["exchange"]
                if exchange in exchange_list:
                    # print(payload)
                    if rds.hget(crypto_asset,"last_index"):
                        last_index=float(rds.hget(crypto_asset,"last_index"))
                        
                    price=float(payload["price"])
                    volume=float(payload["volume"])
                    acc_vol=float(payload["acc_vol"])
                    hr=payload["timestamp_hrs"]
                    last_acc_vol_list[f"{exchange}_{hr}"]=acc_vol
                
                    if hr not in df2['timestamp_hrs'].values:
                        print(f"try to find {hr}")
                        i=len(df2.index)
                        df2.loc[i,"timestamp_hrs"]=hr
                        acc_vol_key=f"{ex}_{crypto_asset}"
                        df2.loc[i,exchange]=acc_vol
                        #print(f"Weighting table init for new hour {hr}")
                        
                        print(df2) 

                    for ex in exchange_list :
                        if last_acc_vol_list.get(f"{ex}_{hr}"):
                            df2.loc[(df2['timestamp_hrs'] == hr), ex] = last_acc_vol_list[f"{ex}_{hr}"]
                        
                    #print(df2) 

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
                
                    #print(df[['time_diff','time_penalty_factor','current_price','outlier_penalty_factor','24hr_vol','weights','adj_price']].rename(columns={'time_penalty_factor':'tpf','outlier_penalty_factor':'opf','current_price':'price'}))
                    last_index=round(df['adj_price'].sum(),2)
        

                    if int(payload['timestamp']) > int(last_index_time) or 1==1:
                        rds.hset(crypto_asset,"last_index",float(last_index))
                        rds.hset(crypto_asset,"last_index_time",int(payload['timestamp']))
                        last_index_time=payload['timestamp']
                        pl={
                            'id':f'{crypto_asset}Index',
                            'ts':current,
                            'hkt':current_hkt,
                            'idx':last_index,
                            'ex':payload["exchange"],
                            'ref':payload["trade_id"]
                        }
                        data_row=[f'{crypto_asset}Index',
                            current,
                            current_hkt,
                            last_index,
                            payload["exchange"],
                            payload["trade_id"],
                            payload["timestamp"],
                            float(df.loc[exchange,'time_penalty_factor']),
                            payload["price"],
                            payload["volume"],
                            payload["acc_vol"],
                            df.loc[exchange,'24hr_vol']]
                        
                        rds.publish(dissem_topic,json.dumps(pl))
                        
                        #partition=get_date_partition(current)
                        #if partition not in file_list:
                        #    file_list[partition]=f"{get_path_by_time(current)}/{file_name}"
                        #    setup_csv_file(file_list[partition])

                        

                        if str(current_hr) not in file_list:
                            #file_name=f"{crypto_asset.lower()}_{current_hr}.csv"
                            file_list[str(current_hr)]=f"{get_path_by_time(current_hr)}/{crypto_asset.lower()}_{current_hr}.csv"
                            setup_csv_file(file_list[str(current_hr)])

                        write_to_csv(file_list[str(current_hr)],data_row)
                        
                        #print(pl)
                #else:
                    #print(f"SKIP! {exchange} is not an eligible exchange!")
if __name__ == "__main__":
    start()
    