#!/usr/bin/env python3

import sys
try:
    import trader
except ImportError:
    sys.path.append('.')
    import trader

import numpy as np
#from scipy import optimize
import matplotlib.pyplot as plt
from trader.indicator.EMA import EMA
from trader.indicator.RSI import RSI
from trader.indicator.OBV import OBV
from trader.account.binance.AccountBinance import AccountBinance
from trader.account.binance.binance.client import Client
from trader.config import *


# kline format: [ time, low, high, open, close, volume ]
def plot_emas_product(plt, klines, product, hours=0):
    open_prices = []
    close_prices = []
    low_prices = []
    high_prices = []
    rsi = RSI()
    rsi_values = []
    timestamps = []
    ema12 = EMA(12, scale=24)
    ema12_prices = []
    ema26 = EMA(26, scale=24)
    ema26_prices = []
    ema50 = EMA(50, scale=24)
    ema50_prices = []

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

        obv_value = obv.update(close=close_price, volume=volume)
        obv_values.append(obv_value)

        ema26_obv_values.append(ema26_obv.update(obv_value))
        ema50_obv_values.append(ema50_obv.update(obv_value))

        rsi.update(close_price)
        if rsi.result != 0:
            rsi_values.append(rsi.result)

        ema12_price = ema12.update(close_price)
        ema12_prices.append(ema12_price)
        ema26_prices.append(ema26.update(close_price))
        ema50_prices.append(ema50.update(close_price))


    xvalues = np.linspace(0, hours, num=len(close_prices))
    symprice, = plt.plot(xvalues, close_prices, label=product) #, color='black')
    fig11, = plt.plot(xvalues, ema12_prices, label='EMA12')
    fig12, = plt.plot(xvalues, ema26_prices, label='EMA26')

    #plt.legend(handles=[symprice, ema4, ema5, ema6])
    plt.subplot(212)
    rsi_xvalues = np.linspace(0, hours, num=len(rsi_values))
    fig1, = plt.plot(rsi_xvalues, rsi_values, label="RSI")
    plt.legend(handles=[fig1])

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
    klines = accnt.get_klines(hours=24)
    diff_values = plot_emas_product(plt, klines, accnt.ticker_id, hours=128)
    plt.show()
