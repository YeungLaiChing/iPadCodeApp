import time
import redis
import sys
from datetime import datetime, timezone,date
import json
from decimal import Decimal
import boto3

def get_current_time():
    return datetime.fromtimestamp(int(time.time()+8*3600), tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

def endprocess():
    target_date = date.today() 

    return "OK"
def create_table(dynamodb=None,table=None):
 
    try:
        dynamodb.create_table(
        TableName=table,
        KeySchema=[

            {
                'AttributeName': 'key',
                'KeyType': 'HASH'  # Sort key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'key',
                # AttributeType refers to the data type 'N' for number type and 'S' stands for string type.
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            # ReadCapacityUnits set to 10 strongly consistent reads per second
            'ReadCapacityUnits': 100,
            'WriteCapacityUnits': 100  # WriteCapacityUnits set to 10 writes per second
        }
        )
    except Exception:
    # do something here as you require
        pass
def get_table_partition(input):
    return int(input/3600)*3600

def get_db_partition(input):
    #return f"GMT{int(input/24/3600)*24*3600-8*3600}"
    return f"IDXDATE{datetime.fromtimestamp(int(input+16*3600), tz=timezone.utc).strftime('%Y%m%d')}"
    
def main_process(table,rds,topic,dbconfig):
    now=time.time()
    table_list={}
    session_list={}
    
    session_name=get_db_partition(now)

    db=boto3.resource('dynamodb', 
                   endpoint_url=dbconfig['endpoint_url'],
                   region_name=dbconfig['region_name'],
                   aws_access_key_id=session_name,
                   aws_secret_access_key= session_name)
    session_list[session_name]=db
    dynamodb=session_list[session_name]
    
    
    table_name=f"{table}_{get_table_partition(now)}"
    
    create_table(dynamodb=dynamodb,table=table_name)
    
    exchange_table = dynamodb.Table(table_name)
    table_list[table_name]=exchange_table
    
    mobile = rds.pubsub()
    mobile.subscribe(topic)
    print(f"{get_current_time()}: already subscribed channel {topic}")
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
                payload=json.loads(message['data'],parse_float=Decimal)
                key=f"{payload['exchange']}_{payload['timestamp_org']}_{payload['from_symbol']}_{payload['to_symbol']}_{payload['side']}_{payload['trade_id']}_{payload['price']}_{payload['volume']}"
                payload['key']=key
                table_name=f"{table}_{get_table_partition(payload['timestamp'])}"
                session_name=get_db_partition(payload['timestamp'])
                
                if session_name not in session_list.keys():
                    print(f"{get_current_time()}: create new session. {session_name}")
                    db=boto3.resource('dynamodb', 
                        endpoint_url=dbconfig['endpoint_url'],
                        region_name=dbconfig['region_name'],
                        aws_access_key_id=session_name,
                        aws_secret_access_key= session_name)
                    session_list[session_name]=db
                        
                dynamodb=session_list[session_name]
                
                if table_name not in table_list.keys():
                    print(f"{get_current_time()}: create new table. {table_name}")
                    create_table(dynamodb=dynamodb,table=table_name)
                    
                    exchange_table = dynamodb.Table(table_name)
                    table_list[table_name]=exchange_table
    
                table = table_list[table_name]
    
                table.batch_writer().put_item(Item=payload)
if __name__ == "__main__":
    print(f"{get_current_time()}: application startup! ")
    print(sys.argv)
    
    if len(sys.argv) > 1:
        
        file_path=sys.argv[1]
        f = open (file_path, "r")
        config = json.loads(f.read())
        f.close()
        print(f"{get_current_time()}: config conten:")
        print(config)
        
        target_table = config['target_table']
        source_topic = config['source_topic']
        rds = redis.Redis(
            host=config['redis_ip'], 
            port=config['redis_port'], 
            db=0,
            decode_responses=True)

        dbconfig={
            'endpoint_url':config['endpoint_url'],
            'region_name':config['region_name']
        }
    else:
        target_table = 'test'
        source_topic = 'ccix_btc_data_channel'
        rds = redis.Redis(host='192.168.0.3', port=6379, db=0,decode_responses=True)

        dbconfig={
            'endpoint_url':'http://192.168.0.3:8000',
            'region_name':'us-east-1'
        }
        
    main_process(table=target_table,rds=rds,topic=source_topic,dbconfig=dbconfig)