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

headers = {
    'Content-Tpye':'application/json',
    "Authorization": f"Bearer {access_token}"  
}

#get data
payloads = {
  "extract.includeFieldTypes": "true",
  "extract.useLocalTime": "false",
  "extract.dateFormat": "YYYY-MM-DD",
  "extract.periodType": "Continuous",
  "extract.upload": "None",
  "extract.maxFileSize": 10
}


url = "https://core.hkexstaging.datahex.rozettatech.com/api/account/v1/preferences"
#r=requests.get(url=url,headers=headers,cookies=cookies)
#r=requests.get(url=url,headers=headers,cookies=cookies)
r=requests.post(url=url,headers=headers,cookies=cookies, data=payloads)
print("===== Post Ref resp text after login =========")
print(r.json())
