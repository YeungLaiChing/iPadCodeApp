from flask import Flask, jsonify, request
from datetime import datetime

import time
import pymongo
import os

mongodb_url=os.environ.get('CONFIG_MONGODB_URL', 'mongodb://testing:testing@192.168.0.9:27017/')
listening_port=int(os.environ.get('LISTENING_PORT', '5000'))

client=pymongo.MongoClient(mongodb_url)

db=client["etf_db"]

table=db["etf_aum_table"]

app = Flask(__name__)

@app.route('/aum', methods=['GET'])
def get_aum():
    
    if request.args.get("date"):
        date=request.args.get("date")
        print(f"Searching result by given date {date} ...")
        results=db["etf_aum_table"].find({"Date":date})
    else :
        results=db["etf_latest_aum_table"].find()
    
    return_val=[]
    for result in results:
        r={
            "Date":result["Date"],
            "Stock":f'{result["Stock"]}.HK',
            "AUM":result["AUM"],
            "URL":result["Z-Link"]
        }
        return_val.append(r)
    
    return jsonify({'aum': return_val})


@app.route('/vol', methods=['GET'])
def get_vol():
    
    if request.args.get("date"):
        date=request.args.get("date")
        print(f"Searching result by given date {date} ...")
        results=db["etf_vol_table"].find({"Date":date})
    else :
        results=db["etf_latest_vol_table"].find()
    
    return_val=[]
    for result in results:
        r={
            "Date":result["Date"],
            "Stock":f'{result["Stock"]}.HK',
            "Vol":result["Vol"]
        }
        return_val.append(r)
    
    return jsonify({'vol': return_val})



if __name__ == '__main__':
    app.run(host="0.0.0.0",port=listening_port,debug=True)