import requests
import time
resp = requests.get('https://public-data-api.london-digital.lmax.com/v1/ticker/btc-usd')
print(resp.json())
time.sleep(0.5)
resp = requests.get('https://public-data-api.london-digital.lmax.com/v1/ticker/btc-usd')
print(resp.json())
