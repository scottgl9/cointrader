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
from trader.account.binance.client import Client
from trader.config import *
import matplotlib.pyplot as plt
import argparse
from trader.HourlyKlinesDB import HourlyKlinesDB
from trader.indicator.OBV import OBV
from trader.lib.HourlySupportResistance import HourlySupportResistance

def simulate(hkdb, symbol, start_ts, end_ts):
    klines = hkdb.get_klines(symbol, start_ts, end_ts)

    hourlysr = HourlySupportResistance(symbol, None, None, hkdb)
    close_prices = []
    timestamps = []

    i=0
    for kline in klines[int(0.5*len(klines)):]:
        hourlysr.update(kline=kline)
        # if hourlysr.daily_support and hourlysr.daily_resistance:
        #     daily_supports.append(hourlysr.daily_support)
        #     daily_x_supports.append(i)
        #     daily_resistances.append(hourlysr.daily_resistance)
        #     daily_x_resistances.append(i)
        # if hourlysr.weekly_support and hourlysr.weekly_resistance:
        #     weekly_supports.append(hourlysr.weekly_support)
        #     weekly_x_supports.append(i)
        #     weekly_resistances.append(hourlysr.weekly_resistance)
        #     weekly_x_resistances.append(i)
        # if hourlysr.monthly_support and hourlysr.monthly_resistance:
        #     monthly_supports.append(hourlysr.monthly_support)
        #     monthly_x_supports.append(i)
        #     monthly_resistances.append(hourlysr.monthly_resistance)
        #     monthly_x_resistances.append(i)
        close_prices.append(kline.close)
        timestamps.append(kline.ts)
        i += 1

    plt.subplot(211)
    symprice, = plt.plot(close_prices, label=symbol)
    for sr in hourlysr.srlines:
        if sr.type == 1:
            color='yellow'
        elif sr.type == 2:
            color = 'blue'
        elif sr.type == 3:
            color = 'green'
        plt.axhline(y=sr.s, color=color)
        plt.axhline(y=sr.r, color=color)
    #fig1, = plt.plot(weekly_x_supports,  weekly_supports, label='WEEKLY_SUPPORT')
    #fig2, = plt.plot(weekly_x_resistances, weekly_resistances, label='WEEKLY_RESISTANCE')
    #fig3, = plt.plot(monthly_x_supports, monthly_supports, label='MONTHLY_SUPPORT')
    #fig4, = plt.plot(monthly_x_resistances, monthly_resistances, label='MONTHLY_RESISTANCE')
    plt.legend(handles=[symprice]) #, fig1, fig2, fig3, fig4])
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

    hkdb = HourlyKlinesDB(None, hourly_filename, None)
    print("Loading {}".format(hourly_filename))

    if results.list_table_names:
        for symbol in hkdb.get_table_list():
            print(symbol)

    if symbol:
        simulate(hkdb, symbol, start_ts, end_ts)
    else:
        parser.print_help()
    hkdb.close()
