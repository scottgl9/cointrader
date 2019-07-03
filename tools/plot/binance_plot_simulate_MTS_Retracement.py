#!/usr/bin/python

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
from trader.indicator.AEMA import AEMA
from trader.lib.MovingTimeSegment.MTS_Retracement import MTS_Retracement

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

    aema12 = AEMA(50, scale_interval_secs=60)
    mts_retracement = MTS_Retracement(win_secs=3600)
    mts_avg1_values = []
    mts_avg2_values = []
    mts_mts1_min_values = []
    mts_mts1_max_values = []
    mts_mts1_x_values = []
    mts_mts2_min_values = []
    mts_mts2_max_values = []
    mts_mts2_x_values = []

    mts1_max_value_diff_values = []
    mts1_value_min_diff_values = []

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

        mts_retracement.update(aema12.result, ts)
        if mts_retracement.crossup_detected(clear=True):
            valleys.append(i)
        elif mts_retracement.crossdown_detected(clear=True):
            peaks.append(i)

        if mts_retracement.mts1_avg() != 0:
            mts_avg1_values.append(mts_retracement.mts1_avg())
            mts_avg2_values.append(mts_retracement.mts2_avg())

        mts1 = mts_retracement.get_short_mts1()
        if mts1.ready() and mts1.min():
            mts_mts1_min_values.append(mts1.min())
            mts_mts1_x_values.append(i)
        if mts1.ready() and mts1.max():
            mts_mts1_max_values.append(mts1.max())

        mts2 = mts_retracement.get_short_mts2()
        if mts2.ready() and mts2.min():
            mts_mts2_min_values.append(mts2.min())
            mts_mts2_x_values.append(i)
        if mts2.ready() and mts2.max():
            mts_mts2_max_values.append(mts2.max())

        #if mts_retracement.mts1_max_value_diff():
        #    mts1_max_value_diff_values.append(mts_retracement.mts1_max_value_diff())

        #if mts_retracement.mts1_value_min_diff():
        #    mts1_value_min_diff_values.append(mts_retracement.mts1_value_min_diff())

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
    #fig2, = plt.plot(lsma_values, label="LSMA")
    #fig2, = plt.plot(mts_mts1_x_values, mts_mts1_min_values, label="MTS1_MIN")
    #fig3, = plt.plot(mts_mts1_x_values, mts_mts1_max_values, label="MTS1_MAX")
    fig4, = plt.plot(mts_mts2_x_values, mts_mts2_min_values, label="MTS2_MIN")
    fig5, = plt.plot(mts_mts2_x_values, mts_mts2_max_values, label="MTS2_MAX")

    plt.legend(handles=[symprice, fig1, fig4, fig5])
    plt.subplot(212)
    plt.plot(mts_avg1_values)
    plt.plot(mts_avg2_values)
    #plt.plot(mts1_max_value_diff_values)
    #plt.plot(mts1_value_min_diff_values)
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
