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
import matplotlib.pyplot as plt
import argparse
from trader.lib.hourly.HourlyMapMovement import HourlyMapMovement
from trader.KlinesDB import KlinesDB
from trader.account.binance.AccountBinance import AccountBinance


def simulate(kdb, symbol, start_ts, end_ts, test_hours=0):
    hourly_map = HourlyMapMovement(symbol, accnt, kdb, win_hours=24)

    hourly_map.hourly_load(start_ts)

    sums = []
    unit_sums = []
    close_prices = []

    count = 0
    msgs = kdb.get_dict_klines(symbol, start_ts, end_ts)
    for msg in msgs:
        close_prices.append(float(msg['close']))

    ts = start_ts # + accnt.hours_to_ts(1)
    while ts <= end_ts:
        ts += 3600 * 1000
        hourly_map.hourly_update(ts)
        #sums.append(hourly_map.get_sum_total())
        #unit_sums.append(hourly_map.get_unit_sum_total())
        sums.append(hourly_map.get_sum_mean())
        unit_sums.append(hourly_map.get_unit_sum_mean())
        #sums.append(hourly_map.get_last_sum())
        #unit_sums.append(hourly_map.get_last_unit_sum())
        #testy.append(hourly_lstm.actual_result)
        #predicty.append(hourly_lstm.predict_result)
        count += 1

    plt.subplot(311)
    symprice, = plt.plot(close_prices, label=symbol)
    plt.legend(handles=[symprice])
    plt.subplot(312)
    fig21, = plt.plot(sums, label='SUMS')
    plt.legend(handles=[fig21])
    plt.subplot(313)
    fig31, = plt.plot(unit_sums, label='UNIT_SUMS')
    plt.legend(handles=[fig31])
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

    parser.add_argument('-k', action='store', dest='hourly_filename',
                        default='binance_hourly_klines_BTC.db',
                        help='filename of hourly kline sqlite db')

    parser.add_argument('-t', action='store', dest='test_hours',
                        default=48,
                        help='Hours before initial kline sqlitedb ts to end model data, and begin test data')

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

    accnt = AccountBinance(None, simulate=True, simulate_db_filename=results.filename)

    if results.filename:
        if not os.path.exists(results.filename):
            print("file {} doesn't exist, exiting...".format(results.filename))
            sys.exit(-1)
        else:
            # first timestamp from kline sqlite db
            start_ts = get_first_timestamp(results.filename, symbol)
            # last timestamp from kline sqlite db
            end_ts = get_last_timestamp(results.filename, symbol)

            # remove minutes and seconds from start timestamp
            start_ts = accnt.get_hourly_ts(start_ts)
            print(time.ctime(int(start_ts / 1000)))
            print(start_ts, end_ts)

    if not os.path.exists(results.hourly_filename):
        print("file {} doesn't exist, exiting...".format(results.filename))
        sys.exit(-1)

    kdb = KlinesDB(accnt, hourly_filename, None)
    print("Loading {}".format(hourly_filename))
    if not start_ts or not end_ts:
        start_ts = kdb.get_table_start_ts(symbol) + accnt.hours_to_ts(24)
        end_ts = kdb.get_table_end_ts(symbol)

    if results.list_table_names:
        for symbol in kdb.get_table_list():
            print(symbol)

    test_hours = int(results.test_hours)

    if symbol:
        simulate(kdb, symbol, start_ts, end_ts, test_hours)
    else:
        parser.print_help()
    kdb.close()
