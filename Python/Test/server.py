import asyncio
import websockets
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
mobile.subscribe('index-distribution')

# .listen() returns a generator over which you can iterate and listen for messages from publisher



# create handler for each connection
 
async def handler(websocket, path):
 
    # .data = await websocket.recv()
 
    # .reply = f"Data recieved as:  {data}!"
 #for message in mobile.listen():
    while True:
        message = mobile.get_message()
        if message:
            current=time.time_ns()
            if message['data']!=1 :
                payload=message['data']
                await websocket.send(payload)

    
start_server = websockets.serve(handler, "0.0.0.0", 8000)
 
asyncio.get_event_loop().run_until_complete(start_server)
 
asyncio.get_event_loop().run_forever()