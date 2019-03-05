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
from trader.lib.MovingTimeSegment.MTSMoveRate import MTSMoveRate
from trader.indicator.EMA import EMA
from trader.lib.TrendState.TrendStateTrack import TrendStateTrack
from trader.lib.TrendState.TrendStateInfo import TrendStateInfo


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

    ema12 = EMA(12, scale=24)
    ema26 = EMA(26, scale=24)
    ema50 = EMA(100, scale=24)
    ema200 = EMA(200, scale=24)

    tst = TrendStateTrack(smoother=EMA(12, scale=24))

    mts_moverate = MTSMoveRate(small_seg_seconds=180, large_seg_seconds=900)
    mts_moverate_values = []

    ema12_values = []
    ema26_values = []
    ema50_values = []
    ema200_values = []
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

        ema12_value = ema12.update(close)
        ema12_values.append(ema12_value)
        ema26_values.append(ema26.update(close))
        ema50_value = ema50.update(close)
        ema50_values.append(ema50_value)
        ema200_value = ema200.update(close)
        ema200_values.append(ema200_value)

        tst.update(close=close, ts=ts)
        if tst.get_trend_string() != last_trend_string:
            state_indices.append((i, tst.get_trend_direction()))
            print("LONG:" + tst.get_trend_string())
            last_trend_string = tst.get_trend_string()

        mts_moverate.update(close, ts)
        mts_moverate_values.append(mts_moverate.result)
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
    fig1, = plt.plot(ema12_values, label='EMA12')
    fig2, = plt.plot(ema26_values, label='EMA26')
    fig3, = plt.plot(ema50_values, label='EMA50')
    fig4, = plt.plot(ema200_values, label='EMA200')
    plt.legend(handles=[symprice, fig1, fig2, fig3, fig4])
    plt.subplot(212)

    fig1, = plt.plot(tst._seg_down_list, label='seg_down')
    fig2, = plt.plot(tst._seg_up_list, label='seg_up')
    fig3, = plt.plot(tst._seg1_down_list, label='seg1_down')
    fig4, = plt.plot(tst._seg1_up_list, label='seg1_up')
    fig5, = plt.plot(tst._seg2_down_list, label='seg2_down')
    fig6, = plt.plot(tst._seg2_up_list, label='seg2_up')
    fig7, = plt.plot(tst._seg3_down_list, label='seg3_down')
    fig8, = plt.plot(tst._seg3_up_list, label='seg3_up')
    plt.legend(handles=[fig1,fig2,fig3,fig4,fig5,fig6,fig7,fig8])

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
