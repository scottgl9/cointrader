#!/usr/bin/env python3

import sys
import os
try:
    import trader
except ImportError:
    sys.path.append('.')
    import trader

import sqlite3
from trader.account.binance.client import Client
from trader.config import *
import matplotlib.pyplot as plt
import argparse
from trader.indicator.DTWMA import DTWMA
from trader.indicator.ZLEMA import *
from trader.lib.MovingTimeSegment.MTS_PeakValleyDetect import MTS_PeakValleyDetect
from trader.indicator.AEMA import AEMA
from trader.lib.MovingTimeSegment.MTS_LSMA import MTS_LSMA

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

    aema12 = AEMA(50, scale_interval_secs=60)
    lsma = MTS_LSMA(3600)

    mtspvd = MTS_PeakValleyDetect()

    aema12_values = []
    lsma_values = []
    open_prices = []
    low_prices = []
    high_prices = []
    volumes = []
    timestamps = []
    close_prices = []

    peaks = []
    valleys = []

    i=0
    for msg in get_rows_as_msgs(c):
        close = float(msg['c'])
        low = float(msg['l'])
        high = float(msg['h'])
        open = float(msg['o'])
        volume = float(msg['v'])
        ts=int(msg['E'])
        volumes.append(volume)

        aema12.update(close, ts)
        aema12_values.append(aema12.result)

        lsma.update(close, ts)
        lsma_values.append(lsma.result)

        mtspvd.update(aema12.result, ts)
        if mtspvd.peak_detect():
            peaks.append(i)
        elif mtspvd.valley_detect():
            valleys.append(i)
        close_prices.append(close)
        open_prices.append(open)
        low_prices.append(low)
        high_prices.append(high)
        timestamps.append(ts)
        i += 1

    plt.subplot(211)
    for peak in peaks:
        plt.axvline(x=peak, color='red')
    for valley in valleys:
        plt.axvline(x=valley, color='green')
    symprice, = plt.plot(close_prices, label=ticker_id)
    fig1, = plt.plot(aema12_values, label="AEMA12")
    fig2, = plt.plot(lsma_values, label="LSMA")

    plt.legend(handles=[symprice, fig1, fig2])
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
