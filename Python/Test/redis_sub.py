import redis
import time
from datetime import datetime
import json


def getFormattedTime(ns):
    dt = datetime.fromtimestamp(ns//1000000000)
    formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
    nanoseconds_part = str(int(ns % 1_000_000_000)).zfill(9)
    formatted_time += '.' + nanoseconds_part
    return formatted_time

r = redis.Redis(
    host='192.168.0.5',
    port=6379,
    decode_responses=True
)

# pubsub() method creates the pubsub object
# but why i named it mobile 🧐
# just kidding 😂 think of it as the waki taki that listens for incomming messages
mobile = r.pubsub()

# use .subscribe() method to subscribe to topic on which you want to listen for messages

topic='index-distribution'
# .listen() returns a generator over which you can iterate and listen for messages from publisher

#for message in mobile.listen():

def msg_handler(message):
        message = mobile.get_message()
        if message:
            current=time.time_ns()
            if message['data']!=1 :
                payload=json.loads(message['data'])
                indexTime=payload['exchangeTime']
                indexName=payload['indexName']
                indexValue=payload['indexValue']
                ns=current
                diff_ns=current-ns
                diff_ms=diff_ns / 1000000
                print(f'{indexTime} : {indexValue} [{indexName}]')

def method2():
    mobile.subscribe(**{topic:msg_handler})
    
def method1():
    mobile.subscribe(topic)
    while True:
        message = mobile.get_message()
        if message:
            current=time.time_ns()
            if message['data']!=1 :
                payload=json.loads(message['data'])
                indexTime=payload['exchangeTime']
                indexName=payload['indexName']
                indexValue=payload['indexValue']
                ns=current
                diff_ns=current-ns
                diff_ms=diff_ns / 1000000
                print(f'{indexTime} : {indexValue} [{indexName}]')
                
method2()
    