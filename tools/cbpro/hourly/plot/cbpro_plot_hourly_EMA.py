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
import matplotlib.pyplot as plt
import argparse
from trader.KlinesDB import KlinesDB
from trader.account.cbpro.AccountCoinbasePro import AccountCoinbasePro
from trader.indicator.OBV import OBV
try:
    from trader.indicator.native.EMA import EMA
except ImportError:
    from trader.indicator.EMA import EMA

def simulate(kdb, symbol, start_ts, end_ts):
    msgs = kdb.get_dict_klines(symbol, start_ts, end_ts)

    obv = OBV()
    scale = 24
    if start_ts and end_ts:
        scale = 1
    ema12 = EMA(12, scale=scale)
    ema26 = EMA(26, scale=scale)
    ema50 = EMA(50, scale=scale)
    ema100 = EMA(100, scale=scale)
    ema200 = EMA(200, scale=scale)
    ema300 = EMA(300, scale=scale)
    ema500 = EMA(500, scale=scale)
    obv_ema12 = EMA(12)
    obv_ema26 = EMA(26)
    obv_ema50 = EMA(50)
    obv_ema12_values = []
    obv_ema26_values = []
    obv_ema50_values = []
    ema12_values = []
    ema26_values = []
    ema50_values = []
    ema100_values = []
    ema200_values = []
    ema300_values = []
    ema500_values = []
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
        volume = float(msg['volume'])
        volumes.append(volume)

        obv_value = obv.update(close=close, volume=volume)
        obv_ema12_values.append(obv_ema12.update(obv_value))
        obv_ema26_values.append(obv_ema26.update(obv_value))
        obv_ema50_values.append(obv_ema50.update(obv_value))

        ema12_value = ema12.update(close)
        ema12_values.append(ema12_value)
        ema26_values.append(ema26.update(close))
        ema50_value = ema50.update(close)
        ema50_values.append(ema50_value)
        ema100.update(close)
        ema100_values.append(ema100.result)
        ema200.update(close)
        ema200_values.append(ema200.result)
        ema300.update(close)
        ema300_values.append(ema300.result)
        ema500.update(close)
        ema500_values.append(ema500.result)

        close_prices.append(close)
        open_prices.append(open)
        low_prices.append(low)
        high_prices.append(high)
        i += 1

    plt.subplot(211)
    symprice, = plt.plot(close_prices, label=symbol)

    fig1, = plt.plot(ema12_values, label='EMA12')
    fig2, = plt.plot(ema26_values, label='EMA26')
    fig3, = plt.plot(ema50_values, label='EMA50')
    fig4, = plt.plot(ema200_values, label='EMA200')
    plt.legend(handles=[symprice, fig1, fig2, fig3, fig4])
    plt.subplot(212)
    fig21, = plt.plot(obv_ema12_values, label='OBV12')
    fig22, = plt.plot(obv_ema26_values, label='OBV26')
    fig23, = plt.plot(obv_ema50_values, label='OBV50')
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
                        default='cbpro_hourly_klines.db',
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
        start_ts = int(time.mktime(start_dt.timetuple()))
        end_ts = int(time.mktime(end_dt.timetuple()))

    if not os.path.exists(results.hourly_filename):
        print("file {} doesn't exist, exiting...".format(results.filename))
        sys.exit(-1)

    accnt = AccountCoinbasePro(client=None, simulate=True)
    kdb = KlinesDB(accnt, hourly_filename, None)
    print("Loading {}".format(hourly_filename))

    if results.list_table_names:
        for symbol in kdb.get_table_list():
            print(symbol)

    if symbol:
        simulate(kdb, symbol, start_ts, end_ts)
    else:
        parser.print_help()
    kdb.close()
