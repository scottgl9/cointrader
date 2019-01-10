#!/usr/bin/python

import sys
import os
try:
    import trader
except ImportError:
    sys.path.append('.')
    import trader

import sqlite3
from datetime import datetime
import sys
import os
from trader.account.binance.client import Client
from trader.MarketManager import MarketManager
from trader.config import *
import matplotlib.pyplot as plt
import argparse
from trader.indicator.OBV import OBV
from trader.indicator.DTWMA import DTWMA
from trader.lib.Kline import Kline
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

    obv = OBV()
    obv_values = []
    close_prices = []
    high_prices = []
    low_prices = []
    volumes = []
    timestamps = []
    mm = MarketManager()

    closes_corrected = []
    dtwma = DTWMA(window=30)
    dtwma_values = []
    ema12 = EMA(12)
    ema26 = EMA(26)
    ema12_prices = []
    ema26_prices = []
    obv_ema12 = EMA(12)
    obv_ema26 = EMA(26)
    obv_ema12_prices = []
    obv_ema26_prices = []
    i=0
    for msg in get_rows_as_msgs(c):
        close = float(msg['c'])
        low = float(msg['l'])
        high = float(msg['h'])
        open = float(msg['o'])
        volume = float(msg['v'])
        ts = int(msg['E'])

        kline = Kline(symbol=msg['s'],
                      open=float(msg['o']),
                      close=float(msg['c']),
                      low=float(msg['l']),
                      high=float(msg['h']),
                      volume=float(msg['v']),
                      ts=int(msg['E']))

        mm.update(kline.symbol, kline)

        if mm.ready():
            for kline in mm.get_klines():
                ema12.update(kline.close)
                ema12_prices.append(ema12.result)
                ema26.update(kline.close)
                ema26_prices.append(ema26.result)
                closes_corrected.append(kline.close)
                high_prices.append(kline.high)
                low_prices.append(kline.low)
                obv.update(kline.close, kline.volume)
                obv_values.append(obv.result)
                obv_ema12.update(obv.result)
                obv_ema26.update(obv.result)
                obv_ema12_prices.append(obv_ema12.result)
                obv_ema26_prices.append(obv_ema26.result)
                volumes.append(volume)
            mm.reset()

        timestamps.append(ts)
        close_prices.append(close)
        #lstsqs_x_values.append(i)
        i += 1

    first_ts = datetime.utcfromtimestamp(int(timestamps[0])/1000)
    last_ts = datetime.utcfromtimestamp(int(timestamps[-1])/1000)
    total_time_hours = (last_ts - first_ts).total_seconds() / (60 * 60)
    print("hours={}".format(total_time_hours))

    plt.subplot(211)

    #symprice, = plt.plot(close_prices, label=ticker_id)
    plt.plot(closes_corrected)
    #plt.plot(low_prices)
    #plt.plot(high_prices)
    plt.plot(ema12_prices)
    plt.plot(ema26_prices)
    #fig2, = plt.plot(ema26_values, label='EMA26')
    #plt.legend(handles=[symprice])
    plt.subplot(212)
    #plt.legend(handles=[fig21, fig22, fig23])
    #plt.plot(volumes)
    plt.plot(obv_values)
    plt.plot(obv_ema12_prices)
    plt.plot(obv_ema26_prices)
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
