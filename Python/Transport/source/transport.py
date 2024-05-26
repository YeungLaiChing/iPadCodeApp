from flask import Flask
import json
from datetime import datetime, timezone
import requests
import time

import os
listening_port=int(os.environ.get('LISTENING_PORT', '5009'))
app = Flask(__name__)

header='<meta name="viewport" content="width=device-width; initial-scale=1.0; maximum-scale=1.0; minimum-scale=1.0; user-scalable=0;" /><meta name="apple-mobile-web-app-capable" content="yes" />'

def get_current_time():
    return datetime.fromtimestamp(int(time.time()+8*3600), tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

def process_city_message(message):
    result=[]
    try:
        for data in message:

            company = data['co']
            route = data['route']
            eta = data['eta']
            dest_en = data['dest']
            timestamp=""
            if eta :
                timestamp = int((datetime.strptime(eta,'%Y-%m-%dT%H:%M:%S+08:00').timestamp()-int(time.time()))/60)
            #print(f"{route} , {dest_en} , {eta},{timestamp}")
                item={
                    "company":"CTB",
                    "route":route,
                    "dest":dest_en,
                    "eta":eta,
                    "minutes":timestamp
                }
                result.append(item)
            
    except json.JSONDecodeError as e:
        print(f"{get_current_time()}: JSON decode error: {e}")
    except IOError as e:
        print(f"{get_current_time()}: IOError: {e}")
    return result
            
def grep_city_bus(stop_id):
    
    #stop_id="E92E009DE3307F85"
    #stop_id="002929"
    #route="98"
    
    #峻瀅	002919
    #首都	002929
    
    result=[]
    
    if True:
        
        #resp = requests.get(f'https://data.etabus.gov.hk/v1/transport/kmb/eta/{stop_id}/{route}/1')
        resp = requests.get(f'https://rt.data.gov.hk/v1/transport/batch/stop-eta/CTB/{stop_id}?lang=zh-hant')
                    
        if resp.status_code==200 :
            content=resp.json()
            if "message" in content: 
                print(f"Reponse  error {content['message']}")
                return result
            else:
                result=process_city_message(content["data"])
                
                return result
        else:
            print(f"Reponse Status error {resp.status_code}")
            
            return result
    

def process_kmb_message(message):
    result=[]
    try:
        for data in message:

            company = data['co']
            route = data['route']
            eta = data['eta']
            dest_tc = data['dest_tc']
            dest_en = data['dest_en']
            timestamp=""
            if eta :
                timestamp = int((datetime.strptime(eta,'%Y-%m-%dT%H:%M:%S+08:00').timestamp()-int(time.time()))/60)
                item={
                    "company":"KMB",
                    "route":route,
                    "dest":dest_tc,
                    "eta":eta,
                    "minutes":timestamp
                }
                result.append(item)
    except json.JSONDecodeError as e:
        print(f"{get_current_time()}: JSON decode error: {e}")
    except IOError as e:
        print(f"{get_current_time()}: IOError: {e}")
    return result
            
def grep_kmb(stop_id):
    result=[]
    
    #峻瀅	B3F2EC8E42FA3184
    #首都	E92E009DE3307F85
    
    
    
    if True:
        
        #resp = requests.get(f'https://data.etabus.gov.hk/v1/transport/kmb/eta/{stop_id}/{route}/1')
        resp = requests.get(f'https://data.etabus.gov.hk/v1/transport/kmb/stop-eta/{stop_id}')
                    
        if resp.status_code==200 :
            content=resp.json()
            if "message" in content: 
                print(f"Reponse  error {content['message']}")
                return result
            else:
                result=process_kmb_message(content["data"])
                return result
        else:
            print(f"Reponse Status error {resp.status_code}")
            
            return result

def process_mtr_message(message):
    result=[]
    try:
        for data in message:
            company = "MTR"
            route = 'LHP'
            eta = data['time']
            timestamp = int((datetime.strptime(eta,'%Y-%m-%d %H:%M:%S').timestamp()-int(time.time()))/60)
            dest_en = data['dest']
            #print(f"{route} , {dest_en} , {eta}, {timestamp}")
            item={
                    "company":"MTR",
                    "route":route,
                    "dest":dest_en,
                    "eta":eta,
                    "minutes":timestamp
                }
            result.append(item)
    except json.JSONDecodeError as e:
        print(f"{get_current_time()}: JSON decode error: {e}")
    except IOError as e:
        print(f"{get_current_time()}: IOError: {e}")
    return result
            
def grep_mtr(stop_id):
        result=[]

        #resp = requests.get(f'https://data.etabus.gov.hk/v1/transport/kmb/eta/{stop_id}/{route}/1')
        resp = requests.get(f'https://rt.data.gov.hk/v1/transport/mtr/getSchedule.php?line=TKL&sta={stop_id}&lang=TC')
                    
        if resp.status_code==200 :
            content=resp.json()
            if "error" in content: 
                print(f"Reponse  error {content['error']}")
                return result
            else:
                result=process_mtr_message(content["data"]["TKL-LHP"]["DOWN"])
                return result
        else:
            print(f"Reponse Status error {resp.status_code}")
            
            return result

def format_bus(route_list,eta_list):
    all={}
    route_array=route_list.split(",")
    
    for eta in eta_list:
        if eta["route"] in route_array or len(route_list)==0:
            if eta["route"] in all.keys():
                tmp=all[eta["route"]]
                t=f"{eta["minutes"]}({eta["company"]})"
                if t != all[eta["route"]]["last"]:
                    
                    all[eta["route"]]={"dest":eta["dest"],"eta":f"{all[eta["route"]]["eta"]} , {eta["minutes"]}({eta["company"]})","last":f"{eta["minutes"]}({eta["company"]})"}
                
            else :
                all[eta["route"]]={"dest":eta["dest"],"eta":f"{eta["minutes"]}({eta["company"]})","last":f"{eta["minutes"]}({eta["company"]})"}
    return all

@app.route('/route', methods=['GET'])
def get_route():
    result=get_result("ba","")
    output="<tr><td>路線</td><td>終點站</td><td>預計到站時間（分鐘）</td></tr>"
    for item in result.keys():
        output=f"{output}<tr><td>{item}</td><td>{result[item]["dest"]}</td><td>{result[item]["eta"]}</td></tr> "
   
    return f"<html><head>{header}</head><body><h1>峻瀅 ({get_current_time()})</h1><table border=1 margin='0 auto'>{output}</table></body></html>"
        
      
@app.route('/route_capitol', methods=['GET'])
def get_route_capitol():
    result=get_result("capitol","")
    output="<tr><td>Route</td><td>Destination</td><td>ETA</td></tr>"
    output="<tr><td>路線</td><td>終點站</td><td>預計到站時間（分鐘）</td></tr>"
    for item in result.keys():
        output=f"{output}<tr><td>{item}</td><td>{result[item]["dest"]}</td><td>{result[item]["eta"]}</td></tr> "
    return f"<html><head>{header}</head><body><h1>首都 ({get_current_time()})</h1><table border=1 margin='0 auto'>{output}</table></body></html>"
        
  
def get_result(stop_id,route):
    #峻瀅	002919
    #首都	002929
    city_bus_list={}
    city_bus_list["capitol"]="002929"
    city_bus_list["ba"]="002919"
    kmb_bus_list={}
    kmb_bus_list["capitol"]="E92E009DE3307F85"
    kmb_bus_list["ba"]="B3F2EC8E42FA3184"

    
    bus=[]
    bus.extend(grep_city_bus(city_bus_list[stop_id]))
    bus.extend(grep_kmb(kmb_bus_list[stop_id]))
    bus.extend(grep_mtr("LHP"))
    bus = sorted(bus, key=lambda x: float(x['minutes']))
    
    return format_bus(route,bus)
    
    
    

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=listening_port,debug=True)