import os
import sys

import ccxt
import time
import datetime
import pandas as pd
import numpy as np
import queue
import threading
import websocket
import math
import requests

import  json

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1200)

if not os.path.isdir('su_record'): os.mkdir('su_record')
if not os.path.isdir('query_record'): os.mkdir('query_record')
if not os.path.isdir('df_record'): os.mkdir('df_record')

def round_down(number, decimals=0):
    factor = 10 ** decimals
    return math.floor(number * factor) / factor

def place_order_and_record(action,
                           trd_side,
                           bid_ask_data,
                           equity_value,
                           exchange,
                           code,
                           unique_id,
                           trade_status_df
                           ):
    top_up = 8

    if trd_side == 'buy':
        action_price = bid_ask_data['asks'][top_up][0]
        qty = round_down((equity_value / action_price), 6)

    elif trd_side == 'sell':
        action_price = bid_ask_data['bids'][top_up][0]
        qty = float(pd.read_csv("su_record/"+unique_id+"_trade_status.csv")["qty"].iloc[-1])


    data = exchange.create_order(symbol = code +"/USDT", type = "limit", side = trd_side, amount = qty, price = action_price)

    order_id = data["info"]["orderId"]
    ### must wait at least 5 sec to update order_list ###
    time.sleep(25)

    data = exchange.fetch_order(order_id, symbol = code +"/USDT")
    # data2 = exchange.fetch_order_trades(order_id, symbol = code +"/USDT")
    # data2 = (pd.DataFrame([data2[0]['info']]))
    # data2 = data2.reset_index(drop=True)

    msg = 'code: ' + code + '\n' \
          + 'qty: ' + str(qty) + '\n' \
          + 'trd_side: ' + trd_side + '\n' \
          + 'unique_id: ' + unique_id + '\n' \
          + 'order_id: ' + order_id + '\n' \
          + 'action_price: ' + str(action_price) + '\n'

    ###### record ######

    order_status = data["info"]["status"]
    if trd_side == "buy":
        comission = float(data["filled"]) * 0.001
        dealt_qty = float(data["filled"]) - comission
    if trd_side == "sell":
        comission = float(data["info"]["cummulativeQuoteQty"]) * 0.001
        dealt_qty = float(data["info"]["cummulativeQuoteQty"])- comission
    dealt_avg_price = float(data["average"])
    open_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


    if order_status == 'FILLED' and trd_side == "buy":

        trade_status_df.at[0, 'qty'] = dealt_qty
        trade_status_df.at[0, 'cost_price'] = dealt_avg_price
        trade_status_df.at[0, 'open_datetime'] = open_datetime
        trade_status_df.at[0, 'last_realized_capital'] = (float(dealt_avg_price)*float(dealt_qty) - float(dealt_avg_price)*float(dealt_qty)*0.001)
        msg = 'ORDER COMPLETED\n' + msg \
              + 'dealt_avg_price: ' + str(dealt_avg_price) + '\n' \
              + 'last_realized_capital: ' + str(trade_status_df.at[0, 'last_realized_capital']) + '\n' \
              + 'order_status: ' + order_status

        send_tg(msg)

    elif order_status == 'FILLED' and trd_side == "sell":

        trade_status_df.at[0, 'qty'] = 0
        trade_status_df.at[0, 'cost_price'] = dealt_avg_price
        trade_status_df.at[0, 'open_datetime'] = open_datetime
        trade_status_df.at[0, 'last_realized_capital'] = dealt_qty
        msg = 'ORDER COMPLETED\n' + msg \
              + 'dealt_avg_price: ' + str(dealt_avg_price) + '\n' \
              + 'last_realized_capital: ' + str(trade_status_df.at[0, 'last_realized_capital']) + '\n' \
              + 'order_status: ' + order_status+ '\n' \

        send_tg(msg)


    else:
        msg = 'ORDER FAILED\n' + msg \
              + 'dealt_qty: ' + str(dealt_qty) + '\n' \
              + 'dealt_avg_price: ' + str(dealt_avg_price) + '\n' \
              + 'order_status: ' + order_status
        send_tg(msg)

    return trade_status_df, dealt_qty


def send_tg(msg):
    msg = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S: ') + msg
    url = 'https://api.telegram.org/{bottoken}/sendMessage?chat_id=-{chatid}&text='
    requests.get(url + msg)
    print(msg)
    print('----------------')

def single_contract_run(exchange, code, para_rows, check_func_dict):
        quote = code+"/USDT"
        time.sleep(1)
        temp_cond = True
        while True:

            now_datetime = datetime.datetime.now()
            now_weekday = now_datetime.weekday()
            now_date_str = now_datetime.strftime('%Y-%m-%d')
            now_hhmmss = now_datetime.strftime('%H:%M:%S')
            now_datetime_str = now_date_str + ' ' + now_hhmmss
            now_hhmmss_int = int(now_hhmmss.replace(':', ''))
            now_ss_int = int(now_datetime.strftime('%S'))
            now_mm_int = int(now_datetime.strftime('%M'))

            # if now_mm_int % 5 == 0 and now_ss_int == 0:
            #     print('thread of:', code, 'now_hhmmss', now_hhmmss)

            for i in range(len(para_rows)):
                para_pairs = para_rows.at[i, 'para'].split('|')
                unique_id = para_rows.at[i, 'unique_id']
                strategy_name = para_rows.at[i, 'strategy_name']
                action_time_mm = int(para_rows.at[i, 'action_time_mm'])
                action_time_ss = para_rows.at[i, 'action_time_ss']

                ########################################## UPDATE ACTION TIME BY STRA ##########################################
            if  action_time_mm == now_mm_int and action_time_ss == now_ss_int:
                ########################################## #####################################################################

                para_combination = {'strategy_name': strategy_name, 'code': code, 'unique_id': unique_id, "exchange": exchange}
                print('ready to check trade logic: ', code, strategy_name)
                for item in para_pairs:
                    key, value = item.split('=')
                    para_combination[key] = value

                ########### check specific trade logic here ###########
                check_function = check_func_dict[strategy_name]
                check_function(para_combination)
                #######################################################
                time.sleep(1)


def get_interest_rates(start_date, end_date, coin, intra_day):
    all_data = []

    # Convert start_date and end_date strings to datetime objects
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")

    current_date = start_date
    while current_date <= end_date:
        url = "https://www.binance.com/bapi/margin/v1/public/margin/vip/spec/history-interest-rate"
        params = {
            "asset": f"{coin}",
            "vipLevel": 0,
            "startTime": int(current_date.timestamp() * 1000),
            "endTime": int((current_date + datetime.timedelta(days=30)).timestamp() * 1000)
        }

        response = requests.get(url, params=params)
        data = response.json()

        # Append the data to the list
        all_data.extend(data["data"])

        # Move to the next month
        current_date += datetime.timedelta(days=30)

    df = pd.DataFrame(all_data)
    # Size reduce
    df = df.drop("vipLevel", axis=1)
    # Adding datetime column
    df = df.sort_values(by="timestamp", ascending=True)
    # Convert "dailyInterestRate" column to numeric dtype
    df["timestamp"] = pd.to_numeric(df["timestamp"])
    df["dailyInterestRate"] = pd.to_numeric(df["dailyInterestRate"])

    df.insert(2, "DateTime", pd.to_datetime(df["timestamp"], unit="ms"))
    df.drop_duplicates(subset='timestamp', keep='first', inplace=True)

    if intra_day:
        df["dailyInterestRate"] = df["dailyInterestRate"]*365
        df = df[["DateTime", "dailyInterestRate"]]
        return df
    else:
        # Convert "timestamp" column to datetime type
        df["DateTime"] = pd.to_datetime(df["timestamp"], unit="ms")
        # Drop duplicated interest rate within a day
        df = df.loc[df.groupby(df["date"].dt.date)["dailyInterestRate"].idxmax()]
        df["dailyInterestRate"] = df["dailyInterestRate"]*365
        df = df[["date", "dailyInterestRate"]]
        return df


def str_to_int(name):
    unique_id = str(int.from_bytes(name.encode(), 'little'))
    if len(unique_id) > 10:
        unique_id = unique_id[0:10] + unique_id[-10:]
    elif len(unique_id) < 10:
        unique_id = unique_id.zfill(0)

    return unique_id

def interest_zscore(para_combination):

    now_datetime = datetime.datetime.now()
    now_date_str = now_datetime.strftime('%Y-%m-%d %H%M%S')

    strategy_name = para_combination['strategy_name']
    code = para_combination['code']
    zscore_length = int(para_combination['zscore_length'])
    zscore_threshold = float(para_combination['zscore_threshold'])

    initial_capital = int(para_combination['initial_capital'])
    mdd_in_sample = int(para_combination['mdd_in_sample'])
    stra_start_date = para_combination['stra_start_date']
    stra_start_date = datetime.datetime.strptime(stra_start_date, '%Y-%m-%d')

    exchange = para_combination['exchange']
    unique_id = para_combination['unique_id']

    end_date = datetime.datetime.now()
    start_date = datetime.datetime.now() - datetime.timedelta(days=12)
    end_date = end_date.strftime('%Y-%m-%d')
    start_date = start_date.strftime('%Y-%m-%d')

    quote = code + "/USDT"

    #################### historical data #####################

    df = get_interest_rates(start_date, end_date, code, True)
    df['DateTime'] = df['DateTime'].dt.strftime('%Y-%m-%d %H:%M:%S')
    now = datetime.datetime.now()
    rounded_now = now.replace(minute=0, second=0, microsecond=0)  # Calculate the starting point: 12 days before 'now'
    start_time = rounded_now - datetime.timedelta(days=12)
    date_range = pd.date_range(start=start_time, end=rounded_now, freq='H')
    df_interest = pd.DataFrame(date_range, columns=['DateTime'])
    df_interest['DateTime'] = df_interest['DateTime'].dt.strftime('%Y-%m-%d %H:%M:%S')

    interest_df = (df_interest.merge(df, how="left", on="DateTime"))
    interest_df['dailyInterestRate'] = interest_df['dailyInterestRate'].fillna(method='ffill')
    interest_df['interest_ma'] = interest_df['dailyInterestRate'].rolling(zscore_length).mean()
    interest_df['interest_std'] = interest_df['dailyInterestRate'].rolling(zscore_length).std()
    interest_df['interest_zscore'] = np.where(
        interest_df['interest_std'] != 0,
        (interest_df['dailyInterestRate'] - interest_df['interest_ma']) / interest_df['interest_std'], np.nan)

    ###################### trade_logic  ######################


    interest_df['trade_logic'] = (interest_df["interest_zscore"] > zscore_threshold)
    interest_df['close_logic'] = (interest_df["interest_zscore"] < zscore_threshold*-1)
    ######################TEMP CLOSE COND###############################
    # interest_df['close_logic'] = (interest_df["interest_zscore"] < zscore_threshold)

    df = interest_df[["DateTime", "interest_zscore", "trade_logic", "close_logic"]]
    ### testing ###

    trade_logic = df.at[df.index[-1], 'trade_logic']
    close_logic = df.at[df.index[-1], 'close_logic']
    last_price = float((requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={code}USDT").json()['price']))
    last_row_index = ""
    msg = f"{last_row_index}\n" + "\n".join([f"{col}: {df[col].iloc[-1]}" for col in df.columns[1:]])
    send_tg(msg)
    ##########################################################

    ######################## reading  #######################

    trade_record_path = os.path.join('su_record', unique_id + '_trade_record.csv')
    trade_status_path = os.path.join('su_record', unique_id + '_trade_status.csv')

    trade_record_df = pd.read_csv(trade_record_path)
    trade_status_df = pd.read_csv(trade_status_path)

    qty = trade_status_df.at[0, 'qty']
    cost_price = trade_status_df.at[0, 'cost_price']
    open_datetime = trade_status_df.at[0, 'open_datetime']

    temp_max_equity = trade_status_df.at[0, 'temp_max_equity']
    equity_value = trade_status_df.at[0, 'equity_value']
    last_realized_capital = trade_status_df.at[0, 'last_realized_capital']
    unrealized_pnl = trade_status_df.at[0, 'unrealized_pnl']
    mdd_out_sample = trade_status_df.at[0, 'mdd_out_sample']

    num_of_trade = trade_status_df.at[0, 'num_of_trade']

    open_datetime = datetime.datetime.strptime(open_datetime, '%Y-%m-%d %H:%M:%S')
    ### open_date for counting holding days ###
    open_date = open_datetime.date()

    ##########################################################

    ################ accinfo and position_list ################

    realized_pnl = 0
    unrealized_pnl = qty * (last_price - cost_price)
    unrealized_pnl = round(unrealized_pnl, 6)
    equity_value = last_realized_capital + unrealized_pnl

    if equity_value > temp_max_equity: temp_max_equity = equity_value
    temp_new_mdd_out_sample = round(100 * (1 - (equity_value / temp_max_equity)), 2)
    mdd_out_sample = max(temp_new_mdd_out_sample, mdd_out_sample)

    ######################### action  ########################

    qty_cond = qty == 0
    mdd_cond = mdd_out_sample < mdd_in_sample

    action = ''
    trd_side = ''
    dealt_qty = 0

    # if datetime.datetime.now().replace(microsecond=0) < datetime.datetime(2024, 1, 12, 15, 42, 30).replace(microsecond=0):
    #     trade_logic = True
    #     qty_cond = True
    # if datetime.datetime.now().replace(second = 0, microsecond=0) == datetime.datetime(2024, 1, 12, 15, 43).replace(second = 0, microsecond=0):
    #     close_logic = True
    #     qty_cond = False

    ### open position ###
    if qty_cond and trade_logic and mdd_cond:
        ######### Align with backtest delay #########
        time.sleep(58.8*60)
        #############################################

        action = 'OPEN'
        trd_side = 'buy'
        bid_ask_data = ccxt.binance().fetch_order_book(quote)
        print(bid_ask_data)
        num_of_trade += 1
        trade_status_df, dealt_qty = place_order_and_record(action,
                                                            trd_side,
                                                            bid_ask_data,
                                                            equity_value,
                                                            exchange,
                                                            code,
                                                            unique_id,
                                                            trade_status_df
                                                            )

        df_record_path = os.path.join('df_record', now_date_str + '_' +
                                      action + '_' + trd_side + '_' + code + '_' +
                                      unique_id + '.csv')
        df.to_csv(df_record_path)

    ### close position ###
    elif not qty_cond and (close_logic):

        ######### Align with backtest delay #########
        time.sleep(58.8*60)
        #############################################

        action = 'CLOSE'
        trd_side = 'sell'
        bid_ask_data = ccxt.binance().fetch_order_book(quote)

        realized_pnl = unrealized_pnl
        unrealized_pnl = 0
        last_realized_capital += realized_pnl
        num_of_trade += 1

        trade_status_df, dealt_qty = place_order_and_record(action,
                                                            trd_side,
                                                            bid_ask_data,
                                                            equity_value,
                                                            exchange,
                                                            code,
                                                            unique_id,
                                                            trade_status_df
                                                            )

        df_record_path = os.path.join('df_record', now_date_str + '_' +
                                      action + '_' + trd_side + '_' + code + '_' +
                                      unique_id + '.csv')
        df.to_csv(df_record_path)

    ####### record everyday ######

    dealt_avg_price = trade_status_df.at[0, 'cost_price']

    trade_status_df.at[0, 'temp_max_equity'] = temp_max_equity
    trade_status_df.at[0, 'equity_value'] = equity_value
    trade_status_df.at[0, 'realized_pnl'] = realized_pnl
    trade_status_df.at[0, 'unrealized_pnl'] = unrealized_pnl
    trade_status_df.at[0, 'mdd_out_sample'] = mdd_out_sample
    trade_status_df.at[0, 'num_of_trade'] = num_of_trade

    trade_status_df.to_csv(trade_status_path, index=False)

    new_record = pd.DataFrame(
        {'datetime': [now_datetime.strftime('%Y-%m-%d %H:%M')],
         'strategy_name': [strategy_name],
         'code': [code],
         'action': [action],
         'trd_side': [trd_side],
         'trd_qty': [dealt_qty],
         'trd_price': [dealt_avg_price]})

    trade_record_df = pd.concat([trade_record_df, new_record])
    trade_record_df.to_csv(trade_record_path, index=False)

if __name__ == '__main__':

    ##################### initiate #####################
    su_table = pd.read_csv('su_table.csv')
    su_table['unique_id'] = su_table['unique_id'].astype(str)
    su_table['code'] = su_table['code'].astype(str)

    for i in range(len(su_table)):
        unique_id = str_to_int(su_table.at[i, 'para'])
        strategy_name = su_table.at[i, 'strategy_name']
        code = su_table.at[i, 'code']

        ### generate unique_id for new strategy
        if unique_id != su_table.at[i, 'unique_id']:
            su_table.at[i, 'unique_id'] = unique_id
            su_table.to_csv('su_table.csv', index=False)
            print('new unique_id saved: ', unique_id)

        ### generate file_path for each unique_id
        trade_record_path = os.path.join('su_record', unique_id + '_trade_record.csv')
        trade_status_path = os.path.join('su_record', unique_id + '_trade_status.csv')

        if not os.path.isfile(trade_record_path):
            trade_record_dict = {'datetime': [], 'strategy_name': [], 'code': [], 'action': [], 'trd_side': [],
                                 'trd_qty': [], 'trd_price': []}
            trade_record_df = pd.DataFrame(trade_record_dict)
            trade_record_df.to_csv(trade_record_path, index=False)

        if not os.path.isfile(trade_status_path):
            trade_status_dict = {'code': [code],
                                 'strategy_name': [strategy_name],
                                 'qty': [0],
                                 'cost_price': [0],
                                 'open_datetime': ['1999-12-31 00:00:00'],

                                 'temp_max_equity': [100],
                                 'equity_value': [100],
                                 'last_realized_capital': [100],
                                 'unrealized_pnl': [0],
                                 'mdd_out_sample': [0],

                                 'num_of_trade': [0]}

            trade_status_df = pd.DataFrame(trade_status_dict)
            trade_status_df.to_csv(trade_status_path, index=False)

        code_list = su_table['code'].unique()

        print('===============su_table is ready===============')
        print(su_table)
        print('===============================================')

        ########################################################
        ########################################################

        check_func_dict = {
            'interest_zscore': interest_zscore
        }

        ########################################################
        ########################################################

        api_key = os.getenv("binance_api_key")
        api_secret = os.getenv("binance_pw")

        # Setup
        exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
        })

        for code in code_list:
            print(code)
            para_rows = su_table[su_table['code'] == code]
            para_rows = para_rows.reset_index(drop=True)
            print(para_rows)

            kwargs = {
                "exchange": exchange,
                'code': code,
                'para_rows': para_rows,
                'check_func_dict': check_func_dict,
            }

            my_thread = threading.Thread(target=single_contract_run, kwargs=kwargs)
            my_thread.start()
            print("threading of ", code, "started")
