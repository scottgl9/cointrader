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
from trader.lib.TimeSegmentValues import TimeSegmentValues
from trader.lib.TimeSegmentPercentChange import TimeSegmentPercentChange
from trader.indicator.DTWMA import DTWMA
from trader.indicator.EMA import EMA


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
    ema50 = EMA(100, scale=24, lag_window=5)
    ema200 = EMA(200, scale=24, lag_window=5)

    dtwma = DTWMA(window=30)

    tspc12 = TimeSegmentPercentChange(seconds=3600)
    tspc12_values = []
    tspc12_x_values = []

    tspc50 = TimeSegmentPercentChange(seconds=3600)
    tspc50_values = []
    tspc50_x_values = []

    tspc50_12 = TimeSegmentPercentChange(seconds=3600*4)
    tspc50_12_values = []
    tspc50_12_x_values = []

    tspc200 = TimeSegmentPercentChange(seconds=3600)
    tspc200_values = []
    tspc200_x_values = []

    ema12_values = []
    ema26_values = []
    ema50_values = []
    ema200_values = []
    close_prices = []
    open_prices = []
    low_prices = []
    high_prices = []
    volumes = []

    i=0
    for msg in get_rows_as_msgs(c):
        close = float(msg['c'])
        low = float(msg['l'])
        high = float(msg['h'])
        open = float(msg['o'])
        volume = float(msg['v'])
        ts=int(msg['E'])
        volumes.append(volume)

        ema12_value = ema12.update(close)
        ema12_values.append(ema12_value)
        ema26_values.append(ema26.update(close))
        ema50_value = ema50.update(close)
        ema50_values.append(ema50_value)
        ema200_value = ema200.update(close)
        ema200_values.append(ema200_value)

        tspc12.update(ema12.result, ts)
        if 1: #tspc12.ready():
            percent = tspc12.get_percent_change()
            tspc12_values.append(percent)
            tspc12_x_values.append(i)

        tspc50.update(ema50.result, ts)
        percent = tspc50.get_percent_change()
        tspc50_values.append(percent)
        tspc50_x_values.append(i)

        tspc50_12.update(ema50.result, ts)
        percent = tspc50_12.get_percent_change()
        tspc50_12_values.append(percent)
        tspc50_12_x_values.append(i)

        tspc200.update(ema200.result, ts)
        if 1: #tspc200.ready():
            percent = tspc200.get_percent_change()
            tspc200_values.append(percent)
            tspc200_x_values.append(i)


        close_prices.append(close)
        open_prices.append(open)
        low_prices.append(low)
        high_prices.append(high)
        #lstsqs_x_values.append(i)
        i += 1

    plt.subplot(211)
    symprice, = plt.plot(close_prices, label=ticker_id)
    fig1, = plt.plot(ema12_values, label='EMA12')
    fig2, = plt.plot(ema26_values, label='EMA26')
    fig3, = plt.plot(ema50_values, label='EMA50')
    fig4, = plt.plot(ema200_values, label='EMA200')
    plt.legend(handles=[symprice, fig1, fig2, fig3, fig4])
    plt.subplot(212)
    fig21, = plt.plot(tspc12_x_values, tspc12_values, label='TSPC12')
    fig22, = plt.plot(tspc50_x_values, tspc50_values, label='TSPC50')
    fig23, = plt.plot(tspc200_x_values, tspc200_values, label='TSPC200')
    fig24, = plt.plot(tspc50_12_x_values, tspc50_12_values, label='TSPC50_12')

    plt.legend(handles=[fig21, fig22, fig23, fig24])

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
