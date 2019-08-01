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
from trader.lib.RTKline import RTKline

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
    c.execute("SELECT E,c,h,l,o,q,s,v FROM miniticker WHERE s='{}'".format(ticker_id)) # ORDER BY E ASC")")

    ema12 = EMA(12)
    ema50 = EMA(50)
    ema12_values = []
    ema50_values = []
    close_prices = []
    open_prices = []
    low_prices = []
    high_prices = []
    volumes = []

    rtkline = RTKline()
    kline_close_prices = []
    kline_high_prices = []
    kline_low_prices = []
    kline_volumes = []
    kline_close_x_values = []

    i=0
    for msg in get_rows_as_msgs(c):
        ts = int(msg['E'])
        close = float(msg['c'])
        low = float(msg['l'])
        high = float(msg['h'])
        open = float(msg['o'])
        volume = float(msg['v'])
        volumes.append(volume)

        rtkline.update(close, ts, volume)
        if rtkline.ready():
            kline = rtkline.get_kline()
            ema12.update(kline.close)
            ema50.update(kline.close)
            ema12_values.append(ema12.result)
            ema50_values.append(ema50.result)
            kline_close_prices.append(kline.close)
            kline_low_prices.append(kline.low)
            kline_high_prices.append(kline.high)
            kline_volumes.append(kline.volume)
            kline_close_x_values.append(i)
        close_prices.append(close)
        open_prices.append(open)
        low_prices.append(low)
        high_prices.append(high)
        i += 1

    plt.subplot(211)
    symprice, = plt.plot(close_prices, label=ticker_id)

    fig1, = plt.plot(kline_close_x_values, kline_close_prices, label='kline_close')
    fig2, = plt.plot(kline_close_x_values, ema12_values, label='EMA12')
    fig3, = plt.plot(kline_close_x_values, ema50_values, label='EMA50')

    plt.legend(handles=[symprice, fig1, fig2, fig3])
    plt.subplot(212)
    fig21, = plt.plot(volumes, label='volume')
    #fig22, = plt.plot(kline_close_x_values, kline_volumes, label='volume_kline')
    plt.legend(handles=[fig21])
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
