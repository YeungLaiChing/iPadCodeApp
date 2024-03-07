from futu import *
import time
from datetime import datetime
import json
from pathlib import Path
import logging.config
import requests
from datetime import date, timedelta

#target_date = date.today() - timedelta(1)
target_date = date.today() 

file_path = Path(__file__).with_name("config.json")
f = open (file_path, "r")
hs_tech_leverage_index_config = json.loads(f.read())
f.close()

resp = requests.get(f'https://www.hkab.org.hk/api/hibor?year={target_date.year}&month={target_date.month}&day={target_date.day}').json()
hs_tech_leverage_index_config["overnight_interest_pct"]=str(resp["Overnight"]);


quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret_sub, err_message = quote_ctx.subscribe(['HK.800700','HK.800868'], [SubType.QUOTE], subscribe_push=False)
# Subscribe to the K line type first. After the subscription is successful, Futu OpenD will continue to receive pushes from the server, False means that there is no need to push to the script temporarily
if ret_sub == RET_OK: # Subscription successful
     ret, data = quote_ctx.get_stock_quote(['HK.800700']) # Get real-time data of subscription stock quotes
     if ret == RET_OK:
         hs_tech_leverage_index_config["underly_index_previous"]=str(data['last_price'][0])
         hs_tech_leverage_index_config["last_calc_date"]=str(data['data_date'][0])
     else:
         print('error:', data)
         
     ret, data = quote_ctx.get_stock_quote(['HK.800868']) # Get real-time data of subscription stock quotes
     if ret == RET_OK:
         hs_tech_leverage_index_config["this_index_previous"]=str(data['last_price'][0])
         hs_tech_leverage_index_config["last_calc_date"]=str(data['data_date'][0])
     else:
         print('error:', data)
else:
     print('subscription failed', err_message)
quote_ctx.close() # Close the current connection, Futu OpenD will automatically cancel the corresponding type of subscription for the corresponding stock after 1 minute




new_file_path = Path(__file__).with_name(f"config_{time.strftime('%Y%m%d_%H%M%S')}.json")
f = open(new_file_path, 'w', encoding='utf-8')
json.dump(hs_tech_leverage_index_config, f, ensure_ascii=False, indent=4)
f.close()


