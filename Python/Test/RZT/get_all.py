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

# GET LIST ########################################################################################
url_list_get=[
"/api/data/v1/datasets/tick/security_types",
"/api/data/v1/datasets/tick/exchanges",
"/api/data/v1/datasets/tick/generic_info",
"/api/data/v1/datasets/tick/exchange_coverages",
"/api/account/v1/usage",
"/api/account/v1/messagetype_fields",
"/api/account/v1/preferences",
"/api/account/v1/preferences/ftp_details",
"/api/account/v1/preferences/sftp_details",
"/api/account/v1/preferences/s3_details",
"/api/account/v1/templates"
]

headers = {
    "Authorization": f"Bearer {access_token}"  
}
for url in url_list_get :
    r=requests.get(url=f"https://core.hkexstaging.datahex.rozettatech.com{url}",headers=headers)
    print(f"===== GET result for {url} =========")
    print(r.json())
