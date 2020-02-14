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
from trader.lib.MovingTimeSegment.MTSPercentChange import MTSPercentChange
from trader.lib.MovingTimeSegment.MTSPercentChangeROC import MTSPercentChangeROC

from trader.indicator.DTWMA import DTWMA
from trader.indicator.EMA import EMA
from trader.indicator.DTWMA_EMA import DTWMA_EMA


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
    ema50 = EMA(100, scale=24)
    ema200 = EMA(200, scale=24)

    dtwma = DTWMA(window=30)

    #tspc12 = TimeSegmentPercentChange(seconds=3600)
    #tspc12_values = []
    #tspc12_x_values = []

    tspc1 = MTSPercentChange(seconds=3600, smoother=DTWMA_EMA(30, 200, scale=24))
    tspc1_values = []
    tspc1_x_values = []

    tspc4 = MTSPercentChange(seconds=3600*4, smoother=DTWMA_EMA(30, 200, scale=24))
    tspc4_values = []
    tspc4_x_values = []

    tspc12 = MTSPercentChange(seconds=3600*12, smoother=DTWMA_EMA(30, 200, scale=24))
    tspc12_values = []
    tspc12_x_values = []

    tspc30 = MTSPercentChange(seconds=1800, smoother=DTWMA_EMA(30, 200, scale=24))
    tspc30_values = []
    tspc30_x_values = []

    tspc_roc = MTSPercentChangeROC(tspc_seconds=500, roc_seconds=500, smoother=EMA(12))
    tspc_roc_values = []
    tspc_roc_x_values = []

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

        tspc1.update(close, ts)
        percent = tspc1.get_percent_change()
        tspc1_values.append(percent)
        tspc1_x_values.append(i)

        tspc12.update(close, ts)
        percent = tspc12.get_percent_change()
        tspc12_values.append(percent)
        tspc12_x_values.append(i)

        tspc4.update(close, ts)
        percent = tspc4.get_percent_change()
        tspc4_values.append(percent)
        tspc4_x_values.append(i)

        tspc30.update(close, ts)
        percent = tspc30.get_percent_change()
        tspc30_values.append(percent)
        tspc30_x_values.append(i)

        tspc_roc.update(close, ts)
        tspc_roc_values.append(tspc_roc.result)
        tspc_roc_x_values.append(i)

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
    plt.legend(handles=[symprice, fig1, fig2, fig3, fig4])
    plt.subplot(312)
    #fig21, = plt.plot(tspc12_x_values, tspc12_values, label='TSPC12')
    fig21, = plt.plot(tspc1_x_values, tspc1_values, label='TSPC1')
    fig22, = plt.plot(tspc12_x_values, tspc12_values, label='TSPC12')
    fig23, = plt.plot(tspc4_x_values, tspc4_values, label='TSPC4')
    fig24, = plt.plot(tspc30_x_values, tspc30_values, label='TSPC30')
    plt.legend(handles=[fig21, fig22, fig23, fig24])
    plt.subplot(313)
    plt.plot(tspc_roc_x_values, tspc_roc_values)
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
