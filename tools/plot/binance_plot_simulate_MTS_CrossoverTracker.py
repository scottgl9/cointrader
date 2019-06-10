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
from trader.lib.MovingTimeSegment.MTSCrossover2 import MTSCrossover2
from trader.lib.CrossoverTracker import CrossoverTracker
import argparse


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
    timestamps = []
    aema12 = AEMA(12, scale_interval_secs=60)
    aema12_values = []
    aema50 = AEMA(50, scale_interval_secs=60)
    aema50_values = []

    cross_tracker = CrossoverTracker(win_secs=60, hourly_mode=False)

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

        cross_tracker.update(aema12.result, aema50.result, ts)

        close_prices.append(close)
        open_prices.append(open)
        low_prices.append(low)
        high_prices.append(high)
        timestamps.append(ts)
        i += 1

    plt.subplot(211)
    symprice, = plt.plot(close_prices, label=ticker_id)

    for ts in cross_tracker.get_cross_up_timestamps():
        index = timestamps.index(ts)
        plt.axvline(x=index, color='green')

    for ts in cross_tracker.get_cross_down_timestamps():
        index = timestamps.index(ts)
        plt.axvline(x=index, color='red')

    fig1, = plt.plot(aema12_values, label='AEMA12')
    fig3, = plt.plot(aema50_values, label='AEMA50')

    plt.legend(handles=[symprice, fig1, fig3])
    plt.subplot(212)
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
