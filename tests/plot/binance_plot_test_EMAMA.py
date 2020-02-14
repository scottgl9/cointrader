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
from trader.indicator.OBV import OBV
from trader.indicator.ehler.EMAMA import EMAMA
from trader.account.binance.AccountBinance import AccountBinance
from trader.account.binance.binance.client import Client
from trader.config import *


# kline format: [ time, low, high, open, close, volume ]
def plot_emas_product(plt, klines, product, hours=0):
    open_prices = []
    close_prices = []
    low_prices = []
    high_prices = []
    timestamps = []

    ema26_obv = EMA(26, scale=24)
    ema26_obv_values = []
    ema50_obv = EMA(50, scale=24)
    ema50_obv_values = []

    obv = OBV()
    obv_values = []

    emama = EMAMA()
    emama_x_values = []
    emama_values = []
    efama_values = []

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

        emama_value, efama_value = emama.update(close_price)
        if emama_value != 0:
            emama_values.append(emama_value)
            efama_values.append(efama_value)
            emama_x_values.append(i)

        obv_value = obv.update(close=close_price, volume=volume)
        obv_values.append(obv_value)

        ema26_obv_values.append(ema26_obv.update(obv_value))
        ema50_obv_values.append(ema50_obv.update(obv_value))

    xvalues = np.linspace(0, hours, num=len(close_prices))
    symprice, = plt.plot(close_prices, label=product) #, color='black')
    fig11, = plt.plot(emama_x_values,emama_values, label="EMAMA")
    fig12, = plt.plot(emama_x_values, efama_values, label="EFAMA")

    plt.legend(handles=[symprice, fig11, fig12])
    plt.subplot(212)
    fig1, = plt.plot(xvalues, obv_values, label="OBV")
    fig2, = plt.plot(xvalues, ema26_obv_values, label="OBVEMA26")
    fig3, = plt.plot(xvalues, ema50_obv_values, label="OBVEMA50")
    #fig3, = plt.plot(obv_values, label="OBP")
    plt.legend(handles=[fig1, fig2, fig3])

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
