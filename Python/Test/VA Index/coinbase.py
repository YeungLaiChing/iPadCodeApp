import requests
import pandas as pd
resp = requests.get('https://api.exchange.coinbase.com/products/BTC-USD/trades')
print(pd.json_normalize(resp.json()).tail())
