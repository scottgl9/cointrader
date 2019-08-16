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
import argparse
from trader.indicator.EMA import EMA
from trader.indicator.AEMA import AEMA
from trader.lib.TrendState.TrendStateTrack import TrendStateTrack
from trader.lib.TrendState.TrendStateInfo import TrendStateInfo


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

    aema12 = AEMA(12, scale_interval_secs=60)
    aema26 = AEMA(26, scale_interval_secs=60)
    aema50 = AEMA(100, scale_interval_secs=60)
    aema200 = AEMA(200, scale_interval_secs=60)

    tst = TrendStateTrack()#smoother=EMA(12, scale=24))

    aema12_values = []
    aema26_values = []
    aema50_values = []
    aema200_values = []
    close_prices = []
    open_prices = []
    low_prices = []
    high_prices = []
    volumes = []

    last_trend_string = ''
    last_short_trend_string = ''
    state_indices = []

    i=0
    for msg in get_rows_as_msgs(c):
        close = float(msg['c'])
        low = float(msg['l'])
        high = float(msg['h'])
        open = float(msg['o'])
        volume = float(msg['v'])
        ts=int(msg['E'])
        volumes.append(volume)

        aema12_value = aema12.update(close)
        aema12_values.append(aema12_value)
        aema26_values.append(aema26.update(close))
        aema50_value = aema50.update(close)
        aema50_values.append(aema50_value)
        aema200_value = aema200.update(close)
        aema200_values.append(aema200_value)

        tst.update(close=close, ts=ts)
        if tst.get_trend_string() != last_trend_string:
            state_indices.append((i, tst.get_trend_direction()))
            print("LONG:" + tst.get_trend_string())
            last_trend_string = tst.get_trend_string()

        close_prices.append(close)
        open_prices.append(open)
        low_prices.append(low)
        high_prices.append(high)
        #lstsqs_x_values.append(i)
        i += 1



    plt.subplot(211)
    for (i, dir) in state_indices:
        if dir == 1:
            plt.axvline(x=i, color='green')
        elif dir == -1:
            plt.axvline(x=i, color='red')
    symprice, = plt.plot(close_prices, label=ticker_id)
    fig1, = plt.plot(aema12_values, label='AEMA12')
    fig2, = plt.plot(aema26_values, label='AEMA26')
    fig3, = plt.plot(aema50_values, label='AEMA50')
    fig4, = plt.plot(aema200_values, label='AEMA200')
    plt.legend(handles=[symprice, fig1, fig2, fig3, fig4])
    plt.subplot(212)

    #fig1, = plt.plot(tst.get_seg_down_list('percent'), label='seg_down')
    #fig2, = plt.plot(tst.get_seg_up_list('percent'), label='seg_up')
    #fig3, = plt.plot(tst.get_seg1_down_list('percent'), label='seg1_down')
    #fig4, = plt.plot(tst.get_seg1_up_list('percent'), label='seg1_up')
    #fig5, = plt.plot(tst.get_seg2_down_list('percent'), label='seg2_down')
    #fig6, = plt.plot(tst.get_seg2_up_list('percent'), label='seg2_up')
    #fig7, = plt.plot(tst.get_seg3_down_list('percent'), label='seg3_down')
    #fig8, = plt.plot(tst.get_seg3_up_list('percent'), label='seg3_up')
    #plt.legend(handles=[fig1,fig2,fig3,fig4,fig5,fig6,fig7,fig8])

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
