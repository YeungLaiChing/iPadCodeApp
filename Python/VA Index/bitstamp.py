import requests
resp = requests.get('https://www.bitstamp.net/api/v2/transactions/btcusd?time=minute')
print(resp.json())

