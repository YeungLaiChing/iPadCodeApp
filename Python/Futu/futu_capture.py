import time
from futu import *
from zoneinfo import ZoneInfo

output_path=f'output.{time.strftime("%Y%m%d-%H%M%S")}.csv'

def getFormattedTime(ns):
    dt = datetime.fromtimestamp(ns//1000000000)
    formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
    nanoseconds_part = str(int(ns % 1_000_000_000)).zfill(9)
    formatted_time += '.' + nanoseconds_part
    return formatted_time

class TickerTest(TickerHandlerBase):
    def on_recv_rsp(self, rsp_pb):
        ret_code, data = super(TickerTest,self).on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            print("TickerTest: error, msg: %s"% data)
            return RET_ERROR, data
        #print(data.head())
        if isinstance(data, pd.DataFrame):
            ns=getFormattedTime(time.time_ns())
            data['ns']=ns
            data.to_csv(output_path, mode='a', header=not os.path.exists(output_path)) 
        #print(data[['code','price']]) # TickerTest's own processing logic
        return RET_OK, data
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
handler = TickerTest()
quote_ctx.set_handler(handler) # Set real-time push callback

#ret, data = quote_ctx.subscribe(['HK.00005'], [SubType.TICKER]) # Subscribe to the type by transaction, Futu OpenD starts to receive continuous push from the server
ret, data = quote_ctx.subscribe(['HK.00005','HK.800000','HK.800864','HK.800700','HK.HSIcurrent','HK.MHIcurrent'], [SubType.TICKER]) # Subscribe to the type by transaction, Futu OpenD starts to receive continuous push from the server
if ret == RET_OK:
    if isinstance(data, pd.DataFrame):
        ns=getFormattedTime(time.time_ns())
        data['ns']=ns
        data.to_csv(output_path, mode='a', header=not os.path.exists(output_path)) 
else:
    print('error:', data)
time.sleep(23*3600) # Set the script to receive Futu OpenD push duration to 15 seconds
quote_ctx.close() # Close the current link, Futu OpenD will automatically cancel the corresponding type of subscription for the corresponding stock after 1 minute
