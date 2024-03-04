import json
import os

from pathlib import Path
file_path = Path(__file__).with_name("config.json")

f = open (file_path, "r")

hs_tech_leverage_index_config = json.loads(f.read())

f.close()


def calculateLeveragedIndex(underly_index_current):
    result=0

    K=float(hs_tech_leverage_index_config["leverage_ratio"])
    DayCount=float(hs_tech_leverage_index_config["number_calendar_days"])
    N=float(365)
    StampDuty=float(hs_tech_leverage_index_config["stamp_duty_pct"])
    Interest=float(hs_tech_leverage_index_config["overnight_interest_pct"])
    UnderlyIndexClose=float(hs_tech_leverage_index_config["underly_index_previous"])
    IndexClose=float(hs_tech_leverage_index_config["this_index_previous"])
    UnderlyIndexCode=hs_tech_leverage_index_config["underly_index_code"]
    
    AmplifiedReturn = K * (underly_index_current / UnderlyIndexClose -1 )
    InterestExpense=(K-1)*(Interest/100/N)*DayCount
    StampDutyExpense = K * (K-1) * abs(underly_index_current / UnderlyIndexClose -1)*(StampDuty/100)
    LeveragedIndexReturn = AmplifiedReturn - InterestExpense - StampDutyExpense
    CurrentIndex  = round(IndexClose * (1 + LeveragedIndexReturn),2)
    return CurrentIndex

def calculateLeveragedIndex2(underly_index_current):
    result=0


    K=float(hs_tech_leverage_index_config["leverage_ratio"])
    DayCount=float(hs_tech_leverage_index_config["number_calendar_days"])
    N=float(365)
    StampDuty=float(hs_tech_leverage_index_config["stamp_duty_pct"])
    Interest=float(hs_tech_leverage_index_config["overnight_interest_pct"])
    UnderlyIndexClose=float(hs_tech_leverage_index_config["underly_index_previous"])
    IndexClose=float(hs_tech_leverage_index_config["this_index_previous"])
    UnderlyIndexCode=hs_tech_leverage_index_config["underly_index_code"]
    
    AmplifiedReturn = round(K * round(round(underly_index_current / UnderlyIndexClose,9) -1 ,9),9)
    InterestExpense=round(round((K-1)*round(Interest/100/N,9),9)*DayCount,9)
    StampDutyExpense = round(round(K * (K-1),9) * abs(round(round(underly_index_current / UnderlyIndexClose,9) -1,9))*(StampDuty/100),9)
    LeveragedIndexReturn = AmplifiedReturn - InterestExpense - StampDutyExpense
    CurrentIndex  = round(IndexClose * (1 + LeveragedIndexReturn),2)
    return CurrentIndex


print(calculateLeveragedIndex(3474.77))
print(calculateLeveragedIndex2(3474.77))
