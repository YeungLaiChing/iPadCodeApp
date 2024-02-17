import requests
resp = requests.get('https://api.exchange.coinbase.com/products/BTC-USD/trades')
print(resp.json())
