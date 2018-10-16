#!/usr/bin/python

import sys
try:
    import trader
except ImportError:
    sys.path.append('.')
    import trader

import os.path
import time
import sqlite3
from datetime import datetime
from pypika import Query, Table, Field, Order
from trader.strategy import *
import threading
import sys
from trader.WebHandler import WebThread
from trader.account.binance.client import Client
from trader.MarketManager import MarketManager
from trader.config import *
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from trader.indicator.OBV import OBV
from trader.indicator.test.DTWMA import DTWMA
from trader.lib.FakeKline import FakeKline
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
    volumes = []
    timestamps = []
    mm = MarketManager()

    closes_corrected = []
    dtwma = DTWMA(window=30)
    dtwma_values = []

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
                closes_corrected.append(kline.close)
                obv.update(kline.close, kline.volume)
                obv_values.append(obv.result)
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
    #fig2, = plt.plot(ema26_values, label='EMA26')
    #plt.legend(handles=[symprice])
    plt.subplot(212)
    #plt.legend(handles=[fig21, fig22, fig23])
    #plt.plot(volumes)
    plt.plot(obv_values)
    plt.show()

if __name__ == '__main__':
    client = Client(MY_API_KEY, MY_API_SECRET)

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
