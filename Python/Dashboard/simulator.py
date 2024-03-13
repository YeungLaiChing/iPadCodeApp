import asyncio
import websockets
import time
from datetime import datetime
import json
import random
import redis

def getFormattedTime(ns):
    dt = datetime.fromtimestamp(ns//1000000000)
    formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
    nanoseconds_part = str(int(ns % 1_000_000_000)).zfill(9)
    formatted_time += '.' + nanoseconds_part
    return formatted_time

# create handler for each connection
def get_y():
    value=random.randrange(6000, 7000)+(random.randrange(0,99)/100)
    return value

def get_message(name):
     payload = {'exchangeTime' : getFormattedTime(time.time_ns()), 'indexName' : name,'indexValue':get_y()}
     return json.dumps(payload)
 
async def handler(websocket, path):
 
    # .data = await websocket.recv()
 
    # .reply = f"Data recieved as:  {data}!"
 #for message in mobile.listen():
    while True:
        #message = mobile.get_message()
        time.sleep(0.5)
        message = get_message("TECH_Sim_Tick_by_Tick")
        await websocket.send(message)
        message = get_message("TECH_Sim_2s")
        await websocket.send(message)
        message = get_message("HSTECH")
        await websocket.send(message)

def method1():    
    start_server = websockets.serve(handler, "0.0.0.0", 8000)
     
    asyncio.get_event_loop().run_until_complete(start_server)
     
    asyncio.get_event_loop().run_forever()'
    
    
def method2():
    
    # initializing the redis instance
    r = redis.Redis(
        host='192.168.0.5',
        port=6379,
        decode_responses=True # <-- this will ensure that binary data is decoded
    )
    
    while True:
        time.sleep(0.5)
        message = get_message("TECH_Sim_Tick_by_Tick")

        r.publish("index-distribution", message)
    
    
    