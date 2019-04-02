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
from trader.lib.MovingTimeSegment.MTSKline import MTSKline
import argparse


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

    close_prices = []
    open_prices = []
    low_prices = []
    high_prices = []
    base_volumes = []
    quote_volumes = []
    kline_x_values = []

    aema12 = AEMA(12, scale_interval_secs=60)
    kline = MTSKline(win_size_secs=300)

    i=0
    for msg in get_rows_as_msgs(c):
        close = float(msg['c'])
        volume_base = float(msg['v'])
        volume_quote = float(msg['q'])
        ts = int(msg['E'])

        aema12.update(close, ts)
        if aema12.ready():
            result = kline.update(aema12.result, ts)
            if result and kline.ready():
                open_prices.append(result.open)
                close_prices.append(result.close)
                low_prices.append(result.low)
                high_prices.append(result.high)
                kline_x_values.append(i)

        base_volumes.append(volume_base)
        quote_volumes.append(volume_quote)

        i += 1

    plt.subplot(211)
    symprice, = plt.plot(kline_x_values, close_prices, label=ticker_id)

    #fig1, = plt.plot(kline_x_values, open_prices, label='open')
    #fig2, = plt.plot(close_prices, label='close')
    fig3, = plt.plot(kline_x_values, low_prices, label='low')
    fig4, = plt.plot(kline_x_values, high_prices, label='high')
    #plt.plot(low_prices)
    #plt.plot(high_prices)

    plt.legend(handles=[symprice, fig3, fig4])
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

    simulate(conn, client, base, currency, type="MACD")
    conn.close()
