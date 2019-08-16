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
from trader.lib.MovingTimeSegment.MTSCrossAngle import MTSCrossAngle
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
    obv = OBV()
    obv_aema12 = AEMA(12, scale_interval_secs=60)
    obv_aema12_values = []
    aema12 = AEMA(12, scale_interval_secs=60)
    aema12_values = []
    aema12_300 = AEMA(12, scale_interval_secs=300)
    aema12_300_values = []
    aema26 = AEMA(26, scale_interval_secs=60)
    aema26_values = []
    aema50 = AEMA(50, scale_interval_secs=60)
    aema50_values = []

    mts_cross = MTSCrossAngle(win_secs=60)
    up_crosses = []
    down_crosses = []
    up_cross_points = []
    down_cross_points = []
    angles1 = []
    angles2 = []

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
        aema12_values.append(aema12.update(close, ts))
        aema50_values.append(aema50.update(close, ts))

        mts_cross.update(ma1_result=aema12.result, ma2_result=aema50.result, ts=ts)
        if mts_cross.crossup_detected():
            up_crosses.append(i)
            if mts_cross.cross_up_ts:
                up_cross_points.append(timestamps.index(mts_cross.cross_up_ts))
        if mts_cross.crossdown_detected():
            down_crosses.append(i)
            if mts_cross.cross_down_ts:
                down_cross_points.append(timestamps.index(mts_cross.cross_down_ts))

        angle1, angle2 = mts_cross.cross_angle()
        angles1.append(angle1)
        angles2.append(angle2)

        close_prices.append(close)
        open_prices.append(open)
        low_prices.append(low)
        high_prices.append(high)
        timestamps.append(ts)
        i += 1

    plt.subplot(211)
    symprice, = plt.plot(close_prices, label=ticker_id)

    #for i in up_crosses:
    #    plt.axvline(x=i, color='green')
    #for i in down_crosses:
    #    plt.axvline(x=i, color='red')

    for i in up_cross_points:
        plt.axvline(x=i, color='green')
    for i in down_cross_points:
        plt.axvline(x=i, color='red')

    fig1, = plt.plot(aema12_values, label='AEMA12')
    #fig2, = plt.plot(aema26_values, label='AEMA26')
    fig3, = plt.plot(aema50_values, label='AEMA50')
    #fig4, = plt.plot(aema12_300_values, label='AEMA12_300')
    #plt.plot(low_prices)
    #plt.plot(high_prices)

    plt.legend(handles=[symprice, fig1, fig3])
    plt.subplot(212)
    plt.plot(angles1)
    plt.plot(angles2)
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

    parser.add_argument('-s', action='store', dest='symbol',
                        default='BTCUSDT',
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

    simulate(conn, client, base, currency)
    conn.close()
