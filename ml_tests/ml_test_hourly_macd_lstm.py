#!/usr/bin/python
# test HourlyLSTM class

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
from trader.lib.DataFrameMLHelper import DataFrameMLHelper
from trader.lib.Crossover2 import Crossover2
from trader.indicator.EMA import EMA
from trader.indicator.MACD import MACD
from numpy import hstack

def create_labels(ema_values, timestamps, cross_up_timestamps, cross_down_timestamps):
    # get rid of last cross up
    if len(cross_up_timestamps) > len(cross_down_timestamps):
        len_diff = len(cross_down_timestamps) - len(cross_up_timestamps)
        cross_up_timestamps = cross_up_timestamps[:len_diff]

    labels = []
    last_label_index = 0
    offset = 4

    for i in range(0, len(cross_up_timestamps)):
        cross_up_ts = cross_up_timestamps[i]
        cross_down_ts = cross_down_timestamps[i]
        cross_up_index = list(timestamps).index(cross_up_ts)
        cross_down_index = list(timestamps).index(cross_down_ts)

        cross_up_value = ema_values[cross_up_index]
        cross_down_value = ema_values[cross_down_index]
        pchange = 100.0 * (cross_down_value - cross_up_value) / cross_up_value
        if pchange <= 1.0:
            continue
        for i in range(last_label_index, cross_down_index + 1):
            if cross_up_index - offset <= i <= cross_up_index + offset:
                labels.append(2)
            elif cross_down_index - offset <= i <= cross_down_index + offset:
                labels.append(1)
            else:
                labels.append(0)
        last_label_index = cross_down_index + 1
    for i in range(last_label_index, len(ema_values)):
        labels.append(0)
    return labels

def simulate(hkdb, symbol, train_start_ts, train_end_ts, test_start_ts, test_end_ts):
    mlhelper = DataFrameMLHelper()
    cross = Crossover2()
    crossups = []
    crossdowns = []
    cross_up_timestamps = []
    cross_down_timestamps = []
    df = hkdb.get_pandas_klines(symbol, train_start_ts, train_end_ts)
    macd = MACD(short_weight=12.0, long_weight=26.0, signal_weight=9.0, scale=24.0)
    ema = EMA(12, scale=24)
    ema_values = []
    macd_values = []
    macd_signal_values = []
    last_cross_type = 0

    i = 0
    close_values = df['close'].values
    timestamps = df['ts'].values
    for close in close_values:
        ema.update(close)
        ema_values.append(ema.result)
        macd.update(close)
        cross.update(macd.result, macd.signal.result)
        if cross.crossup_detected() and last_cross_type != 1:
            ts = timestamps[i]
            crossups.append(i)
            cross_up_timestamps.append(ts)
            last_cross_type = 1
        if cross.crossdown_detected() and last_cross_type != -1:
            ts = timestamps[i]
            crossdowns.append(i)
            cross_down_timestamps.append(ts)
            last_cross_type = -1
        macd_values.append(macd.result)
        macd_signal_values.append(macd.signal.result)
        i += 1

    labels = create_labels(ema_values, timestamps, cross_up_timestamps, cross_down_timestamps)

    macd_df = mlhelper.series_to_supervised(macd_values, 3, 0).values
    macd_signal_df = mlhelper.series_to_supervised(macd_signal_values, 3, 0).values
    print(hstack((macd_df, macd_signal_df)))
    print(macd_df)
    print(macd_signal_df)
    testy = []
    predicty = []

    column_count = 3
    count = 0
    ts = test_start_ts
    while ts <= test_end_ts:
        end_ts = ts
        start_ts = ts - 1000 * 3600 * (column_count - 1)
        #df_test = hkdb.get_pandas_klines(symbol, start_ts, end_ts)
        #print(df_test)
        ts += 3600 * 1000
        count += 1

    plt.subplot(211)
    for i in crossups:
        plt.axvline(x=i, color='green')
    for i in crossdowns:
        plt.axvline(x=i, color='red')
    fig1, = plt.plot(close_values, label=symbol)
    fig2, = plt.plot(ema_values, label="EMA12")
    plt.legend(handles=[fig1, fig2])
    plt.subplot(212)
    fig1, = plt.plot(macd_values, label='MACD')
    fig2, = plt.plot(macd_signal_values, label='MACD_SIGNAL')
    plt.legend(handles=[fig1, fig2])
    plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-k', action='store', dest='hourly_filename',
                        default='binance_hourly_klines.db',
                        help='filename of hourly kline sqlite db')

    parser.add_argument('-p', action='store', dest='split_percent',
                        default='70',
                        help='Percent of klines to use for training (remaining used for test')

    parser.add_argument('-s', action='store', dest='symbol',
                        default='',
                        help='trade symbol')

    results = parser.parse_args()
    if not results.symbol:
        parser.print_help()
        sys.exit(0)

    accnt = AccountBinance(None, simulation=True)

    if not os.path.exists(results.hourly_filename):
        print("file {} doesn't exist, exiting...".format(results.filename))
        sys.exit(-1)


    hkdb = HourlyKlinesDB(accnt, results.hourly_filename, None)
    print("Loading {}".format(results.hourly_filename))

    total_row_count = hkdb.get_table_row_count(results.symbol)
    train_end_index = int(total_row_count * float(results.split_percent) / 100.0)

    train_start_ts = hkdb.get_table_start_ts(results.symbol)
    train_end_ts = hkdb.get_table_ts_by_offset(results.symbol, train_end_index)
    test_start_ts = hkdb.get_table_ts_by_offset(results.symbol, train_end_index + 1)
    test_end_ts = hkdb.get_table_end_ts(results.symbol)

    if results.symbol:
        simulate(hkdb, results.symbol, train_start_ts, train_end_ts, test_start_ts, test_end_ts)
    else:
        parser.print_help()
    hkdb.close()
