import time
import redis
import sys
from datetime import date, timedelta
import json
from decimal import Decimal
import boto3
from pathlib import Path


def endprocess():
    target_date = date.today() 

    #new_file_path = Path(__file__).with_name(f"config.json")
    #f = open(new_file_path, 'w', encoding='utf-8')
    #json.dump(index_config, f, ensure_ascii=False, indent=4)
    #f.close()

    return "OK"
def create_table(dynamodb=None,exchange=None):

    
    # Each table/index must have 1 hash key and 0 or 1 range keys.
    
    dynamodb.create_table(
        TableName=exchange,
        KeySchema=[

            {
                'AttributeName': 'timestamp_hrs',
                'KeyType': 'HASH'  # Sort key
            },
            {
                'AttributeName': 'timestamp',
                'KeyType': 'RANGE'  # Sort key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'timestamp_hrs',
                # AttributeType refers to the data type 'N' for number type and 'S' stands for string type.
                'AttributeType': 'N'
            },
            {
                'AttributeName': 'timestamp',
                'AttributeType': 'N'
            }
        ],
        ProvisionedThroughput={
            # ReadCapacityUnits set to 10 strongly consistent reads per second
            'ReadCapacityUnits': 1000,
            'WriteCapacityUnits': 1000  # WriteCapacityUnits set to 10 writes per second
        }
    )
    
def main_process(exchange,rds,dynamodb):


    ccix_from_data_channel=str(f'ccix_{exchange}_btc_data_channel')

    ccix_consol_data_channel='ccix_btc_data_channel'

    table_list=dynamodb.list_tables()
    if exchange not in table_list:
        create_table(dynamodb=dynamodb,exchange=exchange)
    
    exchange_table = dynamodb.Table(exchange)

    mobile = rds.pubsub()
    mobile.subscribe(ccix_from_data_channel)
    print(f"already subscribed channel {ccix_from_data_channel}")
    
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
                
                exchange_table.put_item(Item=payload)
        
                key=f"{payload['exchange']}_{payload['timestamp_org']}_{payload['from_symbol']}_{payload['to_symbol']}_{payload['side']}_{payload['trade_id']}_{payload['price']}_{payload['volume']}"
                if rds.setnx(key,"1") and 1==2:
                    rds.expire(key,3600*24)
                    if rds.hget(hr,exchange) :
                        acc_vol=volume+float(rds.hget(hr,exchange))
                    rds.hset(hr,exchange,acc_vol)
                    
                    rds.hset(payload['from_symbol'],exchange,f"{str(payload['timestamp'])}@{price}")
                    rds.publish(ccix_consol_data_channel,message['data'])
                    exchange_table.put_item(Item=payload)
                    
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
        dynamodb = boto3.resource(
            'dynamodb', 
            endpoint_url=config['endpoint_url'],
            region_name=config['region_name'],
            aws_access_key_id=config['aws_access_key_id'],
            aws_secret_access_key= config['aws_secret_access_key'])
    else:
        exchange = 'coinbase'
        rds = redis.Redis(host='192.168.0.3', port=6379, db=0,decode_responses=True)
        dynamodb = boto3.resource(
        'dynamodb', endpoint_url="http://192.168.0.3:8000",region_name='us-east-1',aws_access_key_id='key',
            aws_secret_access_key= '')
        
    main_process(exchange=exchange,rds=rds,dynamodb=dynamodb)