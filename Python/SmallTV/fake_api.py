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
  current=int(time.time()/24/3600)*24*3600-8*3600
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
    if (symbol in append_list):
      val=redis_conn.hget(f"{symbol}-USD","last_index")
    else:
       val=redis_conn.hget(symbol,"last_index")
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
  ],
  [1725148800000, "0","0","0","0",
    "20705.15741000",
    1725235199999, "1202176847.39105850",
    2153180, "9651.50531000",
    "560452387.89854740",
    "0"
  ],
  [1725235200000, "0","0","0","0",
    "22895.01461000",
    1725321599999, "1333092369.44656860",
    1966119, "11295.25452000",
    "657496577.63048030",
    "0"
  ],
  [1725321600000, "0","0","0","0",
    "22828.18447000",
    1725407999999, "1335076815.85992480",
    2208758, "10979.79204000",
    "642252673.11321130",
    "0"
  ],
  [1725408000000, "0","0","0","0",
    "35560.82146000",
    1725494399999, "2027630870.17967540",
    3177549, "16861.75483000",
    "961923197.77825300",
    "0"
  ],
  [1725494400000, "0","0","0","0",
    "27806.91413000",
    1725580799999, "1577770853.10079750",
    3368058, "12955.88970000",
    "734996919.35909540",
    "0"
  ],
  [1725580800000, "0","0","0","0",
    "54447.76826000",
    1725667199999, "2988914918.92433420",
    5287281, "25325.18849000",
    "1390546230.88109310",
    "0"
  ],
  [1725667200000, "0","0","0","0",
    "16694.04774000",
    1725753599999, "905693342.58983220",
    1920923, "8023.90683000",
    "435381439.00959560",
    "0"
  ],
  [1725753600000, "0","0","0","0",
    "16274.14779000",
    1725839999999, "885743172.91847590",
    1796092, "8031.76084000",
    "437221897.11041520",
    "0"
  ],
  [1725840000000, "0","0","0","0",
    "32384.51737000",
    1725926399999, "1809715390.04932940",
    3355912, "16412.83148000",
    "917669512.22202930",
    "0"
  ],
  [1725926400000, "0","0","0","0",
    "23626.78126000",
    1726012799999, "1349365460.09005710",
    2843148, "11690.37506000",
    "667774722.69939110",
    "0"
  ],
  [1726012800000, "0","0","0","0",
    "33026.56757000",
    1726099199999, "1875738697.37841530",
    4045103, "15979.30786000",
    "907634258.56498910",
    "0"
  ],
  [1726099200000, "0","0","0","0",
    "31074.40631000",
    1726185599999, "1802848638.07570170",
    3706764, "14783.00418000",
    "857572456.51008690",
    "0"
  ],
  [1726185600000,"0","0","0","0",
    "29825.23333000",
    1726271999999, "1760671733.54929960",
    3378012, "15395.13731000",
    "909141733.97476540",
    "0"
  ],
  [1726272000000, "0","0","0","0",
    "12137.90901000",
    1726358399999, "728527024.34169630",
    1288784, "5570.22098000",
    "334303099.74321360",
    "0"
  ],
  [1726358400000, "0","0","0","0",
    "13757.92361000",
    1726444799999, "822410872.39069560",
    1552950, "6431.24697000",
    "384460724.57039670",
    "0"
  ],
  [1726444800000, "0","0","0","0",
    "26477.56420000",
    1726531199999, "1543273198.70274520",
    3145152, "12859.75840000",
    "749563220.80605080",
    "0"
  ],
  [1726531200000, "0","0","0","0",
    "33116.25878000",
    1726617599999, "1983378424.77570380",
    3918209, "16390.65993000",
    "981860543.27358150",
    "0"
  ],
  [1726617600000, "0","0","0","0",
    "36087.02469000",
    1726703999999, "2174000496.82077610",
    5167671, "18429.59712000",
    "1110622778.75108520",
    "0"
  ],
  [1726704000000, "0","0","0","0",
    "34332.52608000",
    1726790399999, "2153175931.17387170",
    4438284, "17609.62958000",
    "1104427424.52469690",
    "0"
  ],
  [1726790400000, "0","0","0","0",
    "25466.37794000",
    1726876799999, "1611195963.99080440",
    3969296, "12411.32227000",
    "785440558.81257280",
    "0"
  ],
  [1726876800000, "0","0","0","0",
    "8375.34608000",
    1726963199999, "528657852.31830240",
    1283611, "3877.73743000",
    "244802615.78455930",
    "0"
  ],
  [1726963200000,"0","0","0","0",
    "1194.45466000",
    1727049599999, "75438422.12066640",
    213500, "497.48718000",
    "31430859.34588920",
    "0"
  ]
]
    return ret
    
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
    app.run(host="0.0.0.0",port=listening_port,debug=False)