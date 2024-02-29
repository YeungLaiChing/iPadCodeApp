from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import time
import redis
import datetime
import json 

ISOTIMEFORMAT = '%H:%M:%S'

r = redis.Redis(
    host='192.168.0.5',
    port=6379,
    db=0
    #decode_responses=True # <-- this will ensure that binary data is decoded
)

def trigger_job():
    print('trigger_job in fixed interval')
    ns = str(time.time_ns() )
    t = datetime.datetime.now().strftime(ISOTIMEFORMAT)
    payload = {'IndexTime' : t, 'ns' : ns}
    r.publish("army-camp-1",json.dumps(payload))
    
    
if __name__ == '__main__':
    sched = BackgroundScheduler(timezone='UCT')
    
    trigger = CronTrigger(
        year="*", month="*", day="*", hour="*", minute="*", second="*"
    )
    sched.add_job(
        trigger_job,
        trigger=trigger,
        args=[],
        name="trigger job",
    )  
    #sched.add_job(job2,'interval',id='2_sec',seconds=15)
    sched.start()
    
    while (True):
       # print('main 1s')
        time.sleep(100)
        