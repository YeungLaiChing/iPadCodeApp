import json
import threading
from datetime import datetime, timezone, timedelta
import requests
import time

lock=threading.Lock()
def get_current_time():
    return datetime.fromtimestamp(int(time.time()+8*3600), tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

            

def process_message(message):

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
            print(f"{route} , {dest_tc} , {eta},{timestamp}")
    except json.JSONDecodeError as e:
        print(f"{get_current_time()}: JSON decode error: {e}")
    except IOError as e:
        print(f"{get_current_time()}: IOError: {e}")
        
            
def get_data():
    
    stop_id="E92E009DE3307F85"
    stop_id="B3F2EC8E42FA3184"
    route="98"
    
    #峻瀅	B3F2EC8E42FA3184
    #首都	E92E009DE3307F85
    
    
    
    if True:
        
        #resp = requests.get(f'https://data.etabus.gov.hk/v1/transport/kmb/eta/{stop_id}/{route}/1')
        resp = requests.get(f'https://data.etabus.gov.hk/v1/transport/kmb/stop-eta/{stop_id}')
                    
        if resp.status_code==200 :
            content=resp.json()
            if "message" in content: 
                print(f"Reponse  error {content['message']}")
                exit()
            else:
                process_message(content["data"])
                time.sleep(1)
        else:
            print(f"Reponse Status error {resp.status_code}")
            
            exit()
    
if __name__ == "__main__":
    get_data()
    