#!/usr/bin/env python3# test HourlyLSTM class

import sys
try:
    import trader
except ImportError:
    sys.path.append('.')
    import trader

import sqlite3
import sys
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import time
from trader.account.binance.client import Client
from trader.config import *
import matplotlib.pyplot as plt
import argparse
from trader.lib.MachineLearning.HourlyLSTM import HourlyLSTM
from trader.HourlyKlinesDB import HourlyKlinesDB
from trader.account.AccountBinance import AccountBinance

try:
    from trader.indicator.native.EMA import EMA
except ImportError:
    from trader.indicator.EMA import EMA


def simulate(hkdb, symbol, start_ts, end_ts):
    hourly_lstm = HourlyLSTM(hkdb, symbol)

    hourly_lstm.load(model_start_ts=0, model_end_ts=start_ts)

    testy = []
    predicty = []

    count = 0

    ts = start_ts
    while ts <= end_ts:
        ts += 3600 * 1000
        hourly_lstm.update(ts)
        testy.append(hourly_lstm.actual_result)
        predicty.append(hourly_lstm.predict_result)
        count += 1

    plt.subplot(211)
    fig1, = plt.plot(testy, label='TESTY')
    fig2, = plt.plot(predicty, label='PREDICTY')
    plt.legend(handles=[fig1, fig2])
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

    parser.add_argument('-k', action='store', dest='hourly_filename',
                        default='binance_hourly_klines.db',
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

    accnt = AccountBinance(None, simulation=True)

    if not os.path.exists(results.hourly_filename):
        print("file {} doesn't exist, exiting...".format(results.filename))
        sys.exit(-1)


    hkdb = HourlyKlinesDB(accnt, hourly_filename, None)
    print("Loading {}".format(hourly_filename))

    if results.list_table_names:
        for symbol in hkdb.get_table_list():
            print(symbol)

    if symbol:
        timestamps = hkdb.get_kline_values_by_column(symbol, 'ts')
        train_index = int(len(timestamps) * 0.80)
        start_ts = int(timestamps[train_index])
        end_ts = int(timestamps[-1])
        simulate(hkdb, symbol, start_ts, end_ts)
    else:
        parser.print_help()
    hkdb.close()
