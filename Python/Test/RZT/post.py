import requests
import json
####### login
url = "https://core.hkexstaging.datahex.rozettatech.com/realms/datahex/protocol/openid-connect/token"
headers = {'Content-Tpye':'application/x-www-form-urlencoded'}
payloads = { "grant_type": "password", "username": "laichingyeung@hkex.com.hk", "password": "P@ssw0rd!", "client_id": "frontend_client"}
r = requests.post(url=url, headers=headers, data=payloads)
access_token=r.json().get('access_token')
print(access_token)
####### login completed ##########

# POST	/api/data/v1/datasets/tick/instruments/search
url = "/api/data/v1/datasets/tick/instruments/search"

headers = {'Content-Tpye':'application/json', "Authorization": f"Bearer {access_token}"  }

#get data
payloads = {
  "instrument": "1",
  "start": "2023-09-05",
  "end": "2023-09-06",
  "searchType": "instrument"
}

r=requests.post(url=f"https://core.hkexstaging.datahex.rozettatech.com{url}",headers=headers,json=payloads)
print(f"===== POST Result of {url} =========")
result=r.json()
print(r.status_code)
print(result)
if int(result['status']) == 200 :
    print(f"queryId = {r.json()['data']['id']}")
else :
    print("xxxxx ERROR xxxxxxx")



# POST	/api/data/v1/datasets/tick/exchanges/instruments
url = "/api/data/v1/datasets/tick/exchanges/instruments"
headers = { 'Content-Tpye':'application/json', "Authorization": f"Bearer {access_token}"  }

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


r=requests.post(url=f"https://core.hkexstaging.datahex.rozettatech.com{url}",headers=headers,json=payloads)
print(f"===== POST Result of {url} =========")
result=r.json()
print(r.status_code)
print(result)
if int(result['status']) == 200 :
    print(f"queryId = {r.json()['data']['id']}")
else :
    print("xxxxx ERROR xxxxxxx")





# POST	/api/data/v1/datasets/tick/instruments/verify
url = "/api/data/v1/datasets/tick/instruments/verify"

headers = {    'Content-Tpye':'application/json',    "Authorization": f"Bearer {access_token}"  }

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

r=requests.post(url=f"https://core.hkexstaging.datahex.rozettatech.com{url}",headers=headers,json=payloads)
print(f"===== POST Result of {url} =========")
result=r.json()
print(r.status_code)
print(result)
if int(r.status_code) == 200 :
    #print(f"queryId = {r.json()['data']['id']}")
    print("OK")
else :
    print("xxxxx ERROR xxxxxxx")




# POST	/api/data/v1/preview/tick
url = "/api/data/v1/preview/tick"

headers = {    'Content-Tpye':'application/json',    "Authorization": f"Bearer {access_token}"  }

#get data
payloads = {
  "instruments": [
    "1"
  ],
  "start": "2023-09-01",
  "end": "2023-09-02",
  "messageType": "tas",
  "startTime": "00:00:00:000",
  "endTime": "23:59:59:999"
}

r=requests.post(url=f"https://core.hkexstaging.datahex.rozettatech.com{url}",headers=headers,json=payloads)
print(f"===== POST Result of {url} =========")
result=r.json()
print(r.status_code)
print(result)
if int(r.status_code) == 200 :
    #print(f"queryId = {r.json()['data']['id']}")
    print("OK")
else :
    print("xxxxx ERROR xxxxxxx")





# POST	/api/extract/v1/datasets/tick/requests
url = "/api/extract/v1/datasets/tick/requests"

headers = {    'Content-Tpye':'application/json',    "Authorization": f"Bearer {access_token}"  }

#get data
payloads = {
  "instruments": [
    "1",
    "2"
  ],
  "messageType": "tas",
  "start": "2023-09-01",
  "end": "2023-09-02",
  "includeFieldTypes": "true",
  "startTime": "00:00:00:000",
  "endTime": "23:59:59:999"
}

r=requests.post(url=f"https://core.hkexstaging.datahex.rozettatech.com{url}",headers=headers,json=payloads)
print(f"===== POST Result of {url} =========")
result=r.json()
print(r.status_code)
print(result)
if int(r.status_code) == 200 :
    #print(f"queryId = {r.json()['data']['id']}")
    print("OK")
else :
    print("xxxxx ERROR xxxxxxx")




# POST	/api/account/v1/preferences
url = "/api/account/v1/preferences"

headers = {    'Content-Tpye':'application/json',    "Authorization": f"Bearer {access_token}"  }

payloads = {
  "extract.includeFieldTypes": "true",
  "extract.useLocalTime": "false",
  "extract.dateFormat": "YYYY-MM-DD",
  "extract.periodType": "Slice",
  "extract.upload": "None",
  "extract.maxFileSize": "2"
}


r=requests.post(url=f"https://core.hkexstaging.datahex.rozettatech.com{url}",headers=headers,json=payloads)
print(f"===== POST Result of {url} =========")
result=r.json()
print(r.status_code)
print(result)
if int(r.status_code) == 200 :
    print("OK")
else :
    print("xxxxx ERROR xxxxxxx")

# POST	/api/account/v1/preferences/sftp_details
url = "/api/account/v1/preferences/sftp_details"

headers = {    'Content-Tpye':'application/json',    "Authorization": f"Bearer {access_token}"  }

payloads = {
  "name": "API-My-SFTP-host",
  "host": "myhost.mydomain.com",
  "username": "myusername",
  "password": "mypassword"
}


r=requests.post(url=f"https://core.hkexstaging.datahex.rozettatech.com{url}",headers=headers,json=payloads)
print(f"===== POST Result of {url} =========")
result=r.json()
print(r.status_code)
print(result)
if int(r.status_code) == 200 :
    print("OK")
else :
    print("xxxxx ERROR xxxxxxx")

# POST	/api/account/v1/preferences/s3_details
url = "/api/account/v1/preferences/s3_details"

headers = {    'Content-Tpye':'application/json',    "Authorization": f"Bearer {access_token}"  }

payloads = {
  "name": "API-testing",
  "bucket": "my-unique-bucket",
  "path": "my_results"
}


r=requests.post(url=f"https://core.hkexstaging.datahex.rozettatech.com{url}",headers=headers,json=payloads)
print(f"===== POST Result of {url} =========")
result=r.json()
print(r.status_code)
print(result)
if int(r.status_code) == 200 :
    print("OK")
else :
    print("xxxxx ERROR xxxxxxx")


# POST	/api/account/v1/templates
url = "/api/account/v1/templates"

headers = {    'Content-Tpye':'application/json',    "Authorization": f"Bearer {access_token}"  }

payloads = {
  "name": "APItemplate",
  "messageType": "tas",
  "detail": {
    "fields": [
      "MarketCode",
      "CurrentCode",
      "NumberOfSecurities"
    ]
  }
}


r=requests.post(url=f"https://core.hkexstaging.datahex.rozettatech.com{url}",headers=headers,json=payloads)
print(f"===== POST Result of {url} =========")
result=r.json()
print(r.status_code)
print(result)
if int(r.status_code) == 200 :
    print("OK")
else :
    print("xxxxx ERROR xxxxxxx")
