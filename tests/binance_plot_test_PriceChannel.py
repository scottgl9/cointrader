#!/usr/bin/python

import sys
try:
    import trader
except ImportError:
    sys.path.append('.')

import numpy as np
import matplotlib.pyplot as plt
from trader.indicator.EMA import EMA
from trader.indicator.OBV import OBV
from trader.indicator.test.PriceChannel import PriceChannel
from trader.account.AccountBinance import AccountBinance
from trader.account.binance.client import Client
from trader.account.binance.exceptions import BinanceAPIException
import datetime as dt
from trader.config import *

# kline format: [ time, low, high, open, close, volume ]
def plot_emas_product(plt, klines, product, hours=0):
    open_prices = []
    close_prices = []
    low_prices = []
    high_prices = []
    timestamps = []
    pc = PriceChannel()
    pc_values = []
    price_x_values = []
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

        ema12_price = ema12.update(close_price)
        ema12_prices.append(ema12_price)
        ema26_prices.append(ema26.update(close_price))
        ema50_prices.append(ema50.update(close_price))

        last_close = close_price

    low_lines = []
    high_lines = []
    for i in range(0, len(close_prices)):
        close = close_prices[i]
        pc.update(close)
        price_x_values.append(i)
        #if pc.split_up():
        #    plt.axvline(x=i, color='green')
        #elif pc.split_down():
        #    plt.axvline(x=i, color='red')

    for result in pc.get_values():
        center = result[0]
        low_line = result[1]
        high_line = result[2]
        pc_values = np.append(pc_values, center)
        low_lines = np.append(low_lines, low_line)
        high_lines = np.append(high_lines, high_line)

    xvalues = np.linspace(0, hours, num=len(close_prices))
    fig11, = plt.plot(xvalues, close_prices, label=product) #, color='black')
    fig12, = plt.plot(xvalues, ema12_prices, label='EMA12')
    fig13, = plt.plot(xvalues, ema26_prices, label='EMA26')
    plt.legend(handles=[fig11, fig12, fig13])

    # scale from count to hours, then plot
    plt.plot(np.linspace(0, hours, num=len(low_lines)), low_lines)
    plt.plot(np.linspace(0, hours, num=len(high_lines)), high_lines)
    #plt.legend(handles=[symprice, ema4, ema5, ema6])
    plt.subplot(212)
    fig21, = plt.plot(xvalues, obv_values, label="OBV")
    fig22, = plt.plot(xvalues, ema26_obv_values, label="OBVEMA26")
    fig23, = plt.plot(xvalues, ema50_obv_values, label="OBVEMA50")
    #fig3, = plt.plot(obv_values, label="OBP")
    plt.legend(handles=[fig21, fig22, fig23])
    #plt.plot(kst_values)
    #plt.plot(rsquare_values)


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
