import requests
import json
# login
url = "https://core.hkexstaging.datahex.rozettatech.com/realms/datahex/protocol/openid-connect/token"

headers = {
    'Content-Tpye':'application/x-www-form-urlencoded'
}

payloads = {
  "grant_type": "password",
  "username":"laichingyeung@hkex.com.hk",
  "password":"P@ssw0rd!",
  "client_id":"frontend_client"
}

#curl -X POST https://core.hkexstaging.datahex.rozettatech.com/realms/datahex/protocol/openid-connect/token \
#    -H 'Content-Type: application/x-www-form-urlencoded' \
#    -d 'grant_type=password&username=laichingyeung@hkex.com.hk&password=P@ssw0rd!&client_id=frontend_client'

r = requests.post(url=url, headers=headers, json=payloads)

print("===== login resp text=========")
print(r.text)
print("===== login resp header=========")
print(r.headers)
print("===== login resp cookies=========")
cookies=r.cookies
print(cookies)
print(cookies.get_dict())


#get data
#url = "https://tickdata.hkex.datahex.rozettatech.com/api/data/v1/datasets/tick/security_types"

#r=requests.get(url=url,cookies=cookies)
#print("===== GET resp text=========")
#print(r.text)


