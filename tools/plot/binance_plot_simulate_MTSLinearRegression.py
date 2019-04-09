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
import matplotlib.pyplot as plt
from trader.indicator.native.AEMA import AEMA
from trader.lib.MovingTimeSegment.MTSLinearRegression import MTSLinearRegression
import argparse
import numpy as np


def get_rows_as_msgs(c):
    msgs = []
    for row in c:
        msg = {'E': row[0], 'c': row[1], 'h': row[2], 'l': row[3],
               'o': row[4], 'q': row[5], 's': row[6], 'v': row[7]}
        msgs.append(msg)
    return msgs


def simulate(conn, client, base, currency):
    ticker_id = "{}{}".format(base, currency)
    c = conn.cursor()
    #c.execute("SELECT * FROM miniticker WHERE s='{}' ORDER BY E ASC".format(ticker_id))
    c.execute("SELECT E,c,h,l,o,q,s,v FROM miniticker WHERE s='{}'".format(ticker_id)) # ORDER BY E ASC")")

    close_prices = []
    open_prices = []
    low_prices = []
    high_prices = []
    base_volumes = []
    quote_volumes = []
    kline_x_values = []
    pred_values = []
    prev_values = None
    values = None

    aema6 = AEMA(6, scale_interval_secs=60)
    mtslr = MTSLinearRegression()

    count=0
    i=0
    for msg in get_rows_as_msgs(c):
        close = float(msg['c'])
        volume_base = float(msg['v'])
        volume_quote = float(msg['q'])
        ts = int(msg['E'])

        close_prices.append(close)

        aema6.update(close, ts)
        if not aema6.ready():
            i += 1
            continue

        mtslr.update(aema6.result, ts)
        if mtslr.updated():
            values = mtslr.pred_values
            pred_values = pred_values + values
        i += 1

    plt.subplot(211)
    symprice, = plt.plot(close_prices, label=ticker_id)

    #fig1, = plt.plot(kline_x_values, open_prices, label='open')
    #fig2, = plt.plot(close_prices, label='close')
    #fig3, = plt.plot(kline_x_values, low_prices, label='low')
    #fig4, = plt.plot(kline_x_values, high_prices, label='high')
    plt.plot(pred_values)
    #plt.plot(low_prices)
    #plt.plot(high_prices)

    #plt.legend(handles=[symprice, fig3, fig4])
    plt.subplot(212)
    #plt.plot(obv_aema12_values)
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

    simulate(conn, client, base, currency)
    conn.close()
