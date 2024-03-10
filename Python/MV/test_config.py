import json
import os
from datetime import date

from pathlib import Path
file_path = Path(__file__).with_name("config.json")

f = open (file_path, "r")

mv_index_config = json.loads(f.read())

f.close()



def calc_stock_mv(issued_shares,faf,cf,price,fx):
    result=round(round(round(float(issued_shares)*float(faf)*float(cf),0)*float(price),0)*float(fx),0)
    return result

def calc_current_index_mv(con_list):
    result=0
    for stock in con_list:
        result=result+calc_stock_mv(stock["issued_shares"],stock["faf"],stock["cf"],stock["current_price"],1)
    return result

def cal_index_by_mv(current_mv,last_mv,last_index):
    result=round(current_mv/last_mv*last_index,2)
    return result

def calc_index_by_divisor(current_mv,divisor):
    result=round(current_mv/divisor,2)
    return result

print(mv_index_config["last_calc_date"])
print(len(mv_index_config["constituents_list"]))
print(mv_index_config["constituents_list"][0]["stock_code"])
if mv_index_config["constituents_list"][0].get("cap_mv") is None:
    mv_index_config["constituents_list"][0]["cap_mv"]=123

print(mv_index_config["constituents_list"][0]["cap_mv"])
print(calc_current_index_mv(mv_index_config["constituents_list"]))

print(mv_index_config["list"]["0005.HK"]["futu_code"])
