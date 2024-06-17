import time
import datetime

import os
import sys
import multiprocessing as mp
import requests
from datetime import datetime, timedelta

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import plotguy
import itertools

import pandas_ta as ta
import random

pd.set_option('display.max_rows',None)
pd.set_option('display.max_columns',None)
pd.set_option('display.width',None)
pd.set_option('display.float_format', lambda x: '%.6f' % x)

data_folder = 'data'
secondary_data_folder = 'secondary_data'
backtest_output_folder = 'backtest_output'
signal_output_folder = 'signal_output'

if not os.path.isdir(data_folder): os.mkdir(data_folder)
if not os.path.isdir(secondary_data_folder): os.mkdir(secondary_data_folder)
if not os.path.isdir(backtest_output_folder): os.mkdir(backtest_output_folder)
if not os.path.isdir(signal_output_folder): os.mkdir(signal_output_folder)

py_filename = os.path.basename(__file__).replace('.py','')

def get_binance_data(coin_name, start_date, end_date):
    # Define the API endpoint for Kline/Candlestick data
    url = "https://api.binance.com/api/v3/klines"

    # Define the symbol for the coin and the interval (e.g., 1 day)
    symbol = coin_name.upper() + "USDT"
    interval = "1h"

    # Convert the start_date and end_date to timestamps in milliseconds
    start_time = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp()) * 1000
    end_time = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp()) * 1000

    # Set the parameters for the request
    params = {
        "symbol": symbol,
        "interval": interval,
        "endTime": end_time,
        "limit": 1000  # Maximum limit per request
    }

    # Initialize an empty list to store the data
    all_data = []

    # Fetch the data in chunks
    while start_time < end_time:
        # Set the start time for the request
        params["startTime"] = start_time

        # Send the GET request to the API
        response = requests.get(url, params=params)
        data = response.json()

        # Check if the data is empty
        if not data:
            break

        # Append the data to the list
        all_data.extend(data)

        # Move the start time to the next chunk
        start_time = int(data[-1][0]) + 1

    # Convert the data into a DataFrame
    df = pd.DataFrame(all_data, columns=["timestamp", "open", "high", "low", "close", "volume", "close_time",
                                         "quote_asset_volume", "number_of_trades", "taker_buy_base_asset_volume",
                                         "taker_buy_quote_asset_volume", "ignore"])
    df = df.apply(pd.to_numeric, errors='coerce')

    # Convert the timestamp to a readable format
    df.insert(1, "date", pd.to_datetime(df["timestamp"], unit="ms"))
    print(df)
    # sys.exit()

    return df
def get_interest_rates(start_date, end_date, coin, intra_day):
    all_data = []

    # Convert start_date and end_date strings to datetime objects
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    current_date = start_date
    while current_date <= end_date:
        url = "https://www.binance.com/bapi/margin/v1/public/margin/vip/spec/history-interest-rate"
        params = {
            "asset": f"{coin}",
            "vipLevel": 0,
            "startTime": int(current_date.timestamp() * 1000),
            "endTime": int((current_date + timedelta(days=30)).timestamp() * 1000)
        }

        response = requests.get(url, params=params)
        data = response.json()

        # Append the data to the list
        all_data.extend(data["data"])

        # Move to the next month
        current_date += timedelta(days=30)

    df = pd.DataFrame(all_data)
    # Size reduce
    df = df.drop("vipLevel", axis=1)
    # Adding datetime column
    df = df.sort_values(by="timestamp", ascending=True)
    # Convert "dailyInterestRate" column to numeric dtype
    df["timestamp"] = pd.to_numeric(df["timestamp"])
    df["dailyInterestRate"] = pd.to_numeric(df["dailyInterestRate"])

    df.insert(2, "date", pd.to_datetime(df["timestamp"], unit="ms"))
    df.drop_duplicates(subset='timestamp', keep='first', inplace=True)

    if intra_day:
        return df
    else:
        # Convert "timestamp" column to datetime type
        df["date"] = pd.to_datetime(df["timestamp"], unit="ms")
        # Drop duplicated interest rate within a day
        df = df.loc[df.groupby(df["date"].dt.date)["dailyInterestRate"].idxmax()]
        return df
def backtest(para_combination):

    para_dict       = para_combination['para_dict']
    sec_profile     = para_combination['sec_profile']
    start_date      = para_combination['start_date']
    end_date        = para_combination['end_date']
    reference_index = para_combination['reference_index']
    freq            = para_combination['freq']
    file_format     = para_combination['file_format']
    df              = para_combination['df']
    intraday        = para_combination['intraday']
    output_folder   = para_combination['output_folder']
    data_folder     = para_combination['data_folder']
    run_mode        = para_combination['run_mode']
    summary_mode    = para_combination['summary_mode']
    py_filename     = para_combination['py_filename']

    ##### stra specific #####
    code                = para_combination['code']
    zscore_length           = para_combination['zscore_length']
    zscore_threshold        = para_combination["zscore_threshold"]

    ##### sec_profile #####

    market          = sec_profile['market']
    sectype         = sec_profile['sectype']
    initial_capital = sec_profile['initial_capital']
    lot_size_dict   = sec_profile['lot_size_dict']
    lot_size        = lot_size_dict[code]


    commission_rate = sec_profile['commission_rate']

    ##### stra specific #####
    df['interest_ma'] = df['dailyInterestRate'].rolling(zscore_length).mean()
    df['interest_std'] = df['dailyInterestRate'].rolling(zscore_length).std()
    df['interest_zscore'] = np.where(
        df['interest_std'] != 0, (df['dailyInterestRate'] - df['interest_ma']) / df['interest_std'], np.nan)
    df['trade_logic'] = (df["interest_zscore"] > zscore_threshold)
    ##### initialization #####

    df['action'] = ''
    df['num_of_share'] = 0

    df['open_price'] = np.NaN
    df['close_price'] = np.NaN

    df['realized_pnl'] = np.NaN
    df['unrealized_pnl'] = 0
    df['net_profit'] = 0

    df['equity_value'] = initial_capital
    df['mdd_dollar'] = 0
    df['mdd_pct'] = 0

    df['commission'] = 0
    df['logic'] = None


    open_date    = datetime.now().date()
    open_price   = 0
    num_of_share = 0
    net_profit   = 0
    num_of_trade = 0

    last_realized_capital = initial_capital

    equity_value = 0
    realized_pnl   = 0
    unrealized_pnl = 0

    commission = 0

    for i, row in df.iterrows():
        now_date  = i.date()
        now_open  = row['open']
        now_high  = row['high']
        now_low   = row['low']
        now_close = row['close']

        ##### stra specific #####
        trade_logic = row['trade_logic']
        now_zscore     = row["interest_zscore"]

        ##### commission ####
        if num_of_share > 0:
            commission = now_close * num_of_share * 0.001
            commission = 2 * commission
        else:
            commission = 0

        ##### equity value #####
        unrealized_pnl = num_of_share * (now_close - open_price) - commission
        equity_value = last_realized_capital + unrealized_pnl
        equity_value = last_realized_capital + unrealized_pnl
        net_profit = round(equity_value - initial_capital, 2)

        if trade_logic: df.at[i, 'logic'] = 'trade_logic'

        if run_mode == 'backtest':

            close_logic = (num_of_share != 0) and (now_zscore < -1*0.4)
            last_index_cond = i == df.index[-1]
            min_cost_cond = True

            ##### open position #####
            if num_of_share == 0 and not last_index_cond and min_cost_cond and trade_logic:

                num_of_lot = last_realized_capital / (lot_size * now_close)
                num_of_share = num_of_lot * lot_size

                open_price = now_close
                open_date = now_date

                df.at[i, 'action'] = 'open'
                df.at[i, 'open_price'] = open_price

            ##### close position #####
            elif num_of_share > 0 and (last_index_cond or close_logic):

                realized_pnl = unrealized_pnl
                unrealized_pnl = 0
                last_realized_capital += realized_pnl

                num_of_trade += 1

                num_of_share = 0

                if close_logic: df.at[i, 'logic'] = 'close_logic'
                if last_index_cond: df.at[i, 'action'] = 'last_index'
                if close_logic: df.at[i, 'action'] = 'close_logic'

                df.at[i, 'close_price'] = now_close
                df.at[i, 'realized_pnl'] = realized_pnl
                df.at[i, 'commission'] = commission

        ### record at last ###
        df.at[i, 'equity_value'] = equity_value
        df.at[i, 'num_of_share'] = num_of_share
        df.at[i, 'unrealized_pnl'] = unrealized_pnl
        df.at[i, 'net_profit'] = net_profit

    if summary_mode and run_mode == 'backtest':
        df = df[df['action'] != '']

    df["return_pct_change"] = df["equity_value"].pct_change()

    save_path = plotguy.generate_filepath(para_combination)
    print(save_path)
    if file_format == 'csv':
        df.to_csv(save_path)
    elif file_format == 'parquet':
        df.to_parquet(save_path)


def get_hist_data(code_list, start_date, end_date, freq,
                  data_folder, file_format, update_data,
                  market):

    start_date_int = int(start_date.replace('-',''))
    end_date_int   = int(end_date.replace('-',''))

    df_dict ={}
    for code in code_list:

        file_path = os.path.join(data_folder, code + '_' + freq + '.' + file_format)

        if os.path.isfile(file_path) and not update_data:
            if file_format == 'csv':
                df = pd.read_csv(file_path)
                df['datetime'] = pd.to_datetime(df['datetime'], format='%Y-%m-%d')
                df['date'] = df["date"].dt.floor('D')
                df = df.set_index('datetime')

            elif file_format == 'parquet':
                df = pd.read_parquet(file_path)
                df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')

            print(datetime.now(), 'successfully read data', code)
        else:
            df = get_binance_data(code, start_date, end_date)
            df = df[['timestamp','date', 'open', 'high', 'low', 'close', 'volume']]
            df2 = df
            df2["datetime"] = pd.to_datetime(df['timestamp'], unit="ms")
            df2['date'] = df2["datetime"].dt.floor('D')
            df2 = df2.drop("timestamp", axis = 1)
            df2 = df2.set_index('datetime')

            time.sleep(5)

            if file_format == 'csv':
                df2.to_csv(file_path)
            elif file_format == 'parquet':
                df2.to_parquet(file_path, index = False)
            print(datetime.now(), 'successfully get data from data source', code)

        df['pct_change'] = df['close'].pct_change()

        df_dict[code] = df

    return df_dict

def get_secondary_data(df_dict, start_date, end_date):

    interest_df = get_interest_rates(start_date, end_date, "BTC", True)
    interest_df.to_csv("secondary_data/ETH_interest_rate.csv", index= False)
    # interest_df = pd.read_csv("secondary_data/usdt_interest_rate.csv")
    interest_df = interest_df[["timestamp", "dailyInterestRate"]]
    for code, df in df_dict.items():


        df = pd.merge(df, interest_df, on = "timestamp", how = "left")
        df = df.set_index("datetime", drop=True)
        # df = df.rename_axis('datetime')
        # df["dailyInterestRate_pct_change"] = df["dailyInterestRate"].pct_change()
        print(df)
        df = df.drop("timestamp", axis = 1)
        df['date'] = df["date"].dt.floor('D')
        df["dailyInterestRate"] = df["dailyInterestRate"]*365
        df['dailyInterestRate'] = df['dailyInterestRate'].fillna(method='ffill')
        df.to_csv("master.csv")

        df_dict[code] = df

    return df_dict, para_dict

def get_sec_profile(code_list, market, sectype, initial_capital):

    sec_profile = {}
    lot_size_dict = {}


    for code in code_list:
        lot_size_dict[code] = 0.00001

    sec_profile['market'] = market
    sec_profile['sectype'] = sectype
    sec_profile['initial_capital'] = initial_capital
    sec_profile['lot_size_dict'] = lot_size_dict
    sec_profile['commission_rate'] = 0.001

    return sec_profile


def get_all_para_combination(para_dict, df_dict, sec_profile, start_date, end_date,
                             data_folder, signal_output_folder, backtest_output_folder,
                             run_mode, summary_mode, freq, py_filename):

    para_values = list(para_dict.values())
    para_keys = list(para_dict.keys())
    para_list = list(itertools.product(*para_values))

    print('number of combination:', len(para_list))

    intraday = True if freq != '1D' else False
    output_folder = backtest_output_folder if run_mode == 'backtest' else signal_output_folder

    all_para_combination = []

    for reference_index in range(len(para_list)):
        para = para_list[reference_index]
        code = para[0]
        df = df_dict[code]
        para_combination = {}
        for i in range(len(para)):
            key = para_keys[i]
            para_combination[key] = para[i]

        para_combination['para_dict'] = para_dict
        para_combination['sec_profile'] = sec_profile
        para_combination['start_date'] = start_date
        para_combination['end_date'] = end_date
        para_combination['reference_index'] = reference_index
        para_combination['freq'] = freq
        para_combination['file_format'] = file_format
        para_combination['df'] = df
        para_combination['intraday'] = intraday
        para_combination['output_folder'] = output_folder
        para_combination['data_folder'] = data_folder
        para_combination['run_mode'] = run_mode
        para_combination['summary_mode'] = summary_mode
        para_combination['py_filename'] = py_filename

        all_para_combination.append(para_combination)

    return all_para_combination


if __name__ == '__main__':

    start_date  = '2022-09-01'
    end_date    = '2024-04-30'

    freq        = '1H'
    market      = 'CRYPTO'
    sectype     = 'STK'
    file_format = 'csv'

    initial_capital = 200000

    update_data = True
    run_mode = 'backtest'
    summary_mode = False
    read_only = False
    number_of_core = 60
    mp_mode = True

    code_list = ["BTC"]

    difference_min = 0
    difference_max = 0.001
    number_threshold = 30
    step_size = 0.1

    para_dict = {
        'code'                  : code_list,
        # "zscore_length": [x for x in range(120, 141)],
        # "zscore_length": [2 ** i for i in range(11)],
        "zscore_length": [128],
        # "zscore_threshold": [round(difference_min + i * step_size,1) for i in range(number_threshold)],
        "zscore_threshold": [1.8],
        # "zscore_threshold": [difference_min + difference_step * i for i in
        #                          range(int((difference_max - difference_min) / difference_step) + 1)],
    }


    ########################################################################
    ########################################################################

    df_dict = get_hist_data(code_list, start_date, end_date, freq,
                            data_folder, file_format, update_data,
                            market)

    df_dict, para_dict = get_secondary_data(df_dict, start_date, end_date)

    sec_profile = get_sec_profile(code_list, market, sectype, initial_capital)

    all_para_combination = get_all_para_combination(para_dict, df_dict, sec_profile, start_date, end_date,
                             data_folder, signal_output_folder, backtest_output_folder,
                             run_mode, summary_mode, freq, py_filename)

    if not read_only:
        if mp_mode:
            pool = mp.Pool(processes=number_of_core)
            pool.map(backtest, all_para_combination)
            pool.close()
        else:
            for para_combination in all_para_combination:
               backtest(para_combination)

    plotguy.generate_backtest_result(
        all_para_combination=all_para_combination,
        number_of_core=number_of_core
    )

    # sys.exit()

    app = plotguy.plot(
        mode='equity_curves',
        all_para_combination=all_para_combination
    )

    app.run_server(port=random.randint(8900, 9900))
