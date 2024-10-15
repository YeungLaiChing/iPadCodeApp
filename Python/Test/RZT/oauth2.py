import requests
import json
# login
url = "https://core.hkexstaging.datahex.rozettatech.com/realms/datahex/protocol/openid-connect/token"

headers = {
    'Content-Tpye':'application/x-www-form-urlencoded'
}

#headers = {
#    'Content-Tpye':'application/json',
#    'accept': 'application/json'
#}


payloads = {
  "grant_type": "password",
  "username": "laichingyeung@hkex.com.hk",
  "password": "P@ssw0rd!",
  "client_id": "frontend_client"
}

#curl -X POST https://core.hkexstaging.datahex.rozettatech.com/realms/datahex/protocol/openid-connect/token \
#    -H 'Content-Type: application/x-www-form-urlencoded' \
#    -d 'grant_type=password&username=laichingyeung@hkex.com.hk&password=P@ssw0rd!&client_id=frontend_client'

r = requests.post(url=url, headers=headers, data=payloads)

print("===== login resp text=========")
print(r.text)
print("===== login resp text=========")
print(r.json())
print("===== token =========")
access_token=r.json().get('access_token')
print(access_token)
print("===== login resp header=========")
print(r.headers)
print("===== login resp cookies=========")
cookies=r.cookies
print(cookies)
print(cookies.get_dict())

headers = {
    "Authorization": f"Bearer {access_token}"  
}

#get data
url = "https://core.hkexstaging.datahex.rozettatech.com/api/data/v1/datasets/tick/security_types"

r=requests.get(url=url,headers=headers,cookies=cookies)
print("===== GET security_types resp text after login =========")
print(r.json())

#get data
url = "https://core.hkexstaging.datahex.rozettatech.com/api/account/v1/preferences/s3_details"
r=requests.get(url=url,headers=headers,cookies=cookies)
print("===== GET s3_details resp text after login =========")
print(r.json())

#get data
url = "https://core.hkexstaging.datahex.rozettatech.com/api/extract/v1/datasets/tick/requests"
r=requests.get(url=url,headers=headers,cookies=cookies)
print("===== GET requests resp text after login =========")
print(r.json())
