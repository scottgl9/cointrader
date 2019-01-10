#!/usr/bin/python

import sys
import os
try:
    import trader
except ImportError:
    sys.path.append('.')
    import trader

import sqlite3
import sys
import os
from trader.account.binance.client import Client
from trader.config import *
import matplotlib.pyplot as plt
import argparse
from trader.indicator.OBV import OBV
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

    obv_ema12 = DZLEMA(12, scale=24) #EMA(12, scale=24)
    obv_ema26 = DZLEMA(26, scale=24) #EMA(26, scale=24)
    obv_ema50 = DZLEMA(50,scale=24) #EMA(50, scale=24, lag_window=5)
    obv_ema12_values = []
    obv_ema26_values = []
    obv_ema50_values = []

    ema10 = DZLEMA(10, scale=24)
    ema10_values = []
    ema30 = DZLEMA(30, scale=24)
    ema30_values = []
    ema50 = DZLEMA(50, scale=24)
    ema50_values = []

    obv = OBV()
    obv_values = []
    close_prices = []
    open_prices = []
    low_prices = []
    high_prices = []
    volumes = []

    dtwma = DTWMA(window=30)
    dtwma_values = []
    dtwma2 = DTWMA(window=30)

    i=0
    for msg in get_rows_as_msgs(c):
        close = float(msg['c'])
        low = float(msg['l'])
        high = float(msg['h'])
        open = float(msg['o'])
        volume = float(msg['v'])
        ts = int(msg['E'])

        volumes.append(volume)

        dtwma.update(close, ts)
        dtwma_values.append(dtwma.result)

        dtwma2.update(volume, ts)

        obv_value = obv.update(close=dtwma.result, volume=dtwma2.result)
        obv_values.append(obv_value)
        obv_ema12_values.append(obv_ema12.update(obv_value))
        obv_ema26_values.append(obv_ema26.update(obv_value))
        obv_ema50_values.append(obv_ema50.update(obv_value))

        ema10.update(close)
        ema10_values.append(ema10.result)
        ema30.update(close)
        ema30_values.append(ema30.result)
        ema50.update(close)
        ema50_values.append(ema50.result)

        close_prices.append(close)
        open_prices.append(open)
        low_prices.append(low)
        high_prices.append(high)
        #lstsqs_x_values.append(i)
        i += 1

    #plt.subplot(211)
    fig = plt.figure()
    ax = fig.add_subplot(2,1,1)

    symprice, = plt.plot(close_prices, label=ticker_id)
    #fig1, = plt.plot(dtwma_values, label='DTWMA')
    fig1, = plt.plot(ema10_values, label="EMA10")
    fig2, = plt.plot(ema50_values, label='EMA50')
    fig3, = plt.plot(ema30_values, label='EMA30')
    plt.legend(handles=[symprice, fig1, fig2, fig3])
    plt.subplot(212)
    fig21, = plt.plot(obv_ema12_values, label='OBV12')
    #fig22, = plt.plot(obv_ema26_values, label='OBV26')
    fig23, = plt.plot(obv_ema50_values, label='OBV50')
    plt.legend(handles=[fig21, fig23])
    #plt.plot(obv_values)
    #plt.plot(signal_values)
    #plt.plot(tsi_values)
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
