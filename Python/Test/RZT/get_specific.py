import requests
import json
# login
url = "https://core.hkexstaging.datahex.rozettatech.com/realms/datahex/protocol/openid-connect/token"

headers = {
    'Content-Tpye':'application/x-www-form-urlencoded'
}

payloads = {
  "grant_type": "password",
  "username": "laichingyeung@hkex.com.hk",
  "password": "P@ssw0rd!",
  "client_id": "frontend_client"
}

r = requests.post(url=url, headers=headers, data=payloads)

access_token=r.json().get('access_token')

# /api/data/v1/datasets/tick/instruments/search/{queryId}

headers = {
    "Authorization": f"Bearer {access_token}"  
}
queryId=1
url = f"/api/data/v1/datasets/tick/instruments/search/{queryId}"
r=requests.get(url=f"https://core.hkexstaging.datahex.rozettatech.com{url}",headers=headers)
print(f"===== GET result for {url} =========")
print(r.json())


# /api/data/v1/datasets/tick/exchanges/instruments/{queryId}

headers = {
    "Authorization": f"Bearer {access_token}"  
}
queryId=1
url = f"/api/data/v1/datasets/tick/exchanges/instruments/{queryId}"
r=requests.get(url=f"https://core.hkexstaging.datahex.rozettatech.com{url}",headers=headers)
print(f"===== GET result for {url} =========")
print(r.json())



# /api/data/v1/datasets/tick/instruments/verify/{queryId}

headers = {
    "Authorization": f"Bearer {access_token}"  
}
queryId=1
url = f"/api/data/v1/datasets/tick/instruments/verify/{queryId}"
r=requests.get(url=f"https://core.hkexstaging.datahex.rozettatech.com{url}",headers=headers)
print(f"===== GET result for {url} =========")
print(r.json())

