import time
from futu import *
from zoneinfo import ZoneInfo
import redis
import json

from pathlib import Path
file_path = Path(__file__).with_name("config.json")
f = open (file_path, "r")
mv_index_config = json.loads(f.read())
f.close()

topic_name="mv_capture_stream"

output_path=f'./log/market_data.output.{time.strftime("%Y%m%d-%H%M%S")}.csv'
rds = redis.Redis(host='192.168.0.5', port=6379, db=0,decode_responses=True)

def getFormattedTime(ns):
    dt = datetime.fromtimestamp(ns//1000000000)
    formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
    nanoseconds_part = str(int(ns % 1_000_000_000)).zfill(9)
    formatted_time += '.' + nanoseconds_part
    return formatted_time


def handleUpdate(df):
    if isinstance(df,pd.DataFrame):
        handleDfUpdate(df)
    else:
        print(df)

def handleDfUpdate(df):
    ns=time.time_ns()
    df['ns']=ns
    for index, row in df.iterrows():
        record=row.to_json()
        rds.set(row['code']+'_quote',record)
        rds.publish(topic_name,record)
    df.to_csv(output_path, mode='a', header=not os.path.exists(output_path)) 


class StockQuoteTest(StockQuoteHandlerBase):
    def on_recv_rsp(self, rsp_pb):
        ret_code, data = super(StockQuoteTest,self).on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            print("StockQuoteTest: error, msg: %s" % data)
            return RET_ERROR, data
        #print("StockQuoteTest ", data) # StockQuoteTest 自己的处理逻辑
        handleUpdate(data)
        return RET_OK, data
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
handler = StockQuoteTest()
quote_ctx.set_handler(handler)  # 设置实时报价回调
ret, data = quote_ctx.subscribe(['HK.00700', 'HK.09988', 'HK.03690', 'HK.01810', 'HK.02015', 'HK.09618', 'HK.01024', 'HK.09999', 'HK.00981', 'HK.09888', 'HK.00992', 'HK.06690', 'HK.09961', 'HK.09868', 'HK.02382', 'HK.06618', 'HK.00285', 'HK.00268', 'HK.00780', 'HK.09626', 'HK.03888', 'HK.00241', 'HK.00020', 'HK.01347', 'HK.01797', 'HK.06060', 'HK.00772', 'HK.01833', 'HK.09866', 'HK.09898'], [SubType.QUOTE])  # 订阅实时报价类型，OpenD 开始持续收到服务器的推送
if ret == RET_OK:
    handleUpdate(data)
    #print(data)
else:
    print('error:', data)
time.sleep(8*3600)  #  设置脚本接收 OpenD 的推送持续时间为15秒
quote_ctx.close()   # 关闭当条连接，OpenD 会在1分钟后自动取消相应股票相应类型的订阅    	

rds.publish(topic_name,"SHUTDOWN")

time.sleep(10) 