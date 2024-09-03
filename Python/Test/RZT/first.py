import requests
import json
# login
url = "https://tickdata.hkex.datahex.rozettatech.com/api/auth/login"

headers = {
    'Content-Tpye':'application/json',
    'accept': 'application/json'
}

payloads = {
  "grant_type": "client_credentials",
  "payload": {
    "client_id": "5pmc41s7ehr8e3gdf4f7fr34d2",
    "client_secret": "6qkg4aipsu24rbfpoi6u9v9ur3faqi3n6rb2hke0j50i1ulso0"
  }
}

#curl -X 'POST' \
#  'https://tickdata.hkex.datahex.rozettatech.com/api/auth/login' \
#  -H 'accept: application/json' \
#  -H 'Content-Type: application/json' \
#  -d '{
#  "grant_type": "client_credentials",
#  "payload": {
#    "client_id": "5pmc41s7ehr8e3gdf4f7fr34d2",
#    "client_secret": "6qkg4aipsu24rbfpoi6u9v9ur3faqi3n6rb2hke0j50i1ulso0"
#  }
#}'

r = requests.post(url=url, headers=headers, data=json.dumps(payloads))

print("===== login resp text=========")
print(r.text)
print("===== login resp header=========")
print(r.headers)
print("===== login resp cookies=========")
cook=r.cookies
print(cook)
print(cook.get_dict())


# get data
# url = "https://tickdata.hkex.datahex.rozettatech.com/api/data/v1/datasets/tick/security_types"

# r=requests.get(url=url,cookies=cook)
