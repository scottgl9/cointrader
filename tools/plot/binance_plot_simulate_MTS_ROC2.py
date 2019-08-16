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
from trader.indicator.AEMA import AEMA
from trader.indicator.OBV import OBV
from trader.lib.MovingTimeSegment.MTS_ROC2 import MTS_ROC2
import argparse


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

    close_prices = []
    open_prices = []
    low_prices = []
    high_prices = []
    base_volumes = []
    quote_volumes = []

    mts12_roc = MTS_ROC2(win_secs=3600, smoother=AEMA(12, scale_interval_secs=60))
    mts12_roc_values = []
    mts50_roc = MTS_ROC2(win_secs=3600, smoother=AEMA(12, scale_interval_secs=60))
    mts50_roc_values = []
    mts200_roc = MTS_ROC2(win_secs=3600, smoother=AEMA(12, scale_interval_secs=60))
    mts200_roc_values = []
    aema12 = AEMA(12, scale_interval_secs=60)
    aema12_values = []
    aema50 = AEMA(50, scale_interval_secs=60)
    aema50_values = []
    aema200 = AEMA(200, scale_interval_secs=60)
    aema200_values = []

    i=0
    for msg in get_rows_as_msgs(c):
        close = float(msg['c'])
        low = float(msg['l'])
        high = float(msg['h'])
        open = float(msg['o'])
        volume_base = float(msg['v'])
        volume_quote = float(msg['q'])
        ts = int(msg['E'])

        base_volumes.append(volume_base)
        quote_volumes.append(volume_quote)

        aema12_values.append(aema12.update(close, ts))
        aema50_values.append(aema50.update(close, ts))
        aema200_values.append(aema200.update(close, ts))

        mts12_roc.update(aema12.result, ts)
        mts12_roc_values.append(mts12_roc.result)
        mts50_roc.update(aema50.result, ts)
        mts50_roc_values.append(mts50_roc.result)
        mts200_roc.update(aema200.result, ts)
        mts200_roc_values.append(mts200_roc.result)

        close_prices.append(close)
        open_prices.append(open)
        low_prices.append(low)
        high_prices.append(high)

        i += 1

    plt.subplot(211)
    symprice, = plt.plot(close_prices, label=ticker_id)

    fig1, = plt.plot(aema12_values, label='AEMA12')
    fig2, = plt.plot(aema50_values, label='AEMA50')
    fig3, = plt.plot(aema200_values, label='AEMA200')
    plt.legend(handles=[symprice, fig1, fig2, fig3])

    #plt.subplot(312)
    #plt.plot(aema_diff_6_12)

    plt.subplot(212)
    fig21, = plt.plot(mts12_roc_values, label='MTS_ROC_12')
    fig22, = plt.plot(mts50_roc_values, label="MTS_ROC_50")
    fig23, = plt.plot(mts50_roc_values, label="MTS_ROC_200")
    plt.legend(handles=[fig21, fig22, fig23])

    plt.plot(mts200_roc_values)
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
