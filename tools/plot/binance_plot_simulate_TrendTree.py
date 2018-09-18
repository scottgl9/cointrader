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
from datetime import datetime, timedelta
from pypika import Query, Table, Field, Order
from trader.strategy import *
from datetime import datetime, timedelta
import threading
import logging
import sys
from trader.WebHandler import WebThread
from trader.account.binance.client import Client
from trader.MultiTrader import MultiTrader
from trader.account.AccountBinance import AccountBinance
from trader.config import *
import numpy as np
import matplotlib.pyplot as plt
from trader.indicator.EMA import EMA
from trader.indicator.OBV import OBV
from trader.indicator.SLOPE import SLOPE
from trader.lib.TrendTree import TrendTreeProcessor


def get_rows_as_msgs(c):
    msgs = []
    for row in c:
        msg = {'E': row[0], 'c': row[1], 'h': row[2], 'l': row[3],
               'o': row[4], 'q': row[5], 's': row[6], 'v': row[7]}
        msgs.append(msg)
    return msgs


def simulate(conn, client, base, currency, type="channel"):
    logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
    logger = logging.getLogger()
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)
    logger.setLevel(logging.INFO)

    ticker_id = "{}{}".format(base, currency)
    c = conn.cursor()
    #c.execute("SELECT * FROM miniticker WHERE s='{}' ORDER BY E ASC".format(ticker_id))
    c.execute("SELECT E,c,h,l,o,q,s,v FROM miniticker WHERE s='{}'".format(ticker_id)) # ORDER BY E ASC")")

    ema12 = EMA(12, scale=24, lagging=True)
    ema26 = EMA(26, scale=24, lagging=True)
    ema50 = EMA(50, scale=24, lagging=True, lag_window=5)
    ema200 = EMA(200, scale=24, lagging=True, lag_window=5)
    obv_ema12 = EMA(12, scale=24) #EMA(12, scale=24, lagging=True)
    obv_ema26 = EMA(26, scale=24) #EMA(26, scale=24, lagging=True)
    obv_ema50 = EMA(50,scale=24) #EMA(50, scale=24, lagging=True, lag_window=5)
    obv_ema12_values = []
    obv_ema26_values = []
    obv_ema50_values = []

    slope = SLOPE(window=50)
    slope_values = []
    slope_ema = EMA(50, scale=24)

    ttp = TrendTreeProcessor(logger=logger)

    obv = OBV()
    quad_x_values = []
    quad_y_values = []
    ema12_values = []
    ema26_values = []
    ema50_values = []
    ema200_values = []
    close_prices = []
    open_prices = []
    low_prices = []
    diff_values = []
    signal_values = []
    high_prices = []
    timestamps = []

    macd_diff_values = []
    macd_signal_values = []

    i=0
    for msg in get_rows_as_msgs(c):
        close = float(msg['c'])
        low = float(msg['l'])
        high = float(msg['h'])
        open = float(msg['o'])
        volume = float(msg['v'])
        ts = int(msg['E'])

        ttp.update(price=close, ts=ts)

        if ttp.indicator.result != 0:
            macd_diff_values.append(ttp.indicator.result)

        obv_value = obv.update(close=close, volume=volume)
        obv_ema12_values.append(obv_ema12.update(obv_value))
        obv_ema26_values.append(obv_ema26.update(obv_value))
        obv_ema50_values.append(obv_ema50.update(obv_value))

        ema12_value = ema12.update(close)
        ema12_values.append(ema12_value)
        ema26_values.append(ema26.update(close))
        ema50_value = ema50.update(close)
        ema50_values.append(ema50_value)
        ema200_value = ema200.update(close)
        ema200_values.append(ema200_value)

        value = slope.update(ema26.result)
        slope_values.append(value)

        close_prices.append(close)
        open_prices.append(open)
        low_prices.append(low)
        high_prices.append(high)
        timestamps.append(ts)
        i += 1

    ttp.print_tree()

    plt.subplot(211)
    #fig = plt.figure()
    #ax = fig.add_subplot(2,1,1)

    for entry in ttp.tree_values:
        start_i = timestamps.index(entry[3])
        end_i = timestamps.index(entry[4])
        start_price = entry[1]
        end_price = entry[2]
        size_i = end_i - start_i
        size_price = end_price - start_price
        print(entry[0], entry[-1], start_i, end_i)
        if entry[-1] == 1:
            color="green"
        else:
            color="red"
        plt.gca().add_patch(plt.Rectangle([start_i, start_price], size_i, size_price, color=color, fill=False))


    symprice, = plt.plot(close_prices, label=ticker_id)
    fig1, = plt.plot(ema12_values, label='EMA12')
    fig2, = plt.plot(ema26_values, label='EMA26')
    fig3, = plt.plot(ema50_values, label='EMA50')
    fig4, = plt.plot(ema200_values, label='EMA200')
    plt.legend(handles=[symprice, fig1, fig2, fig3, fig4])
    plt.subplot(212)
    #fig21, = plt.plot(macd_diff_values, label='MACDDIFF')
    #fig22, = plt.plot(macd_signal_values, label='MACDSIG')
    #plt.legend(handles=[fig21, fig22])
    plt.plot(slope_values)
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
