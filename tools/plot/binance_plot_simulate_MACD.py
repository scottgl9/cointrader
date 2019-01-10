#!/usr/bin/python

import sys
try:
    import trader
except ImportError:
    sys.path.append('.')
    import trader

import os.path
import time
import sqlite3
from datetime import datetime, timedelta
from pypika import Query, Table, Field, Order
from trader.strategy import *
from datetime import datetime, timedelta
import threading
import sys
from trader.WebHandler import WebThread
from trader.account.binance.client import Client
from trader.MultiTrader import MultiTrader
from trader.account.AccountBinance import AccountBinance
from trader.config import *
import numpy as np
import matplotlib.pyplot as plt
import argparse
import matplotlib
from trader.indicator.EMA import EMA
from trader.indicator.OBV import OBV
from trader.indicator.MACD import MACD
from trader.lib.Crossover2 import Crossover2


def get_rows_as_msgs(c):
    msgs = []
    for row in c:
        msg = {'E': row[0], 'c': row[1], 'h': row[2], 'l': row[3],
               'o': row[4], 'q': row[5], 's': row[6], 'v': row[7]}
        msgs.append(msg)
    return msgs


def simulate(conn, client, base, currency, type="channel"):
    ticker_id = "{}{}".format(base, currency)
    c = conn.cursor()
    #c.execute("SELECT * FROM miniticker WHERE s='{}' ORDER BY E ASC".format(ticker_id))
    c.execute("SELECT E,c,h,l,o,q,s,v FROM miniticker WHERE s='{}'".format(ticker_id)) # ORDER BY E ASC")")

    ema12 = EMA(12, scale=24)
    ema26 = EMA(26, scale=24)
    ema50 = EMA(50, scale=24, lag_window=5)

    macd = MACD(12.0, 26.0, 9.0, scale=24.0)
    macd_cross = Crossover2(window=10)
    macd_zero_cross = Crossover2(window=10)
    macd_signal = EMA(9, scale=24.0)
    macd_diff_values = []
    macd_signal_values = []

    ema12_values = []
    ema26_values = []
    ema50_values = []
    close_prices = []
    open_prices = []
    low_prices = []
    high_prices = []

    i=0
    for msg in get_rows_as_msgs(c):
        close = float(msg['c'])
        low = float(msg['l'])
        high = float(msg['h'])
        open = float(msg['o'])
        volume = float(msg['v'])

        ema12_value = ema12.update(close)
        ema12_values.append(ema12_value)
        ema26_values.append(ema26.update(close))
        ema50_value = ema50.update(close)
        ema50_values.append(ema50_value)

        macd.update(close)
        #if macd.result_signal == 0:
        #    print(i)
        if macd.result != 0 and macd.result_signal != 0:
            value = macd_signal.update(macd.diff)
            macd_diff_values.append(macd.result)
            macd_signal_values.append(value)

        close_prices.append(close)
        open_prices.append(open)
        low_prices.append(low)
        high_prices.append(high)
        #lstsqs_x_values.append(i)
        i += 1

    #plt.subplot(211)
    fig = plt.figure()
    ax = fig.add_subplot(2,1,1)

    symprice, = plt.plot(close_prices, label=ticker_id)

    bought = False
    bought_price = 0
    macd_prices = close_prices[len(close_prices)-len(macd_diff_values):]
    for i in range(0, len(macd_diff_values)):
        macd_zero_cross.update(macd_diff_values[i], 0)
        macd_cross.update(macd_diff_values[i], macd_signal_values[i])
        if macd_zero_cross.crossup_detected():
            if not bought:
                plt.axvline(x=i, color='green')
                bought = True
                bought_price = macd_prices[i]
        elif macd_zero_cross.crossdown_detected():
            if bought and (bought_price * 1.01) < macd_prices[i]:
                plt.axvline(x=i, color='red')
                bought = False
                bought_price = 0
        if macd_cross.crossup_detected():
            if not bought:
                plt.axvline(x=i, color='green')
                bought = True
                bought_price = macd_prices[i]
        elif macd_cross.crossdown_detected():
            if bought and (bought_price * 1.01) < macd_prices[i]:
                plt.axvline(x=i, color='red')
                bought = False
                bought_price = 0

    #plt.plot(filter_x_values, filter_values)
    #plt.plot(low_prices)
    #plt.plot(high_prices)
    #plt.plot(lstsqs_x_values, support1_values)
    #plt.plot(lstsqs_x_values, support2_values)
    #fig1, = plt.plot(ema12_values, label='EMA12')
    #fig2, = plt.plot(ema26_values, label='EMA26')
    #fig3, = plt.plot(ema50_values, label='EMA50')
    plt.legend(handles=[symprice])
    plt.subplot(212)
    fig1, = plt.plot(macd_diff_values, label='MACD DIFF')
    fig2, = plt.plot(macd_signal_values, label='MACD SIG')
    plt.legend(handles=[fig1, fig2])

    #plt.plot(signal_values)
    #plt.plot(tsi_values)
    plt.show()

if __name__ == '__main__':
    client = None

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', action='store', dest='filename',
                        default='cryptocurrency_database.miniticker_collection_04092018.db',
                        help='filename of kline sqlite db')

    parser.add_argument('-b', action='store', dest='base',
                        default='BTC',
                        help='base part of symbol')

    parser.add_argument('-c', action='store', dest='currency',
                        default='USDT',
                        help='currency part of symbol')

    results = parser.parse_args()

    if not os.path.exists(results.filename):
        print("file {} doesn't exist, exiting...".format(results.filename))
        sys.exit(-1)

    filename = results.filename
    base = results.base
    currency = results.currency

    print("Loading {}".format(filename))
    conn = sqlite3.connect(filename)

    simulate(conn, client, base, currency, type="MACD")
    conn.close()
