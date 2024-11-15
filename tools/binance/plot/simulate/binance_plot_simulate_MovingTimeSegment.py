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
import matplotlib.pyplot as plt
import argparse
from trader.lib.MovingTimeSegment.MovingTimeSegment import MovingTimeSegment
from trader.indicator.DTWMA import DTWMA
from trader.indicator.ZLEMA import *


def get_rows_as_msgs(c):
    msgs = []
    for row in c:
        msg = {'E': row[0], 'c': row[1], 'h': row[2], 'l': row[3],
               'o': row[4], 'q': row[5], 's': row[6], 'v': row[7]}
        msgs.append(msg)
    return msgs


def simulate(conn, client, base=None, currency=None, ticker_id=None):
    c = conn.cursor()
    #c.execute("SELECT * FROM miniticker WHERE s='{}' ORDER BY E ASC".format(ticker_id))
    c.execute("SELECT E,c,h,l,o,q,s,v FROM miniticker WHERE s='{}'".format(ticker_id)) # ORDER BY E ASC")")

    ema12 = EMA(12, scale=24)
    ema26 = EMA(26, scale=24)
    ema50 = EMA(100, scale=24, lag_window=5)
    ema200 = EMA(200, scale=24, lag_window=5)

    dtwma = DTWMA(window=30)
    tsv = MovingTimeSegment(seconds=3600, percent_smoother=EMA(100, scale=24))
    tsv_min_ema = EMA(50, scale=24)
    tsv_max_ema = EMA(50, scale=24)
    tsv_min_values = []
    tsv_min_x_values = []
    tsv_max_values = []
    tsv_max_x_values = []
    tsv2 = MovingTimeSegment(seconds=1000, percent_smoother=ZLEMA(100, scale=24))
    tsv_x_values = []
    tsv_values = []
    tsv2_x_values = []
    tsv2_values = []
    tsv_counts = []
    tsv2_counts = []

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

        tsv.update(close, ts)
        if tsv.ready() and tsv.percent_change() != None:
            tsv_x_values.append(i)
            tsv_values.append(tsv.percent_change())
            tsv_counts.append(tsv.value_count())
            if tsv.min() != 0:
                tsv_min_values.append(tsv_min_ema.update(tsv.min()))
                tsv_min_x_values.append(i)
            if tsv.max() != 0:
                tsv_max_values.append(tsv_max_ema.update(tsv.max()))
                tsv_max_x_values.append(i)

        tsv2.update(close, ts)
        if tsv2.ready() and tsv2.percent_change() != None:
            tsv2_x_values.append(i)
            tsv2_values.append(tsv2.percent_change())
            tsv2_counts.append(tsv2.value_count())

        close_prices.append(close)
        open_prices.append(open)
        low_prices.append(low)
        high_prices.append(high)
        #lstsqs_x_values.append(i)
        i += 1

    plt.subplot(311)
    symprice, = plt.plot(close_prices, label=ticker_id)
    fig1, = plt.plot(ema12_values, label='EMA12')
    fig2, = plt.plot(ema26_values, label='EMA26')
    fig3, = plt.plot(ema50_values, label='EMA50')
    fig4, = plt.plot(ema200_values, label='EMA200')
    plt.plot(tsv_min_x_values, tsv_min_values)
    plt.plot(tsv_max_x_values, tsv_max_values)
    plt.legend(handles=[symprice, fig1, fig2, fig3, fig4])
    plt.subplot(312)
    fig21, = plt.plot(tsv_x_values, tsv_values, label='TSV_PERCENT')
    fig22, = plt.plot(tsv2_x_values, tsv2_values, label='TSV2_PERCENT')
    plt.legend(handles=[fig21, fig22])
    plt.subplot(313)
    fig31, = plt.plot(tsv_x_values, tsv_counts, label='TSV_COUNTS')
    fig32, = plt.plot(tsv2_x_values, tsv2_counts, label='TSV2_COUNTS')
    plt.legend(handles=[fig31, fig32])

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

    symbol_default = 'BTCUSDT'
    parser.add_argument('-s', action='store', dest='symbol',
                        default=symbol_default,
                        help='trade symbol')

    results = parser.parse_args()

    if not os.path.exists(results.filename):
        print("file {} doesn't exist, exiting...".format(results.filename))
        sys.exit(-1)

    filename = results.filename
    base = results.base
    currency = results.currency

    print("Loading {}".format(filename))
    conn = sqlite3.connect(filename)

    ticker_id = "{}{}".format(base, currency)
    if results.symbol != symbol_default:
        ticker_id = results.symbol
    simulate(conn, client, ticker_id=ticker_id)
    conn.close()
