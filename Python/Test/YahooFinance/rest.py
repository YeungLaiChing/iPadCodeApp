import requests
import json
# login
crumb = "https://query1.finance.yahoo.com/v1/test/getcrumb"

#'Content-Tpye':'application/json',
#'accept': 'application/json',
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/42.0'
}

r = requests.get(url=crumb,headers=headers)
print("===== login resp text=========")
print(r.text)
print("===== login resp header=========")
print(r.headers)
print("===== login resp cookies=========")
cookies=r.cookies
print(cookies)

crumb_number="ABC"
#get data
url = f"https://query1.finance.yahoo.com/v7/finance/quote?&symbols=BTC-USD&fields=currency,regularMarketChange,regularMarketChangePercent,regularMarketPrice&crumb={crumb_number}"
#r=requests.get(url=url,cookies=cookies)
#print("===== GET resp text=========")
#print(r.text)


