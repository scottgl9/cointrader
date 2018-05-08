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
from trader.account.AccountBinance import AccountBinance
from config import *
import numpy as np
import matplotlib.pyplot as plt
from trader.SupportResistLevels import SupportResistLevels
from trader.indicator.IchimokuCloud import IchimokuCloud
from trader.indicator.EMA import EMA
from trader.indicator.LinReg import LinReg
from trader.indicator.TESTMA import TESTMA
from trader.indicator.OBV import OBV
from trader.indicator.HMA import HMA
from trader.indicator.RMA import RMA
from trader.indicator.MACD import MACD
from trader.indicator.PSAR import PSAR
from trader.indicator.QUAD import QUAD
from trader.indicator.BOX import BOX
from trader.indicator.ZLEMA import *
from trader.indicator.WMA import WMA
from scipy import optimize

def simulate(conn, client, base, currency):
    ticker_id = "{}{}".format(base, currency)
    c = conn.cursor()
    #c.execute("SELECT * FROM miniticker WHERE s='{}' ORDER BY E ASC".format(ticker_id))
    c.execute("SELECT E,c,h,l,o,q,s,v FROM miniticker WHERE s='{}'".format(ticker_id)) # ORDER BY E ASC")")

    cloud = IchimokuCloud()
    macd = MACD(12.0, 26.0, 9.0, scale=24.0)
    ema12 = EMA(12, scale=24, lagging=True)
    ema26 = EMA(26, scale=24, lagging=True)
    ema50 = EMA(50, scale=24, lagging=True, lag_window=5)
    hma = HMA(window=26)
    obv_ema12 = DZLEMA(12, scale=24) #EMA(12, scale=24, lagging=True)
    obv_ema26 = DZLEMA(26, scale=24) #EMA(26, scale=24, lagging=True)
    obv_ema50 = DZLEMA(50,scale=24) #EMA(50, scale=24, lagging=True, lag_window=5)
    obv_ema12_values = []
    obv_ema26_values = []
    obv_ema50_values = []
    testma = TESTMA(segment=30, window=500)
    testma_values = []
    testma_x_values = []
    zlema = ZLEMA(window=50, scale=24)
    zlema2 = ZLEMA(window=50, scale=24)
    zlema_values = []

    quad = QUAD()
    obv = OBV()
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
    line = LinReg()
    line2 = LinReg()
    line_values = []
    line_x_values = []
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
        volume = float(msg['v'])
        #sar_value = sar.update(close=close, low=low, high=high)
        #if sar.bull:
        #    sar_x_values.append(i)
        #    sar_values.append(sar_value)

        box_low, box_high = box.update(close)
        if box_low != 0 and box_high != 0:
            box_lows.append(box_low)
            box_highs.append(box_high)

        obv_value = obv.update(close=close, volume=volume)
        obv_ema12_values.append(obv_ema12.update(obv_value))
        obv_ema26_values.append(obv_ema26.update(obv_value))
        obv_ema50_values.append(obv_ema50.update(obv_value))

        ema12_value = ema12.update(close)
        ema12_values.append(ema12_value)
        ema26_values.append(ema26.update(close))
        ema50_value = ema50.update(close)
        ema50_values.append(ema50_value)

        values = testma.update(close)
        if len(values) != 0:
            for value in values:
                testma_values.append(value)
                testma_x_values.append(i)

        zlema_values.append(zlema2.update(zlema.update(close)))

        #line_value = line.update(ema12_value)
        #if line_value != 0:
        #    line_values.append(line_value)
        #    line_x_values.append(i)
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
    ema0, = plt.plot(ema12_values, label='EMA12')
    plt.plot(testma_x_values, testma_values)
    #ema1, = plt.plot(ema26_values, label='EMA26')
    ema2, = plt.plot(ema50_values, label='EMA50')
    #plt.plot(box_lows)
    #plt.plot(box_highs)
    #plt.plot(line_x_values, line_values)
    #plt.plot(support1_values)
    #plt.plot(support2_values)
    #plt.plot(resistance1_values)
    #quad0, = plt.plot(quad_y_values, label='QUAD')
    #plt.plot(lstsqs_x_values, lstsqs_y_values)
    #sar0, = plt.plot(sar_x_values, sar_values, label='PSAR')
    plt.legend(handles=[symprice, ema0, ema2])
    plt.subplot(212)
    plt.plot(obv_ema12_values)
    plt.plot(obv_ema26_values)
    plt.plot(obv_ema50_values)
    #plt.plot(signal_values)
    plt.show()

if __name__ == '__main__':
    client = Client(MY_API_KEY, MY_API_SECRET)
    #conn = sqlite3.connect('cryptocurrency_database.ticker_collection_04282018.db') #'cryptocurrency_database.miniticker_collection_04092018.db')
    conn = sqlite3.connect('cryptocurrency_database.miniticker_collection_04092018.db')

    base = 'BTC'
    currency='USDT'
    if len(sys.argv) == 3:
        base=sys.argv[1]
        currency = sys.argv[2]

    simulate(conn, client, base, currency)
    conn.close()
