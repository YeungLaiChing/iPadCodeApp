import asyncio
from websockets.asyncio.server import serve
from websockets import ConnectionClosed
from datetime import datetime
import json
import random
import time
import redis
import os

#pip install websockets
#python -m websockets --version
#This tutorial is written for websockets 13.1.
#If you installed another version, you should switch to the corresponding version of the documentation.
redis_host=os.environ.get('REDIS_HOST', '192.168.0.55')
redis_port=int(os.environ.get('REDIS_PORT', '6379'))

r = redis.Redis(
    host=redis_host,
    port=redis_port,
    decode_responses=True
)
last={}
last['BTCIndex']="0"
last['ETHIndex']="0"

CLIENTS = set()
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

async def relay(queue, websocket):
    while True:
        # Implement custom logic based on queue.qsize() and
        # websocket.transport.get_write_buffer_size() here.
        message = await queue.get()
        await websocket.send(message)

async def handler(websocket):
    print("Add :" + str(websocket.id))
    print(websocket.local_address)
    print(websocket.remote_address)
    queue = asyncio.Queue()
    relay_task = asyncio.create_task(relay(queue, websocket))
    CLIENTS.add(queue)
    try:
        async for message in websocket:
            await broadcast(message)
            print(message)
    finally:
        print("Drop :" + str(websocket.id))
        CLIENTS.remove(queue)
        relay_task.cancel()


async def send(websocket, message):
    try:
        await websocket.send(message)
    except ConnectionClosed:
        pass

        
async def broadcast(message):
    for queue in CLIENTS:
        queue.put_nowait(message)
        
def getMessage():
    message="Hello"
    return message

async def broadcast_messages():
    mobile = r.pubsub()
    mobile.subscribe('calc_btc_index')
    mobile2 = r.pubsub()
    mobile2.subscribe('crypto_index_HKBTCI-USD')
    while True:
        await asyncio.sleep(0.001)
        message =  mobile.get_message()
        if message:
            current=time.time_ns()
            if message['data']!=1 :
                payload=json.loads(message['data'])
                if last['BTCIndex']<payload.get('hkt') :
                    last['BTCIndex']=payload.get('hkt')
                    output = {'indexName': payload.get('id'), 'exchangeTime' : payload.get('hkt')+".000000000", 'indexValue' : payload.get('idx')}
                    await broadcast(json.dumps(output))
                #output = {'indexName': name, 'exchangeTime' : getFormattedTime(current), 'indexValue' : result}
        message2 =  mobile2.get_message()
        if message2:
            current=time.time_ns()
            if message2['data']!=1 :
                payload=json.loads(message2['data'])
                output = {'indexName': payload.get('indexName'), 'exchangeTime' : payload.get('exchangeTime')+".000000000", 'indexValue' : payload.get('indexValue')}
                await broadcast(json.dumps(output))
                #output = {'indexName': name, 'exchangeTime' : getFormattedTime(current), 'indexValue' : result}
        time.sleep(0.01)
    #while True:
    #    data = await mobile.rec.recv()
    #    c = datetime.now()
    #    # Displays Time
    #    message = get_message('Hello')
    #    await broadcast(message)

async def main():
    async with serve(handler, "localhost", 8765):
        await broadcast_messages()  # runs forever

if __name__ == "__main__":
    asyncio.run(main())