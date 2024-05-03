import time
import redis
import sys
from datetime import datetime, timezone, timedelta,date
import json
from decimal import Decimal
import boto3
from pathlib import Path

def get_current_time():
    return datetime.fromtimestamp(int(time.time()+8*3600), tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

def endprocess():
    target_date = date.today() 

    return "OK"
def create_table(dynamodb=None,table=None):

    
    # Each table/index must have 1 hash key and 0 or 1 range keys.
    
    try:
        dynamodb.create_table(
        TableName=table,
        KeySchema=[

            {
                'AttributeName': 'timestamp',
                'KeyType': 'HASH'  # Sort key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'timestamp',
                # AttributeType refers to the data type 'N' for number type and 'S' stands for string type.
                'AttributeType': 'N'
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
    
def main_process(table,rds,dynamodb,topic):

    create_table(dynamodb=dynamodb,table=table)
    
    exchange_table = dynamodb.Table(table)

    mobile = rds.pubsub()
    mobile.subscribe(topic)
    print(f"{get_current_time()}: already subscribed channel {topic}")
    
    while True:
        message = mobile.get_message(timeout=5)
        if message:
            current=time.time_ns()
            if message['data']=="SHUTDOWN":
                endprocess()
                exit()
            if message['data']!=1 :
                payload=json.loads(message['data'],parse_float=Decimal)
                exchange_table.put_item(Item=payload)
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
        dynamodb = boto3.resource(
            'dynamodb', 
            endpoint_url=config['endpoint_url'],
            region_name=config['region_name'],
            aws_access_key_id=config['aws_access_key_id'],
            aws_secret_access_key= config['aws_secret_access_key'])
    else:
        target_table = 'coinbase'
        rds = redis.Redis(host='192.168.0.3', port=6379, db=0,decode_responses=True)
        dynamodb = boto3.resource(
        'dynamodb', endpoint_url="http://192.168.0.3:8000",region_name='us-east-1',aws_access_key_id='key',
            aws_secret_access_key= '')
        
    main_process(table=target_table,rds=rds,dynamodb=dynamodb,topic=source_topic)