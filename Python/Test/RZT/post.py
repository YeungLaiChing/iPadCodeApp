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
print(access_token)
### optional , plese duble chekc
cookies=r.cookies

headers = {
    "Authorization": f"Bearer {access_token}"  
}

#get data
url = "https://core.hkexstaging.datahex.rozettatech.com/api/data/v1/datasets/tick/security_types"
#r=requests.get(url=url,headers=headers,cookies=cookies)
r=requests.get(url=url,headers=headers)
print("===== GET security_types resp text after login =========")
print(r.json())

# POST	/api/data/v1/datasets/tick/instruments/search
headers = {
    'Content-Tpye':'application/json',
    "Authorization": f"Bearer {access_token}"  
}

#get data
payloads = {
  "instrument": "1",
  "start": "2023-09-05",
  "end": "2023-09-06",
  "searchType": "instrument"
}

url = "/api/data/v1/datasets/tick/instruments/search"
#r=requests.get(url=url,headers=headers,cookies=cookies)
#r=requests.get(url=url,headers=headers,cookies=cookies)
#r=requests.post(url=url,headers=headers,cookies=cookies, json=payloads)
r=requests.post(url=f"https://core.hkexstaging.datahex.rozettatech.com{url}",headers=headers,json=payloads)
print(f"===== POST Result of {url} =========")
print(r.json())
print(f"queryId = {r.json()['data']['id']}")



# POST	/api/data/v1/datasets/tick/exchanges/instruments
headers = {
    'Content-Tpye':'application/json',
    "Authorization": f"Bearer {access_token}"  
}

#get data
payloads = {
  "start": "2023-09-01",
  "end": "2023-09-02",
  "exchanges": [
    "HKEX"
  ],
  "searchType": "instrument",
  "searchText": "8",
  "matchType": "startswith",
  "securityTypes": [
    "101",
    "102"
  ],
  "limit": "100"
}

url = "/api/data/v1/datasets/tick/exchanges/instruments"
#r=requests.get(url=url,headers=headers,cookies=cookies)
#r=requests.get(url=url,headers=headers,cookies=cookies)
#r=requests.post(url=url,headers=headers,cookies=cookies, json=payloads)
r=requests.post(url=f"https://core.hkexstaging.datahex.rozettatech.com{url}",headers=headers,json=payloads)
print(f"===== POST Result of {url} =========")
print(r.json())
print(f"queryId = {r.json()['data']['id']}")





# POST	/api/data/v1/datasets/tick/instruments/verify
headers = {
    'Content-Tpye':'application/json',
    "Authorization": f"Bearer {access_token}"  
}

#get data
payloads = {
  "instruments": [
    {
      "exchange": "HKEX",
      "secType": "101",
      "instrument": "1"
    },
    {
      "exchange": "HKEX",
      "isin": "HK0002007356"
    }
  ],
  "start": "2023-09-01",
  "end": "2023-09-02"
}

url = "/api/data/v1/datasets/tick/instruments/verify"
#r=requests.get(url=url,headers=headers,cookies=cookies)
#r=requests.get(url=url,headers=headers,cookies=cookies)
#r=requests.post(url=url,headers=headers,cookies=cookies, json=payloads)
r=requests.post(url=f"https://core.hkexstaging.datahex.rozettatech.com{url}",headers=headers,json=payloads)
print(f"===== POST Result of {url} =========")
print(r.json())
print(f"queryId = {r.json()['data']['id']}")












# POST	/api/account/v1/preferences
headers = {
    'Content-Tpye':'application/json',
    "Authorization": f"Bearer {access_token}"  
}

payloads = {
  "extract.includeFieldTypes": "true",
  "extract.useLocalTime": "false",
  "extract.dateFormat": "YYYY-MM-DD",
  "extract.periodType": "Slice",
  "extract.upload": "None",
  "extract.maxFileSize": "2"
}

url = "/api/account/v1/preferences"
#r=requests.get(url=url,headers=headers,cookies=cookies)
#r=requests.get(url=url,headers=headers,cookies=cookies)
#r=requests.post(url=url,headers=headers,cookies=cookies, json=payloads)
r=requests.post(url=f"https://core.hkexstaging.datahex.rozettatech.com{url}",headers=headers,json=payloads)
print(f"===== POST Result of {url} =========")
print(r.json())
