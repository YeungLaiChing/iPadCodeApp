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
import json, math
import pandas as pd
from decimal import Decimal


class OrderBookProcessor():
    def __init__(self, snapshot):
        self.bids = []
        self.offers = []
        snapshot_data = json.loads(snapshot)
        px_levels = snapshot_data['data']
       
        for i in range(len(px_levels)):
            level = px_levels[i]
    
            if level['side'] == 'Buy':
                
                self.bids.append(level)
            elif level['side'] == 'Sell':
                
                self.offers.append(level)
            else:
                raise IOError()
        
        self._sort()
       

    def apply_update(self, data):
        event = json.loads(data)
        #if event['channel'] != 'l2_data':
        #    return
        action = event['action']
        if event['action'] != 'delete':
            for update in event['data']:
                self._apply(update)
        else :
            for update in event['data']:
                self._delete(update)
        self._filter_closed()
        self._sort()
        
    def _delete(self, level):
        if level['side'] == 'Buy':
            
            for i in range(len(self.bids)):
                if self.bids[i]['price'] == level['price']:
                    print(f"Delete bid {level['price']}")
                    self.bids.pop(i)
                    break
        else:
            for i in range(len(self.offers)):
                if self.offers[i]['price'] == level['price']:
                    print(f"Delete ask {level['price']}")
                    self.offers.pop(i)
                    break
         

    def _apply(self, level):
        if level['side'] == 'Buy':
            found = False
            for i in range(len(self.bids)):
                if self.bids[i]['price'] == level['price']:
                    self.bids[i] = level
                    found = True
                    break
            if not found:
                self.bids.append(level)
        else:
            found = False
            for i in range(len(self.offers)):
                if self.offers[i]['price'] == level['price']:
                    self.offers[i] = level
                    found = True
                    break
            if not found:
                self.offers.append(level)

    def _filter_closed(self):
        self.bids = [x for x in self.bids if abs(float(x['size'])) > 0]
        self.offers = [x for x in self.offers if abs(float(x['size'])) > 0]

    def _sort(self):
        self.bids = sorted(self.bids, key=lambda x: float(x['price']) * -1)
        self.offers = sorted(self.offers, key=lambda x: float(x['price']))

    def create_df(self, agg_level):

        bids_subset = int(len(self.bids)/1)
        asks_subset = int(len(self.offers)/1)
        
        print(len(self.bids))

        bids = self.bids[:bids_subset]
        asks = self.offers[:asks_subset]
        
        print(bids)
        print(asks)

        bid_df = pd.DataFrame(bids, columns=['price', 'size'], dtype=float)
        ask_df = pd.DataFrame(asks, columns=['price', 'size'], dtype=float)
        
        print(bid_df)
        print(ask_df)

        bid_df = self.aggregate_levels(
            bid_df, agg_level=Decimal(agg_level), side='bid')
        ask_df = self.aggregate_levels(
            ask_df, agg_level=Decimal(agg_level), side='offer')

        bid_df = bid_df.sort_values('price', ascending=False)
        ask_df = ask_df.sort_values('price', ascending=False)

        bid_df.reset_index(inplace=True)
        bid_df['id'] = bid_df['index'].index.astype(str) + '_bid'

        ask_df = ask_df.iloc[::-1]
        ask_df.reset_index(inplace=True)
        ask_df['id'] = ask_df['index'].index.astype(str) + '_ask'
        ask_df = ask_df.iloc[::-1]

        order_book = pd.concat([ask_df, bid_df])
        return order_book

    def aggregate_levels(self, levels_df, agg_level, side):
        right=False
        if side == 'bid':
            right = False
            def label_func(x): return x.left
        elif side == 'offer':
            right = True
            def label_func(x): return x.right

        min_level = math.floor(Decimal(min(levels_df.price)) / agg_level - 1) * agg_level
        max_level = math.ceil(Decimal(max(levels_df.price)) / agg_level + 1) * agg_level

        level_bounds = [float(min_level + agg_level * x)
                        for x in range(int((max_level - min_level) / agg_level) + 1)]

        levels_df['bin'] = pd.cut(levels_df.price, bins=level_bounds, precision=10, right=right)

        levels_df = levels_df.groupby('bin').agg(size=('size', 'sum')).reset_index()
        print("price")
        levels_df['price'] = levels_df.bin.apply(label_func)
        print(levels_df)
        print("DF")
        levels_df = levels_df[levels_df['size'] > 0]
        levels_df = levels_df[['price', 'size']]

        return levels_df
