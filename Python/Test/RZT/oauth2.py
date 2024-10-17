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
  "extract.periodType": "Slice",
  "extract.upload": "None",
  "extract.maxFileSize": "2"
}

url = "https://core.hkexstaging.datahex.rozettatech.com/api/account/v1/preferences"
#r=requests.get(url=url,headers=headers,cookies=cookies)
#r=requests.get(url=url,headers=headers,cookies=cookies)
#r=requests.post(url=url,headers=headers,cookies=cookies, json=payloads)
r=requests.post(url=url,headers=headers,json=payloads)
print("===== Post Ref resp text after login =========")
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
r=requests.post(url=url,headers=headers,json=payloads)
print(f"===== POST Result of {url} =========")
print(r.json())
print(r.json()['data']['id'])

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
