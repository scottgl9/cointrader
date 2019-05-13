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
from trader.account.AccountBinance import AccountBinance
import argparse
from trader.HourlyKlinesDB import HourlyKlinesDB
from trader.lib.ValueLag import ValueLag


def get_largest_value_change(msgs, field='close', hours=4, direction=1, percent=True):
    lag = ValueLag(window=hours)
    largest_value_change = 0
    for msg in msgs:
        value = float(msg[field])
        lag.update(value)
        if not lag.ready():
            continue
        last_value = lag.result
        if direction == 1 and last_value and value > last_value:
            if not largest_value_change or (value - last_value) > largest_value_change:
                if percent:
                    largest_value_change = round(100 * (value - last_value) / last_value, 2)
                else:
                    largest_value_change = value - last_value
        elif direction == -1 and last_value and value < last_value:
            if not largest_value_change or (value - last_value) < largest_value_change:
                if percent:
                    largest_value_change = round(100 * (value - last_value) / last_value, 2)
                else:
                    largest_value_change = value - last_value
    return largest_value_change


# get longest amount of time where all hourly values delta change is in same direction
def get_longest_trend(msg, field='close', direction=1, percent=True):
    pass


def analyze(hkdb, symbol, start_ts, end_ts):
    msgs = hkdb.get_dict_klines(symbol, start_ts, end_ts)
    print("Largest 4 hour price change {}:".format(symbol))
    print(get_largest_value_change(msgs, hours=4, direction=1))
    print(get_largest_value_change(msgs, hours=4, direction=-1))
    print("Largest 8 hour price change {}:".format(symbol))
    print(get_largest_value_change(msgs, hours=8, direction=1))
    print(get_largest_value_change(msgs, hours=8, direction=-1))
    print("Largest 24 hour price change {}:".format(symbol))
    print(get_largest_value_change(msgs, hours=24, direction=1))
    print(get_largest_value_change(msgs, hours=24, direction=-1))


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
    hkdb.close()
