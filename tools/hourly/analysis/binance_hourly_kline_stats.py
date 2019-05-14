#!/usr/bin/python

import sys
try:
    import trader
except ImportError:
    sys.path.append('.')
    import trader

import sqlite3
import sys
import os
import time
from trader.account.AccountBinance import AccountBinance
import argparse
from trader.HourlyKlinesDB import HourlyKlinesDB
from trader.lib.ValueLag import ValueLag


def get_largest_value_change(msgs, field='close', hours=4, direction=1, percent=True):
    lag = ValueLag(window=hours)
    lag_ts = ValueLag(window=hours)
    largest_value_change = 0
    largest_change_start_ts = 0
    largest_change_end_ts = 0
    for msg in msgs:
        value = float(msg[field])
        ts = int(msg['ts'])
        lag_ts.update(int(ts))
        lag.update(value)
        if not lag.ready():
            continue
        last_value = lag.result
        if direction == 1 and last_value and value > last_value:
            if not largest_value_change or (value - last_value) > largest_value_change:
                largest_change_start_ts = int(lag_ts.result)
                largest_change_end_ts = int(ts)
                if percent:
                    largest_value_change = round(100 * (value - last_value) / last_value, 2)
                else:
                    largest_value_change = value - last_value
        elif direction == -1 and last_value and value < last_value:
            if not largest_value_change or (value - last_value) < largest_value_change:
                largest_change_start_ts = int(lag_ts.result)
                largest_change_end_ts = int(ts)
                if percent:
                    largest_value_change = round(100 * (value - last_value) / last_value, 2)
                else:
                    largest_value_change = value - last_value
    return largest_value_change, largest_change_start_ts, largest_change_end_ts


# get longest amount of time where all hourly values delta change is in same direction
def get_longest_trend(msgs, field='close', direction=1, percent=True):
    last_value = 0
    count = 0
    max_count = 0
    max_start_value = 0
    max_start_ts = 0
    max_end_ts = 0
    max_tmp_start_ts = 0
    max_change = 0
    for msg in msgs:
        value = float(msg[field])
        ts = int(msg['ts'])
        if not last_value:
            last_value = value
            continue
        if direction == 1:
            if value > last_value:
                if count == 0:
                    max_start_value = last_value
                    max_tmp_start_ts = ts
                count += 1
            else:
                if count > max_count and max_start_value:
                    max_start_ts = int(max_tmp_start_ts)
                    max_end_ts = int(ts)
                    if percent:
                        max_change = round(100.0 * (value - max_start_value) / max_start_value, 2)
                    else:
                        max_change = value - max_start_value
                    max_count = count
                count = 0
        elif direction == -1:
            if value < last_value:
                if count == 0:
                    max_start_value = last_value
                    max_tmp_start_ts = ts
                count += 1
            else:
                if count > max_count and max_start_value:
                    max_start_ts = int(max_tmp_start_ts)
                    max_end_ts = int(ts)
                    if percent:
                        max_change = round(100.0 * (value - max_start_value) / max_start_value, 2)
                    else:
                        max_change = value - max_start_value
                    max_count = count
                count = 0
        last_value = value
    return max_count, max_change, max_start_ts, max_end_ts


def analyze(hkdb, symbol, start_ts, end_ts):
    msgs = hkdb.get_dict_klines(symbol, start_ts, end_ts)
    print("Largest 4 hour price change {}:".format(symbol))
    value_change, start_ts, end_ts = get_largest_value_change(msgs, hours=4, direction=1)
    print(value_change, time.ctime(start_ts/1000), time.ctime(end_ts/1000))
    value_change, start_ts, end_ts = get_largest_value_change(msgs, hours=4, direction=-1)
    print(value_change, time.ctime(start_ts/1000), time.ctime(end_ts/1000))
    print("Largest 8 hour price change {}:".format(symbol))
    value_change, start_ts, end_ts = get_largest_value_change(msgs, hours=8, direction=1)
    print(value_change, time.ctime(start_ts/1000), time.ctime(end_ts/1000))
    value_change, start_ts, end_ts = get_largest_value_change(msgs, hours=8, direction=-1)
    print(value_change, time.ctime(start_ts/1000), time.ctime(end_ts/1000))
    print("Largest 24 hour price change {}:".format(symbol))
    value_change, start_ts, end_ts = get_largest_value_change(msgs, hours=24, direction=1)
    print(value_change, time.ctime(start_ts/1000), time.ctime(end_ts/1000))
    value_change, start_ts, end_ts = get_largest_value_change(msgs, hours=24, direction=-1)
    print(value_change, time.ctime(start_ts/1000), time.ctime(end_ts/1000))
    print("Longest trend {}:".format(symbol))
    max_count, max_change, start_ts, end_ts = get_longest_trend(msgs, direction=1)
    print(max_count, max_change, time.ctime(start_ts/1000), time.ctime(end_ts/1000))
    max_count, max_change, start_ts, end_ts = get_longest_trend(msgs, direction=-1)
    print(max_count, max_change, time.ctime(start_ts/1000), time.ctime(end_ts/1000))


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


    if not os.path.exists(results.hourly_filename):
        print("file {} doesn't exist, exiting...".format(results.filename))
        sys.exit(-1)

    accnt = AccountBinance(None, simulation=True)

    hkdb = HourlyKlinesDB(accnt, hourly_filename, None)
    print("Loading {}".format(hourly_filename))

    if results.list_table_names:
        for symbol in hkdb.get_table_list():
            print(symbol)

    if symbol:
        analyze(hkdb, symbol, start_ts, end_ts)
    else:
        parser.print_help()
    hkdb.close()
