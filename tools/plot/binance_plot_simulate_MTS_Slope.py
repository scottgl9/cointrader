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
from trader.lib.MovingTimeSegment.MTS_Slope import MTS_Slope
from trader.lib.MovingTimeSegment.MTS_LSMA import MTS_LSMA
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
    obv = OBV()
    obv_aema12 = AEMA(12, scale_interval_secs=60)
    obv_aema12_values = []
    aema50 = AEMA(50, scale_interval_secs=60)
    aema50_values = []
    aema200 = AEMA(200, scale_interval_secs=60)
    aema200_values = []
    mts_lsma = MTS_LSMA(win_secs=3600)
    mts_lsma_values = []
    mts_lsma_slopes = []
    mts_slope = MTS_Slope(win_secs=3600, slope_secs=900)
    mts_slope_values = []


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

        obv.update(close, volume_base)
        obv_aema12.update(obv.result, ts)
        obv_aema12_values.append(obv_aema12.result)
        aema50_values.append(aema50.update(close, ts))
        aema200_values.append(aema200.update(close, ts))

        mts_lsma.update(close, ts)
        mts_lsma_values.append(mts_lsma.result)
        mts_lsma_slopes.append(mts_lsma.m)

        mts_slope.update(aema200.result, ts)
        mts_slope_values.append(mts_slope.result)

        close_prices.append(close)
        open_prices.append(open)
        low_prices.append(low)
        high_prices.append(high)

        i += 1

    plt.subplot(211)
    symprice, = plt.plot(close_prices, label=ticker_id)

    fig1, = plt.plot(aema50_values, label='AEMA50')
    fig2, = plt.plot(aema200_values, label='AEMA200')
    fig3, = plt.plot(mts_lsma_values, label="MTS_LSMA")
    plt.legend(handles=[symprice, fig1, fig2, fig3])

    #plt.subplot(312)
    #plt.plot(aema_diff_6_12)

    plt.subplot(212)
    #plt.plot(mts_slope_values)
    plt.plot(mts_lsma_slopes)
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
