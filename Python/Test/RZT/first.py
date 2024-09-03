import requests
session = requests.session()
# login
url = "https://tickdata.hkex.datahex.rozettatech.com/api/auth/login"
headers = {
    'Content-Tpye':'application/json',
    'accept': 'application/json'
}

payloads = {
  "grant_type": "client_credentials",
  "payload": {
    "client_id": "myClientId",
    "client_secret": "myClientSecret"
  }
}
r = session.post(url=url, headers=headers, data=payloads)

print("===== login resp text=========")
print(r.text)
print("===== login resp header=========")
print(r.headers)
print("===== login resp cookies=========")
cook=r.cookies
print(cook)
print(cook.get_dict())


# get data
url = "https://tickdata.hkex.datahex.rozettatech.com/api/data/v1/datasets/tick/security_types"
headers = {
    'Content-Tpye':'application/json',
    'accept': 'application/json'
}

r=session.get(url=url,headers=headers,cookies=cook)


print("===== get resp text=========")
print(r.text)
print("===== get resp header=========")
print(r.headers)
print("===== get resp cookies=========")
cook=r.cookies
print(cook)
print(cook.get_dict())

session.cookies.clear()

session.close()

exit()