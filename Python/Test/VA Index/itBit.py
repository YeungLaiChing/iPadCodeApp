import requests
resp = requests.get('https://api.paxos.com/v2/markets/BTCUSD/recent-executions')
print(resp.json())
