from flask import Flask, jsonify, request
from datetime import datetime
import requests
import json

import time
import os
import redis

listening_port=int(os.environ.get('LISTENING_PORT', '80'))
eligible_list={'BTC','ETH','HKBTCI-USD','HKETHI-USD','HKEXBTC-USD','HKEXETH-USD','HKBTCI','HKETHI','HKEXBTC','HKEXETH'}
append_list={'HKBTCI','HKETHI','HKEXBTC','HKEXETH'}

redis_host=os.environ.get('REDIS_HOST', '192.168.0.55')
redis_port=int(os.environ.get('REDIS_PORT', '6379'))

redis_conn = redis.Redis(
    host=redis_host,
    port=redis_port,
    decode_responses=True
)

app = Flask(__name__)
app.json.sort_keys = False
ether=[]
bitcoin=[]
hkbtci=[]
hkethi=[]

@app.route('/test', methods=['GET'])
def get_aum2():
    return get_aum()
  
@app.route('/v1/test/getcrumb', methods=['GET'])
def yahoo_quote_crum():
  ret="4kTCSw9aFp6"
  return ret


@app.route('/v7/finance/quote', methods=['GET'])
def yahoo_quote():
  ret={
    "quoteResponse": {
      "result": [
        {
          #"language": "en-US",
          #"region": "US",
          #"quoteType": "CRYPTOCURRENCY",
          #"typeDisp": "Cryptocurrency",
          #"quoteSourceName": "CoinMarketCap",
          #"triggerable": "true",
          #"customPriceAlertConfidence": "HIGH",
          #"sourceInterval": 15,
          #"exchangeDataDelayedBy": 0,
          #"regularMarketChange": -489.27734,
          #"regularMarketTime": 1728478800,
          #"regularMarketPreviousClose": 62122.836,
          #"hasPrePostMarketData": "false",
          #"firstTradeDateMilliseconds": 1410912000000,
          #"currency": "USD",
          #"exchange": "CCC",
          #"exchangeTimezoneName": "UTC",
          #"exchangeTimezoneShortName": "UTC",
          #"gmtOffSetMilliseconds": 0,
          #"market": "ccc_market",
          #"esgPopulated": "false",
          #"tradeable": "false",
          #"cryptoTradeable": "true",
          #"marketState": "REGULAR",
          "regularMarketChangePercent": -10.78383887,
          "regularMarketPrice": 61931.664,
          #"fullExchangeName": "CCC",
          "symbol": "BTC-USD"
        }
      ],
      "error": "null"
    }
    
  }
  return ret
  
#https://query1.finance.yahoo.com/v7/finance/quote?&symbols=BTC-USD&fields=currency,regularMarketChange,regularMarketChangePercent,regularMarketPrice&crumb=4kTCSw9aFp6

@app.route('/api/v3/uiKlines', methods=['GET'])
def chart():
    symbol=request.args.get('symbol')
    if (symbol in eligible_list) :
      ret=get_kline_from_redis(symbol)
    else :
      ret=get_kline_from_binance(symbol,request.args.get('interval'),request.args.get('limit'))
    return jsonify(ret)
last_time={}
last_close_value={}

def get_close_value_from_rest(symbol):
  global last_close_value
  global last_time
  instrument="BTC-USD"
  if "ETH" in symbol:
    instrument="ETH-USD"
  url=f'https://data-api.ccdata.io/index/cc/v1/historical/days?market=ccix&instrument={instrument}&limit=1'
  resp=requests.get(url)
  rt_val=0;
  if resp.status_code==200 :
      content=resp.json()
      ts=content['Data'][0]['TIMESTAMP']
      rt_val=float(content['Data'][0]['CLOSE'])
      last_close_value[symbol]=rt_val
      last_time[symbol]=ts
      print(f"updated last time {ts} and last close {rt_val} for symbol {symbol}")
  return rt_val
      
def get_close_value(symbol):
  global last_close_value
  global last_time
  current=int(time.time()/24/3600)*24*3600
  rt_val=0;
  if (last_time.get(symbol) is None) or (int(last_time.get(symbol)) != current) :
      rt_val=get_close_value_from_rest(symbol)
  else:
      rt_val=float(last_close_value.get(symbol))
  
  return rt_val;

def get_value_from_binance(symbol):
    url=f'https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}'
    resp=requests.get(url)
    if resp.status_code==200 :
      content=resp.json()
      return content
    
def get_kline_from_binance(symbol,interval,limit):
    url=f'https://api.binance.com/api/v3/uiKlines?symbol={symbol}&interval={interval}&limit={limit}'
    resp=requests.get(url)
    if resp.status_code==200 :
      content=resp.json()
      return content
      
def get_value_from_redis(symbol):
    global hkbtci
    global hkethi
    
    if (symbol in append_list):
        val=redis_conn.hget(f"{symbol}-USD","last_index")
    else:
        val=redis_conn.hget(symbol,"last_index")
    

    val2=[int(time.time()*1000),val,val,val,val,
    "1194.45466000",
    int(time.time()*1000), "75438422.12066640",
    213500, "497.48718000",
    "31430859.34588920",
    "0"
  ]
    if "ETH" in symbol:
      hkethi.append(val2)
      tmp=hkethi[-24:]
      hkethi=tmp
    else :
      hkbtci.append(val2)
      tmp=hkbtci[-24:]
      hkbtci=tmp
    
    close=get_close_value(symbol)
    diff=0;
    if close>0 :
      diff=(float(val)/float(close)-1)*100
    ret={
        "symbol": symbol,
        "priceChangePercent": diff,
        "lastPrice": val
        }
    return ret
def get_kline_from_redis(symbol):
    #val=redis_conn.hget(symbol,"last_index")
    ret=[
      [1724976000000, "0","0","0","0",
        "28519.32195000",
        1725062399999, "1680918972.46584970",
        2845696, "13783.34749000",
        "812769089.28498120",
        "0"
      ],
      [1725062400000,"0","0","0","0",
        "8798.40900000",
        1725148799999, "519849184.86904460",
        895944, "4195.93079000",
        "247955494.35915920",
        "0"
      ]
    ]
    
    global hkethi
    global hkbtci

    ret_all={}
    ret_val=[]
    if "ETH" in symbol :
      for item in hkethi:
        ret_val.append( item)
    else:
      for item in hkbtci:
         ret_val.append( item)
        

    #print(json.dumps(ret_val))
    #ret=json.dumps(ret_val)
      
    return ret_val
    
@app.route('/api/v3/ticker/24hr', methods=['GET'])
def binance():
    symbol=request.args.get('symbol')
    if (symbol in eligible_list) :
      ret=get_value_from_redis(symbol)
    else :
      ret=get_value_from_binance(symbol)
    return jsonify(ret)


@app.route('/v2/assets/<symbol>',methods=['GET'])
def coincap(symbol):
    global ether
    global bitcoin
    ticker="HKBTCI-USD"
    if symbol=="ethereum" :
      ticker="HKETHI-USD"
      
    
    val=redis_conn.hget(ticker,"last_index")
    if symbol=="ethereum" :
      ether.append(val)
      tmp=ether[-60:]
      ether=tmp
    else :
      bitcoin.append(val)
      tmp=bitcoin[-60:]
      bitcoin=tmp
      
    close=get_close_value(ticker)
    diff=0;
    if close>0 :
      diff=(float(val)/float(close)-1)*100
  
    ret={
    "data": {
      "id": symbol,
      "symbol": ticker,
      "name": ticker,
      "priceUsd": val,
      "changePercent24Hr": diff
    },
    "timestamp": 1728565096360
    }
    return ret

@app.route('/v2/assets/<symbol>/history',methods=['GET'])
def coincap_history(symbol):
  global ether
  global bitcoin
  ret={
  "data": [
    {
      "priceUsd": "2440.38"
    }
  ],
  "timestamp": 1728417600000
  }
  ret_all={}
  ret_val=[]
  if symbol=="ethereum" :
    for item in ether:
      ret_val.append({"priceUsd":item})
  else:
    for item in bitcoin:
      ret_val.append({"priceUsd":item})
  ret_all={
      "data": ret_val,
      "timestamp": 1728417600000
  }
  #print(json.dumps(ret_all))
  ret=json.dumps(ret_all)
    
  return ret
@app.route('/data/2.5/weather', methods=['GET'])
def get_aum():
    ret={
        "coord":{
            "lon":114.1667,
            "lat":22.25
        },
        "weather":[
            {
                "id":501,
                "main":"Rain",
                "description":"moderate rain",
                "icon":"10d"
            }
        ],
        "base":"stations",
        "main":{
            "temp":65323.12,
            "feels_like":65323.12,
            "temp_min":55323.12,
            "temp_max":66663.12,
            "pressure":1002,
            "humidity":94,
            "sea_level":1002,
            "grnd_level":995
        },
        "visibility":10000,
        "wind":{
            "speed":3.28,
            "deg":61,
            "gust":5.37
        },
        "rain":{
            "1h":0
        },
        "clouds":{
            "all":0
        },
        "dt":1726895960,
        "sys":{
            "type":2,
            "id":2035800,
            "country":"12:23",
            "sunrise":1726870307,
            "sunset":1726914068
        },
        "timezone":28800,
        "id":1819730,
        "name":"HKETHI",
        "cod":200
    }
    return jsonify(ret)

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=listening_port)