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
            company = "MTR"
            route = 'MTR'
            eta = data['time']
            utc_datetime = datetime.strptime(eta,'%Y-%m-%d %H:%M:%S')
            dest_en = data['dest']
            print(f"{route} , {dest_en} , {eta}, {utc_datetime}")
    except json.JSONDecodeError as e:
        print(f"{get_current_time()}: JSON decode error: {e}")
    except IOError as e:
        print(f"{get_current_time()}: IOError: {e}")
        
            
def get_data():
    
    stop_id="E92E009DE3307F85"
    stop_id="002919"
    route="98"
    
    #https://rt.data.gov.hk/v2/transport/citybus/route-stop/CTB/797/inbound
    
    #峻瀅	002919
    #首都	003827
    
    
    
    if True:
        
        #resp = requests.get(f'https://data.etabus.gov.hk/v1/transport/kmb/eta/{stop_id}/{route}/1')
        resp = requests.get(f'https://rt.data.gov.hk/v1/transport/mtr/getSchedule.php?line=TKL&sta=LHP&lang=TC')
                    
        if resp.status_code==200 :
            content=resp.json()
            if "error" in content: 
                print(f"Reponse  error {content['error']}")
                exit()
            else:
                process_message(content["data"]["TKL-LHP"]["DOWN"])
                time.sleep(1)
        else:
            print(f"Reponse Status error {resp.status_code}")
            
            exit()
    
if __name__ == "__main__":
    get_data()
    