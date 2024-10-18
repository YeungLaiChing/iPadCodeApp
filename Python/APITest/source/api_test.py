from flask import Flask, jsonify, request
from datetime import datetime
import requests
import json

import time
import os


listening_port=int(os.environ.get('LISTENING_PORT', '80'))

app = Flask(__name__)

server="https://core.hkexstaging.datahex.rozettatech.com"

@app.route('/apiLoginToken', methods=['POST'])
def login_token():
    username="laichingyeung@hkex.com.hk"
    password="P@ssw0rd!"

    url= "/realms/datahex/protocol/openid-connect/token"
    headers = {
        'Content-Tpye':'application/x-www-form-urlencoded'
    }

    payloads = {
        "grant_type": "password",
        "username": username,
        "password": password,
        "client_id": "frontend_client"
    }

    r = requests.post(url=url, headers=headers, data=payloads)

    if (r.status_code==200):
        result=r.json().get('access_token')
        print(result)
        return result,200
    else :
        print(result)
        return r.text,400
   
  
@app.route('/apiTestPost', methods=['POST'])
def api_test():
    method="POST"
    content_server=request.form.get('server')
    content_url=request.form.get('url')
    content_header=json.loads(request.form.get('header'))
    content_data=json.loads(request.form.get('data'))
    r=requests.post(url=f"{content_server}{content_url}",headers=content_header,json=content_data)
    return r.text,r.status_code
   
  
@app.route('/apiTestPostJson', methods=['POST'])
def api_test_json():
    data=request.json()
    method="POST"
    content_server=data.get('server')
    content_url=data.get('url')
    content_header=json.loads(data.get('header'))
    content_data=json.loads(data.get('data'))
    r=requests.post(url=f"{content_server}{content_url}",headers=content_header,json=content_data)
    return r.text,r.status_code

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=listening_port,debug=True)