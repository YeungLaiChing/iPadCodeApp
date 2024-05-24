# Copyright 2023-present Coinbase Global, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import asyncio, websockets, sqlite3, json, hmac, hashlib, base64, os, time, sys
from orderbook import OrderBookProcessor


URI = 'wss://trade-hk.osl.com/ws/v4?subscribe=orderBook:BTCUSD'

timestamp = str(int(time.time()))
conn = sqlite3.connect('prime_orderbook.db')
channel = 'l2_data'

product_id = 'ETH-USD'
agg_level = '0.1'
row_count = '50'


async def main_loop():
    while True:
        try:
            async with websockets.connect(URI, ping_interval=None, max_size=None) as websocket:
                #auth_message = await create_auth_message(
                #    channel,
                #    product_id,
                #    timestamp
                #)
                #await websocket.send(auth_message)
                while True:
                    response = await websocket.recv()
                    parsed = json.loads(response)
                    if parsed['action'] == 'partial':
                        print("Init==========================")
                        processor = OrderBookProcessor(response)
                    elif processor is not None:
                        print("Update===============================")
                        processor.apply_update(response)
                    if processor is not None:
                        print("start to create df====================")
                        table = processor.create_df(agg_level=agg_level)
                        print('updated')
                        table.to_sql('book', conn, if_exists='replace', index=False)
                        print("done ============")
                        sys.stdout.flush()
        except websockets.ConnectionClosed:
            continue




if __name__ == '__main__':
    asyncio.run(main_loop())
