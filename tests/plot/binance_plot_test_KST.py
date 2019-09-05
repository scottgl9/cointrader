#!/usr/bin/env python3

import sys
try:
    import trader
except ImportError:
    sys.path.append('.')
    import trader

import numpy as np
import matplotlib.pyplot as plt
from trader.myhelpers import *
from trader.indicator.EMA import EMA
from trader.indicator.OBV import OBV
from trader.indicator.KST import KST
from trader.account.AccountBinance import AccountBinance
from trader.account.binance.client import Client
from trader.account.binance.exceptions import BinanceAPIException
import datetime as dt
from trader.config import *

def piecewise_linear(x, x0, x1, b, k1, k2, k3):
    condlist = [x < x0, (x >= x0) & (x < x1), x >= x1]
    funclist = [lambda x: k1*x + b, lambda x: k1*x + b + k2*(x-x0), lambda x: k1*x + b + k2*(x-x0) + k3*(x - x1)]
    return np.piecewise(x, condlist, funclist)

def get_x_values(hours, values):
    return np.linspace(0, hours, num=len(values))

# kline format: [ time, low, high, open, close, volume ]
def plot_emas_product(plt, klines, product, hours=0):
    open_prices = []
    close_prices = []
    low_prices = []
    high_prices = []
    timestamps = []
    price_x_values = []
    kst = KST(use_ema=True, scale=24)
    kst_values = []
    kst_signal_values = []
    ema12 = EMA(12, scale=24)
    ema12_prices = []
    ema26 = EMA(26, scale=24)
    ema26_prices = []

    ema26_obv = EMA(26, scale=24)
    ema26_obv_values = []
    ema50_obv = EMA(50, scale=24)
    ema50_obv_values = []

    obv = OBV()
    obv_values = []

    for i in range(1, len(klines) - 1):
        ts = float(klines[i][0])
        low = float(klines[i][1])
        high = float(klines[i][2])
        open_price = float(klines[i][3])
        close_price = float(klines[i][4])
        volume = float(klines[i][5])

        open_prices.append(open_price)
        close_prices.append(close_price)
        low_prices.append(low)
        high_prices.append(high)
        timestamps.append(ts)

        kst.update(close_price)
        if kst.result != 0:
            kst_values.append(kst.result)
        if kst.signal_result != 0:
            kst_signal_values.append(kst.signal_result)

        obv_value = obv.update(close=close_price, volume=volume)
        obv_values.append(obv_value)

        ema26_obv_values.append(ema26_obv.update(obv_value))
        ema50_obv_values.append(ema50_obv.update(obv_value))

        ema12_price = ema12.update(close_price)
        ema12_prices.append(ema12_price)
        ema26_prices.append(ema26.update(close_price))

        last_close = close_price

    xvalues = get_x_values(hours, close_prices)
    symprice, = plt.plot(xvalues, close_prices, label=product) #, color='black')
    ema4, = plt.plot(xvalues, ema12_prices, label='EMA12')
    ema5, = plt.plot(xvalues, ema26_prices, label='EMA26')

    #plt.legend(handles=[symprice, ema4, ema5, ema6])
    plt.subplot(212)
    #fig1, = plt.plot(xvalues, obv_values, label="OBV")
    #fig2, = plt.plot(xvalues, ema26_obv_values, label="OBVEMA26")
    #fig3, = plt.plot(xvalues, ema50_obv_values, label="OBVEMA50")
    #print(pmo_values)
    #print(pmo_signal_values)
    fig1, = plt.plot(get_x_values(hours,kst_values), kst_values, label="KST")
    fig2, = plt.plot(get_x_values(hours,kst_signal_values), kst_signal_values, label="KST_SIG")

    plt.legend(handles=[fig1, fig2])

def abs_average(values):
    total = 0.0
    for value in values:
        total += abs(value)
    total = total / float(len(values))
    return total

if __name__ == '__main__':
    client = Client(MY_API_KEY, MY_API_SECRET)
    #print(client.get_user_trades())
    base = 'BTC'
    currency='USDT'
    if len(sys.argv) == 3:
        base=sys.argv[1]
        currency = sys.argv[2]
    accnt = AccountBinance(client, base, currency)
    #balances = accnt.get_account_balances()
    #print(balances)
    plt.figure(1)
    plt.subplot(211)
    klines = accnt.get_klines(hours=128)
    plot_emas_product(plt, klines, accnt.ticker_id, hours=128)
    plt.show()
