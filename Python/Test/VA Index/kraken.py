import requests
resp = requests.get('https://api.kraken.com/0/public/Trades?pair=BTCUSD')
print(resp.json())
