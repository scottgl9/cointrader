#!/usr/bin/env python3
import sys
try:
    import trader
except ImportError:
    sys.path.append('.')
    import trader

import sqlite3
import sys
import os
from datetime import datetime
import time
from trader.account.binance.client import Client
from trader.config import *
import matplotlib.pyplot as plt
import argparse
from trader.HourlyKlinesDB import HourlyKlinesDB
from trader.indicator.OBV import OBV
from trader.indicator.RSI import RSI
from trader.indicator.EMA import EMA

def simulate(hkdb, symbol, start_ts, end_ts):
    msgs = hkdb.get_dict_klines(symbol, start_ts, end_ts)

    rsi_daily = RSI(24)
    rsi_weekly = RSI(24 * 7)
    rsi_monthly = RSI(24 * 30)
    rsi_daily_values = []
    rsi_weekly_values = []
    rsi_monthly_values = []
    ema = EMA(12, scale=24)
    ema_values = []
    close_prices = []
    open_prices = []
    low_prices = []
    high_prices = []
    volumes = []

    i=0
    for msg in msgs: #get_rows_as_msgs(c):
        ts = int(msg['ts'])
        close = float(msg['close'])
        low = float(msg['low'])
        high = float(msg['high'])
        open = float(msg['open'])
        volume = float(msg['quote_volume'])
        volumes.append(volume)

        ema.update(close)
        rsi_daily.update(close)
        rsi_daily_values.append(rsi_daily.result)
        rsi_weekly.update(close)
        rsi_weekly_values.append(rsi_weekly.result)
        rsi_monthly.update(close)
        rsi_monthly_values.append(rsi_monthly.result)

        close_prices.append(close)
        open_prices.append(open)
        low_prices.append(low)
        high_prices.append(high)
        i += 1

    plt.subplot(211)
    symprice, = plt.plot(close_prices, label=symbol)
    plt.legend(handles=[symprice])
    plt.subplot(212)
    fig21, = plt.plot(rsi_daily_values, label='RSI_DAILY')
    fig22, = plt.plot(rsi_weekly_values, label='RSI_WEEKLY')
    fig23, = plt.plot(rsi_monthly_values, label='RSI_MONTHLY')
    plt.legend(handles=[fig21, fig22, fig23])
    plt.show()

# get first timestamp from kline sqlite db
def get_first_timestamp(filename, symbol):
    conn = sqlite3.connect(filename)
    c = conn.cursor()
    c.execute("SELECT E FROM miniticker WHERE s='{}' ORDER BY E ASC LIMIT 1".format(symbol))
    result = c.fetchone()
    return int(result[0])

def get_last_timestamp(filename, symbol):
    conn = sqlite3.connect(filename)
    c = conn.cursor()
    #c.execute("SELECT ts FROM {} ORDER BY ts DESC LIMIT 1".format(symbol))
    c.execute("SELECT E FROM miniticker WHERE s='{}' ORDER BY E DESC LIMIT 1".format(symbol))
    result = c.fetchone()
    return int(result[0])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # used to get first timestamp for symbol from precaptured live market data
    parser.add_argument('-f', action='store', dest='filename',
                        default='',
                        help='filename of kline sqlite db')

    parser.add_argument('--hours', action='store', dest='hours',
                        default=48,
                        help='Hours before first ts in db specified by -f')

    parser.add_argument('-k', action='store', dest='hourly_filename',
                        default='binance_hourly_klines.db',
                        help='filename of hourly kline sqlite db')

    parser.add_argument('-s', action='store', dest='symbol',
                        default='',
                        help='trade symbol')

    parser.add_argument('-l', action='store_true', dest='list_table_names',
                        default=False,
                        help='List table names in db')

    parser.add_argument('--start-date', action='store', dest='start_date',
                        default='',
                        help='specify start date in month/day/year format')

    parser.add_argument('--end-date', action='store', dest='end_date',
                        default='',
                        help='specify end date in month/day/year format')

    results = parser.parse_args()


    hourly_filename = results.hourly_filename
    symbol = results.symbol
    start_ts = 0
    end_ts = 0

    if results.filename:
        if not os.path.exists(results.filename):
            print("file {} doesn't exist, exiting...".format(results.filename))
            sys.exit(-1)
        else:
            end_ts = get_last_timestamp(results.filename, symbol)
            start_ts = get_first_timestamp(results.filename, symbol)
            start_ts = start_ts - 1000 * 3600 * int(results.hours)
            print(start_ts, end_ts)
    elif results.start_date and results.end_date:
        start_dt = datetime.strptime(results.start_date, '%m/%d/%Y')
        end_dt = datetime.strptime(results.end_date, '%m/%d/%Y')
        start_ts = int(time.mktime(start_dt.timetuple()) * 1000.0)
        end_ts = int(time.mktime(end_dt.timetuple()) * 1000.0)

    if not os.path.exists(results.hourly_filename):
        print("file {} doesn't exist, exiting...".format(results.filename))
        sys.exit(-1)

    hkdb = HourlyKlinesDB(None, hourly_filename, None)
    print("Loading {}".format(hourly_filename))

    if results.list_table_names:
        for symbol in hkdb.get_table_list():
            print(symbol)

    if symbol:
        simulate(hkdb, symbol, start_ts, end_ts)
    else:
        parser.print_help()
    hkdb.close()