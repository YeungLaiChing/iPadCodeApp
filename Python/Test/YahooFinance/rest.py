import requests
import json


import requests


def get_yahoo_cookie():
    cookie = None

    user_agent_key = "User-Agent"
    user_agent_value = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"

    headers = {user_agent_key: user_agent_value}
    response = requests.get(
        "https://fc.yahoo.com", headers=headers, allow_redirects=True
    )

    if not response.cookies:
        raise Exception("Failed to obtain Yahoo auth cookie.")

    cookie = list(response.cookies)[0]

    return cookie


def get_yahoo_crumb(cookie):
    crumb = None

    user_agent_key = "User-Agent"
    user_agent_value = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"

    headers = {user_agent_key: user_agent_value}

    crumb_response = requests.get(
        "https://query1.finance.yahoo.com/v1/test/getcrumb",
        headers=headers,
        cookies={cookie.name: cookie.value},
        allow_redirects=True,
    )
    crumb = crumb_response.text

    if crumb is None:
        raise Exception("Failed to retrieve Yahoo crumb.")

    return crumb

def get_yahoo_data(crumb_number):
    url = f"https://query1.finance.yahoo.com/v7/finance/quote?&symbols=BTC-USD&fields=currency,regularMarketChange,regularMarketChangePercent,regularMarketPrice&crumb={crumb_number}"
    r=requests.get(url=url,cookies=cookies)
    print("===== GET resp text=========")
    print(r.text)

# Usage
cookie = get_yahoo_cookie()
crumb = get_yahoo_crumb(cookie)
get_yahoo_data(crumb_number=crumb)