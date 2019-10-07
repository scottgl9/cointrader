#!/usr/bin/env python3
# new version of HourlyLSTM

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
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse
from trader.KlinesDB import KlinesDB
from trader.account.AccountBinance import AccountBinance
from trader.lib.MachineLearning.HourlyLSTMSignals import HourlyLSTMSignals


def simulate(hkdb, symbol, start_ts, end_ts):
    hourly_lstm = HourlyLSTMSignals(hkdb, symbol)

    hourly_lstm.load(model_start_ts=0, model_end_ts=start_ts)

    testy = []
    predicty = []

    count = 0

    ts = start_ts
    while ts <= end_ts:
        ts += 3600 * 1000
        hourly_lstm.update(ts)
        #print(hourly_lstm.actual_result)
        #print(hourly_lstm.predict_result)
        testy.append(hourly_lstm.actual_result)
        predicty.append(hourly_lstm.predict_result)
        count += 1

    plt.subplot(211)
    fig1, = plt.plot(testy, label='TESTY')
    fig2, = plt.plot(predicty, label='PREDICTY')
    #fig1, = plt.plot(hourly_lstm.df['close'].values.tolist(), label='close')
    #fig2, = plt.plot(hourly_lstm.df['EMA_CLOSE'].values.tolist(), label='EMA')
    plt.legend(handles=[fig1, fig2])
    plt.subplot(212)
    #fig21, = plt.plot(hourly_lstm.df['quote_volume'].values.tolist(), label='volume')
    #plt.legend(handles=[fig21])
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

    accnt = AccountBinance(None, simulation=True)

    if not os.path.exists(results.hourly_filename):
        print("file {} doesn't exist, exiting...".format(results.filename))
        sys.exit(-1)


    hkdb = KlinesDB(accnt, hourly_filename, None)
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
