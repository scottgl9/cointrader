#!/usr/bin/python

import sys
try:
    import trader
except ImportError:
    sys.path.append('.')
    import trader

import sqlite3
import sys
from trader.account.binance.client import Client
from trader.config import *
import matplotlib.pyplot as plt
from trader.lib.Angle import Angle
from trader.lib.MAAvg import MAAvg
from trader.indicator.DTWMA import DTWMA
from trader.indicator.ZLEMA import *


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
    ema50 = EMA(100, scale=24, lag_window=5)
    ema200 = EMA(200, scale=24, lag_window=5)

    maavg = MAAvg()
    maavg.add(ema12)
    maavg.add(ema26)
    maavg.add(ema50)

    dtwma = DTWMA(window=30)
    angle = Angle(seconds=3600)
    angle_values = []
    ema12_values = []
    ema26_values = []
    ema50_values = []
    ema200_values = []
    maavg_values = []
    detrend_values = []
    detrend_x_values = []
    close_prices = []
    open_prices = []
    low_prices = []
    diff_values = []
    signal_values = []
    high_prices = []
    volumes = []

    i=0
    for msg in get_rows_as_msgs(c):
        close = float(msg['c'])
        low = float(msg['l'])
        high = float(msg['h'])
        open = float(msg['o'])
        volume = float(msg['v'])
        ts = int(msg['E'])
        volumes.append(volume)

        ema12.update(close)
        ema26.update(close)
        ema50.update(close)
        ema200.update(close)
        maavg.update()
        maavg_values.append(maavg.result)
        ema12_values.append(ema12.result)
        ema26_values.append(ema26.result)
        ema200_values.append(ema200.result)

        if maavg.result != 0 and ema200.result != 0:
            angle.update(value1=maavg.result, value2=ema200.result, ts=ts)

        if angle.result != 0:
            angle_values.append(angle.result)

        result = angle.detrend_result()
        if result != 0:
            detrend_values.append(result)
            detrend_x_values.append(i)

        close_prices.append(close)
        open_prices.append(open)
        low_prices.append(low)
        high_prices.append(high)
        #lstsqs_x_values.append(i)
        i += 1

    plt.subplot(211)
    #symprice, = plt.plot(close_prices, label=ticker_id)
    fig1, = plt.plot(maavg_values, label='MAAVG')
    fig4, = plt.plot(ema200_values, label='EMA200')
    plt.legend(handles=[fig1])
    plt.subplot(212)
    fig21, = plt.plot(angle_values, label='ANGLE')
    #fig22, = plt.plot(slope2_values, label='SLOPE26')

    #plt.plot(bb_low_values)
    plt.legend(handles=[fig21])
    #plt.plot(signal_values)
    #plt.plot(tsi_values)
    plt.show()

if __name__ == '__main__':
    client = None

    base = 'BTC'
    currency='USDT'
    filename = 'cryptocurrency_database.miniticker_collection_04092018.db'
    if len(sys.argv) == 4:
        base=sys.argv[1]
        currency = sys.argv[2]
        filename = sys.argv[3]
    if len(sys.argv) == 3:
        base=sys.argv[1]
        currency = sys.argv[2]

    print("Loading {}".format(filename))
    conn = sqlite3.connect(filename)

    simulate(conn, client, base, currency, type="MACD")
    conn.close()
