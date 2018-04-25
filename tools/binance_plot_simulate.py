#!/usr/bin/python

import os.path
import time
import sys
import sqlite3
from datetime import datetime, timedelta
from pypika import Query, Table, Field, Order
from trader.strategy import *
from datetime import datetime, timedelta
import threading
import sys
from trader.WebHandler import WebThread
from trader.account.binance.client import Client
from trader.MultiTrader import MultiTrader
from trader.AccountBinance import AccountBinance
from config import *
import numpy as np
import matplotlib.pyplot as plt
from trader.SupportResistLevels import SupportResistLevels
from trader.indicator.IchimokuCloud import IchimokuCloud
from trader.indicator.EMA import EMA
from trader.indicator.MACD import MACD
from trader.indicator.PSAR import PSAR

def simulate(conn, client, base, currency):
    ticker_id = "{}{}".format(base, currency)
    c = conn.cursor()
    c.execute("SELECT * FROM miniticker WHERE s='{}' ORDER BY E ASC".format(ticker_id))

    cloud = IchimokuCloud()
    macd = MACD(12.0, 26.0, 9.0, scale=24.0)
    ema12 = EMA(12, scale=24, lagging=True)
    ema26 = EMA(26, scale=24, lagging=True)
    ema50 = EMA(50, scale=24, lagging=True, lag_window=5)
    ema12_values = []
    ema26_values = []
    ema50_values = []
    close_prices = []
    low_prices = []
    diff_values = []
    signal_values = []
    high_prices = []
    Senkou_SpanA_values = []
    Senkou_SpanB_values = []
    span_x_values = []
    sar = PSAR()
    sar_values = []
    sar_x_values = []

    i=0
    for row in c:
        msg = {'E': row[0], 'c': row[1], 'h': row[2], 'l': row[3],
               'o': row[4], 'q': row[5], 's': row[6], 'v': row[7]}
        close = float(msg['c'])
        low = float(msg['l'])
        high = float(msg['h'])
        sar_value = sar.update(close=close, low=low, high=high)
        if sar.bull:
            sar_x_values.append(i)
            sar_values.append(sar_value)

        ema12_values.append(ema12.update(close))
        ema26_values.append(ema26.update(close))
        ema50_values.append(ema50.update(close))
        macd.update(close)
        diff_values.append(macd.result)
        signal_values.append(macd.signal.result)
        SpanA, SpanB = cloud.update(close=close, low=low, high=high)
        if SpanA != 0 and SpanB != 0:
            Senkou_SpanA_values.append(SpanA)
            Senkou_SpanB_values.append(SpanB)
            #close_last_values.append(close_last_window)
            span_x_values.append(i)

        close_prices.append(close)
        low_prices.append(low)
        high_prices.append(high)
        i += 1
    plt.subplot(211)
    symprice, = plt.plot(close_prices, label=ticker_id)
    #lowprice, = plt.plot(low_prices, label=ticker_id)
    #highprice, = plt.plot(high_prices, label=ticker_id)
    #SpanA, = plt.plot(Senkou_SpanA_values, label="SpanA")
    #SpanB, = plt.plot(Senkou_SpanB_values, label="SpanB")
    print(sar_values)
    ema0, = plt.plot(ema12_values, label='EMA12')
    ema1, = plt.plot(ema26_values, label='EMA26')
    ema2, = plt.plot(ema50_values, label='EMA50')
    sar0, = plt.plot(sar_x_values, sar_values, label='PSAR')
    plt.legend(handles=[symprice, ema0, ema1, ema2, sar0])
    plt.subplot(212)
    plt.plot(diff_values)
    #plt.plot(signal_values)
    plt.show()

if __name__ == '__main__':
    client = Client(MY_API_KEY, MY_API_SECRET)
    conn = sqlite3.connect('cryptocurrency_database.miniticker_collection_04092018.db')

    base = 'BTC'
    currency='USDT'
    if len(sys.argv) == 3:
        base=sys.argv[1]
        currency = sys.argv[2]

    simulate(conn, client, base, currency)
    conn.close()
