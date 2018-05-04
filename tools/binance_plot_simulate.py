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
from trader.indicator.QUAD import QUAD
from trader.indicator.BOX import BOX
from scipy import optimize

def simulate(conn, client, base, currency):
    ticker_id = "{}{}".format(base, currency)
    c = conn.cursor()
    #c.execute("SELECT * FROM miniticker WHERE s='{}' ORDER BY E ASC".format(ticker_id))
    c.execute("SELECT E,c,a,b,o,q,s,v FROM ticker WHERE s='{}'".format(ticker_id)) # ORDER BY E ASC")")

    cloud = IchimokuCloud()
    macd = MACD(12.0, 26.0, 9.0, scale=24.0)
    ema12 = EMA(12, scale=24, lagging=True)
    ema26 = EMA(26, scale=24, lagging=True)
    ema50 = EMA(50, scale=24, lagging=True, lag_window=5)
    quad = QUAD()
    quad_x_values = []
    quad_y_values = []
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
    pp_values = []
    support1_values = []
    support2_values = []
    resistance1_values = []
    box = BOX()
    box_lows = []
    box_highs = []

    lstsqs_x_values = []
    lstsqs_y_values = []

    i=0
    for row in c:
        msg = {'E': row[0], 'c': row[1], 'h': row[2], 'l': row[3],
               'o': row[4], 'q': row[5], 's': row[6], 'v': row[7]}
        close = float(msg['c'])
        low = float(msg['l'])
        high = float(msg['h'])
        open = float(msg['o'])
        #sar_value = sar.update(close=close, low=low, high=high)
        #if sar.bull:
        #    sar_x_values.append(i)
        #    sar_values.append(sar_value)

        box_low, box_high = box.update(close)
        if box_low != 0 and box_high != 0:
            box_lows.append(box_low)
            box_highs.append(box_high)

        ema12_values.append(ema12.update(close))
        ema26_values.append(ema26.update(close))
        ema50_value = ema50.update(close)
        ema50_values.append(ema50_value)
        #pp_value = (high + low + open)/3.0
        #support1 = (pp_value * 2.0) - high
        #support2 = pp_value - (high - low)
        #resistance1 = (pp_value * 2.0) - low
        #support1_values.append(support1)
        #support2_values.append(support2)
        #resistance1_values.append(resistance1)
        #pp_values.append(pp_value)

        #result = quad.update(ema50_value)
        #if result != 0:
        #    quad_y_values.append(quad.C)
        #macd.update(close)
        #diff_values.append(macd.result)
        #signal_values.append(macd.signal.result)
        #SpanA, SpanB = cloud.update(close=close, low=low, high=high)
        #if SpanA != 0 and SpanB != 0:
        #    Senkou_SpanA_values.append(SpanA)
        #    Senkou_SpanB_values.append(SpanB)
        #    span_x_values.append(i)

        close_prices.append(close)
        low_prices.append(low)
        high_prices.append(high)
        lstsqs_x_values.append(i)
        i += 1

    #lstsqs = np.poly1d(np.polyfit(np.array(lstsqs_x_values), np.array(close_prices), 5))
    #for x in lstsqs_x_values:
    #    lstsqs_y_values.append(lstsqs(x))

    plt.subplot(211)
    symprice, = plt.plot(close_prices, label=ticker_id)
    #lowprice, = plt.plot(low_prices, label=ticker_id)
    #highprice, = plt.plot(high_prices, label=ticker_id)
    #SpanA, = plt.plot(Senkou_SpanA_values, label="SpanA")
    #SpanB, = plt.plot(Senkou_SpanB_values, label="SpanB")
    #ema0, = plt.plot(ema12_values, label='EMA12')
    ema1, = plt.plot(ema26_values, label='EMA26')
    ema2, = plt.plot(ema50_values, label='EMA50')
    plt.plot(box_lows)
    plt.plot(box_highs)
    #plt.plot(support1_values)
    #plt.plot(support2_values)
    #plt.plot(resistance1_values)
    #quad0, = plt.plot(quad_y_values, label='QUAD')
    #plt.plot(lstsqs_x_values, lstsqs_y_values)
    #sar0, = plt.plot(sar_x_values, sar_values, label='PSAR')
    plt.legend(handles=[symprice, ema1, ema2])
    plt.subplot(212)
    plt.plot(diff_values)
    #plt.plot(signal_values)
    plt.show()

if __name__ == '__main__':
    client = Client(MY_API_KEY, MY_API_SECRET)
    conn = sqlite3.connect('cryptocurrency_database.ticker_collection_04282018.db') #'cryptocurrency_database.miniticker_collection_04092018.db')

    base = 'BTC'
    currency='USDT'
    if len(sys.argv) == 3:
        base=sys.argv[1]
        currency = sys.argv[2]

    simulate(conn, client, base, currency)
    conn.close()
