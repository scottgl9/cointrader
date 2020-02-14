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
from trader.indicator.OBV import OBV
from trader.indicator.MACD import MACD
from trader.lib.Crossover2 import Crossover2
from trader.lib.FourierFilter import FourierFilter

def simulate(kdb, symbol, start_ts, end_ts):
    msgs = kdb.get_dict_klines(symbol, start_ts, end_ts)

    cross = Crossover2()
    obv = OBV()
    scale = 12
    #scale = 24
    #if start_ts and end_ts:
    #    scale = 1
    macd = MACD(short_weight=12, long_weight=26, signal_weight=9, scale=scale)
    macd_values = []
    macd_signal_values = []
    close_prices = []
    open_prices = []
    low_prices = []
    high_prices = []
    volumes = []
    crossups = []
    crossdowns = []

    ff = FourierFilter()

    i=0
    for msg in msgs: #get_rows_as_msgs(c):
        ts = int(msg['ts'])
        close = float(msg['close'])
        volume = float(msg['quote_volume'])
        volumes.append(volume)

        #macd.update(close)
        #macd_values.append(macd.result)
        #macd_signal_values.append(macd.signal.result)

        close_prices.append(close)
        i += 1

    ff.load(close_prices)
    ff.process()
    ff_close_prices = ff.get_result()
    i=0
    last_cross = 0
    for close in ff_close_prices:
        macd.update(close)
        macd_values.append(macd.result)
        macd_signal_values.append(macd.signal.result)
        cross.update(macd.result, macd.signal.result)

        if cross.crossup_detected() and last_cross != 1:
            crossups.append(i)
            last_cross = 1
        elif cross.crossdown_detected() and last_cross != -1:
            crossdowns.append(i)
            last_cross = -1
        i+=1

    plt.subplot(211)
    for i in crossups:
        plt.axvline(x=i, color='green')
    for i in crossdowns:
        plt.axvline(x=i, color='red')
    symprice, = plt.plot(close_prices, label=symbol)
    fig1, = plt.plot(ff_close_prices, label="FF")
    plt.legend(handles=[symprice, fig1])
    plt.subplot(212)
    fig21, = plt.plot(macd_values, label='MACD')
    fig22, = plt.plot(macd_signal_values, label='MACD_SIGNAL')
    plt.legend(handles=[fig21, fig22])
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
    elif results.start_date and results.end_date:
        start_dt = datetime.strptime(results.start_date, '%m/%d/%Y')
        end_dt = datetime.strptime(results.end_date, '%m/%d/%Y')
        start_ts = int(time.mktime(start_dt.timetuple()) * 1000.0)
        end_ts = int(time.mktime(end_dt.timetuple()) * 1000.0)

    if symbol:
        simulate(kdb, symbol, start_ts, end_ts)
    else:
        parser.print_help()
    kdb.close()
