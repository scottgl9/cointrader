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
from trader.account.binance.client import Client
from trader.config import *
import matplotlib.pyplot as plt
import argparse
from trader.KlinesDB import KlinesDB
from trader.indicator.OBV import OBV
from trader.indicator.EMA import EMA
from trader.lib.HourlySupportResistance import HourlySupportResistance, HourlySRLine


def plot(kdb, symbol, start_ts, end_ts, daily, weekly, monthly):
    klines = kdb.get_klines(symbol, start_ts, end_ts)

    # plot all if all are false
    if not daily and not weekly and not monthly:
        daily = True
        weekly = True
        monthly = True

    hourlysr = HourlySupportResistance(symbol, None, None, kdb)
    close_prices = []
    timestamps = []
    ema12 = EMA(12)
    ema12_values = []

    i=0
    for kline in klines:#[int(0.5*len(klines)):]:
        ema12.update(kline.close)
        ema12_values.append(ema12.result)
        kline.close = ema12.result
        hourlysr.update(kline=kline)
        close_prices.append(kline.close)
        timestamps.append(kline.ts)
        i += 1

    plt.subplot(211)
    symprice, = plt.plot(close_prices, label=symbol)
    fig1, = plt.plot(ema12_values, label="EMA12")
    for sr in hourlysr.srlines:
        if daily and sr.type == HourlySRLine.SRTYPE_DAILY:
            start = timestamps.index(sr.start_ts)
            end = timestamps.index(sr.end_ts)
            plt.hlines(y=sr.s, xmin=start, xmax=end, color='green')
            plt.hlines(y=sr.r, xmin=start, xmax=end, color='red')
        elif weekly and sr.type == HourlySRLine.SRTYPE_WEEKLY:
            start = timestamps.index(sr.start_ts)
            end = timestamps.index(sr.end_ts)
            plt.hlines(y=sr.s, xmin=start, xmax=end, color='blue')
            plt.hlines(y=sr.r, xmin=start, xmax=end, color='orange')
        elif monthly and sr.type == HourlySRLine.SRTYPE_MONTHLY:
            start = timestamps.index(sr.start_ts)
            end = timestamps.index(sr.end_ts)
            plt.hlines(y=sr.s, xmin=start, xmax=end, color='purple')
            plt.hlines(y=sr.r, xmin=start, xmax=end, color='yellow')
    #fig1, = plt.plot(weekly_x_supports,  weekly_supports, label='WEEKLY_SUPPORT')
    #fig2, = plt.plot(weekly_x_resistances, weekly_resistances, label='WEEKLY_RESISTANCE')
    #fig3, = plt.plot(monthly_x_supports, monthly_supports, label='MONTHLY_SUPPORT')
    #fig4, = plt.plot(monthly_x_resistances, monthly_resistances, label='MONTHLY_RESISTANCE')
    plt.legend(handles=[symprice, fig1]) #, fig1, fig2, fig3, fig4])
    plt.subplot(212)
    #plt.legend(handles=[fig21, fig22, fig23])
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

    parser.add_argument('-d', action='store_true', dest='daily',
                        default=False,
                        help='plot daily s/r lines')

    parser.add_argument('-w', action='store_true', dest='weekly',
                        default=False,
                        help='plot weekly s/r lines')

    parser.add_argument('-m', action='store_true', dest='monthly',
                        default=False,
                        help='plot monthly s/r lines')

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
            end_ts = get_last_timestamp(results.filename, symbol)
            start_ts = get_first_timestamp(results.filename, symbol)
            start_ts = start_ts - 1000 * 3600 * int(results.hours)
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
        plot(kdb, symbol, start_ts, end_ts, results.daily, results.weekly, results.monthly)
    else:
        parser.print_help()
    kdb.close()
