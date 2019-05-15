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
from trader.account.binance.client import Client
from trader.config import *
import matplotlib.pyplot as plt
import argparse
from trader.indicator.OBV import OBV
from trader.indicator.EMA import EMA
from trader.lib.AccelEMA import AccelEMA


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

    obv = OBV()
    emaroc12 = AccelEMA(12, scale=24, percent=False)
    emaroc26 = AccelEMA(26, scale=24, percent=False)
    emaroc200 = AccelEMA(200, scale=24, percent=False)
    ema12 = EMA(12, scale=24)
    ema26 = EMA(26, scale=24)
    ema200 = EMA(200, scale=24)
    obv_ema12 = EMA(12, scale=24) #EMA(12, scale=24)
    obv_ema26 = EMA(26, scale=24) #EMA(26, scale=24)
    obv_ema50 = EMA(50,scale=24) #EMA(50, scale=24, lag_window=5)
    obv_ema12_values = []
    obv_ema26_values = []
    obv_ema50_values = []
    emaroc12_values = []
    emaroc26_values = []
    emaroc200_values = []
    ema12_values = []
    ema26_values = []
    ema200_values = []
    close_prices = []
    open_prices = []
    low_prices = []
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

        obv_value = obv.update(close=close, volume=volume)
        obv_ema12_values.append(obv_ema12.update(obv_value))
        obv_ema26_values.append(obv_ema26.update(obv_value))
        obv_ema50_values.append(obv_ema50.update(obv_value))

        ema12_value = ema12.update(close)
        ema12_values.append(ema12_value)
        ema26_values.append(ema26.update(close))
        ema200.update(close)
        ema200_values.append(ema200.result)

        emaroc12.update(close, ts)
        emaroc26.update(close, ts)
        emaroc200.update(close, ts)

        emaroc12_values.append(emaroc12.result)
        emaroc26_values.append(emaroc26.result)
        emaroc200_values.append(emaroc200.result)
        close_prices.append(close)
        open_prices.append(open)
        low_prices.append(low)
        high_prices.append(high)
        i += 1

    plt.subplot(211)
    symprice, = plt.plot(close_prices, label=ticker_id)
    fig1, = plt.plot(ema12_values, label='EMA12')
    fig2, = plt.plot(ema26_values, label='EMA26')
    fig3, = plt.plot(ema200_values, label='EMA200')
    plt.legend(handles=[symprice, fig1, fig2, fig3])
    plt.subplot(212)
    fig21, = plt.plot(emaroc12_values, label='VEMA12')
    fig22, = plt.plot(emaroc26_values, label='VEMA26')
    fig23, = plt.plot(emaroc200_values, label='VEMA200')
    plt.legend(handles=[fig21, fig22, fig23])
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
