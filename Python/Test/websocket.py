import asyncio
import websockets
import json

URL = 'wss://stream.coinmarketcap.com/price/latest'


async def hello():
  async with websockets.connect(URL) as websocket:
    payload = {
      'data': {
        'cryptoIds': [1],
        'index': 'detail'
        },
      'id': 'price',
      'method': 'subscribe'
    }
    await websocket.send(json.dumps(payload))
    msg = await websocket.recv()
    print(msg)
        
def default(args):
  asyncio.run(hello())
  
        