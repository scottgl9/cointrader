#!/usr/bin/python

import sys
try:
    import tools.trader
except ImportError:
    sys.path.append('.')
import os.path
import time
import sqlite3
from datetime import datetime, timedelta
from pypika import Query, Table, Field, Order
from tools.trader.strategy import *
from datetime import datetime, timedelta
import threading
import sys
from tools.trader.WebHandler import WebThread
from tools.trader.account.binance.client import Client
from tools.trader.MultiTrader import MultiTrader
from tools.trader.account.AccountBinance import AccountBinance
from tools.trader.config import *
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from tools.trader.indicator.IchimokuCloud import IchimokuCloud
from tools.trader.indicator.EMA import EMA
from tools.trader.indicator.LinReg import LinReg
from tools.trader.indicator.OBV import OBV
from tools.trader.indicator.MACD import MACD
from tools.trader.lib.FakeKline import FakeKline
from tools.trader.signal.TD_Sequential_Signal import TD_Sequential_Signal
from tools.trader.lib.PeakValleyDetect import PeakValleyDetect
from tools.trader.lib.PriceFilter import PriceFilter
from tools.trader.indicator.TSI import TSI
from tools.trader.indicator.test.PriceChannel import PriceChannel
from tools.trader.lib.Crossover2 import Crossover2
from tools.trader.indicator.WMA import WMA
from scipy import optimize

def simulate(conn, client, base, currency, type="channel"):
    ticker_id = "{}{}".format(base, currency)
    c = conn.cursor()
    #c.execute("SELECT * FROM miniticker WHERE s='{}' ORDER BY E ASC".format(ticker_id))
    c.execute("SELECT E,c,h,l,o,q,s,v FROM miniticker WHERE s='{}'".format(ticker_id)) # ORDER BY E ASC")")

    ema12 = EMA(12, scale=24, lagging=True)
    ema26 = EMA(26, scale=24, lagging=True)
    ema50 = EMA(50, scale=24, lagging=True, lag_window=5)
    obv_ema12 = EMA(12, scale=24) #EMA(12, scale=24, lagging=True)
    obv_ema26 = EMA(26, scale=24) #EMA(26, scale=24, lagging=True)
    obv_ema50 = EMA(50,scale=24) #EMA(50, scale=24, lagging=True, lag_window=5)
    fkline = FakeKline()
    obv_ema12_values = []
    obv_ema26_values = []
    obv_ema50_values = []
    filter = PriceFilter(window=20, range_filter=False)
    filter_values =[]
    filter_x_values = []

    macd = MACD(12.0, 26.0, 9.0, scale=24.0)
    macd_cross = Crossover2(window=10, cutoff=0.0)
    macd_zero_cross = Crossover2(window=10, cutoff=0.0)
    macd_signal = EMA(9, scale=24.0)
    macd_diff_values = []
    macd_signal_values = []

    pc = PriceChannel()
    pc_values = []
    price_x_values = []

    obv = OBV()
    quad_x_values = []
    quad_y_values = []
    ema12_values = []
    ema26_values = []
    ema50_values = []
    close_prices = []
    open_prices = []
    low_prices = []
    diff_values = []
    signal_values = []
    high_prices = []
    volumes = []

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

        volumes.append(volume)

        obv_value = obv.update(close=close, volume=volume)
        obv_ema12_values.append(obv_ema12.update(obv_value))
        obv_ema26_values.append(obv_ema26.update(obv_value))
        obv_ema50_values.append(obv_ema50.update(obv_value))

        ema12_value = ema12.update(close)
        ema12_values.append(ema12_value)
        ema26_values.append(ema26.update(close))
        ema50_value = ema50.update(close)
        ema50_values.append(ema50_value)


        macd.update(close)
        #if macd.result_signal == 0:
        #    print(i)
        if macd.diff != 0:
            value = macd_signal.update(macd.diff)
            macd_diff_values.append(macd.diff)
            macd_signal_values.append(value)

        value = filter.update(close)
        if value != 0:
            filter_values.append(value)
            filter_x_values.append(i)

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

    bought = False
    bought_price = 0
    macd_prices = close_prices[len(close_prices)-len(macd_diff_values):]
    for i in range(0, len(macd_diff_values)):
        macd_zero_cross.update(macd_diff_values[i], 0)
        macd_cross.update(macd_diff_values[i], macd_signal_values[i])
        if macd_zero_cross.crossup_detected():
            if not bought:
                plt.axvline(x=i, color='green')
                bought = True
                bought_price = macd_prices[i]
        elif macd_zero_cross.crossdown_detected():
            if bought and (bought_price * 1.01) < macd_prices[i]:
                plt.axvline(x=i, color='red')
                bought = False
                bought_price = 0
        if macd_cross.crossup_detected():
            if not bought:
                plt.axvline(x=i, color='green')
                bought = True
                bought_price = macd_prices[i]
        elif macd_cross.crossdown_detected():
            if bought and (bought_price * 1.01) < macd_prices[i]:
                plt.axvline(x=i, color='red')
                bought = False
                bought_price = 0

    #plt.plot(filter_x_values, filter_values)
    #plt.plot(low_prices)
    #plt.plot(high_prices)
    #plt.plot(lstsqs_x_values, support1_values)
    #plt.plot(lstsqs_x_values, support2_values)
    #fig1, = plt.plot(ema12_values, label='EMA12')
    #fig2, = plt.plot(ema26_values, label='EMA26')
    #fig3, = plt.plot(ema50_values, label='EMA50')
    plt.legend(handles=[symprice])
    plt.subplot(212)
    plt.plot(macd_diff_values)
    plt.plot(macd_signal_values)

    #plt.plot(signal_values)
    #plt.plot(tsi_values)
    plt.show()

if __name__ == '__main__':
    client = Client(MY_API_KEY, MY_API_SECRET)
    #conn = sqlite3.connect('cryptocurrency_database.ticker_collection_04282018.db') #'cryptocurrency_database.miniticker_collection_04092018.db')
    conn = sqlite3.connect('cryptocurrency_database.miniticker_collection_04032018.db')

    base = 'BTC'
    currency='USDT'
    if len(sys.argv) == 3:
        base=sys.argv[1]
        currency = sys.argv[2]

    simulate(conn, client, base, currency, type="MACD")
    conn.close()
