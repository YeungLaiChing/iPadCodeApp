import asyncio
from websockets.asyncio.server import serve
from websockets import ConnectionClosed
from datetime import datetime
import json
import random
import time

#pip install websockets
#python -m websockets --version
#This tutorial is written for websockets 13.1.
#If you installed another version, you should switch to the corresponding version of the documentation.

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
    
    while True:
        await asyncio.sleep(1)
        c = datetime.now()
        # Displays Time
        message = get_message('Hello')
        await broadcast(message)

async def main():
    async with serve(handler, "localhost", 8765):
        await broadcast_messages()  # runs forever

if __name__ == "__main__":
    asyncio.run(main())