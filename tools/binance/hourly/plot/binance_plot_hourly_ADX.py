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
import matplotlib.pyplot as plt
import argparse
from trader.KlinesDB import KlinesDB
from trader.indicator.OBV import OBV
from trader.indicator.ADX import ADX
import numpy as np
import talib

def simulate(kdb, symbol, start_ts, end_ts):
    msgs = kdb.get_dict_klines(symbol, start_ts, end_ts, daily=True)

    obv = OBV()
    obv_values = []
    adx = ADX(win=14.0)
    adx_x_values = []
    adx_values = []
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

        obv_value = obv.update(close=close, volume=volume)
        obv_values.append(obv_value)

        adx.update(close, low=low, high=high)
        if adx.result:
            adx_values.append(adx.result)
            adx_x_values.append(i)

        close_prices.append(close)
        open_prices.append(open)
        low_prices.append(low)
        high_prices.append(high)
        i += 1

    talib_adx_values = talib.ADX(np.array(high_prices), np.array(low_prices), np.array(close_prices), 14.0)

    plt.subplot(311)
    symprice, = plt.plot(close_prices, label=symbol)
    plt.legend(handles=[symprice])
    plt.subplot(312)
    fig21, = plt.plot(adx_x_values, adx_values, label='ADX')
    plt.legend(handles=[fig21])
    plt.subplot(313)
    fig31, = plt.plot(talib_adx_values, label='TALIB_ADX')
    plt.legend(handles=[fig31])
    plt.show()

# get first timestamp from kline sqlite db
def get_first_timestamp(filename, symbol):
    conn = sqlite3.connect(filename)
    c = conn.cursor()
    c.execute("SELECT E FROM miniticker WHERE s='{}' ORDER BY E ASC LIMIT 1".format(symbol))
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
                        default='binance_hourly_klines_BTC.db',
                        help='filename of hourly kline sqlite db')

    parser.add_argument('-s', action='store', dest='symbol',
                        default='',
                        help='trade symbol')

    parser.add_argument('-l', action='store_true', dest='list_table_names',
                        default=False,
                        help='List table names in db')

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
            end_ts = get_first_timestamp(results.filename, symbol)
            start_ts = end_ts - 1000 * 3600 * int(results.hours)
            print(start_ts, end_ts)


    if not os.path.exists(results.hourly_filename):
        print("file {} doesn't exist, exiting...".format(results.filename))
        sys.exit(-1)

    kdb = KlinesDB(None, hourly_filename, None)
    print("Loading {}".format(hourly_filename))

    if results.list_table_names:
        for symbol in kdb.get_table_list():
            print(symbol)

    if symbol:
        simulate(kdb, symbol, start_ts, end_ts)
    else:
        parser.print_help()
    kdb.close()