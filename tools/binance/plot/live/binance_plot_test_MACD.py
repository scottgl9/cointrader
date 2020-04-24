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
from trader.indicator.MACD import MACD
from trader.indicator.MINMAX import MINMAX
from trader.indicator.OBV import OBV
from trader.indicator.test.PriceChannel import PriceChannel
from trader.account.binance.AccountBinance import AccountBinance
from trader.account.binance.binance.client import Client
from trader.config import *


# kline format: [ time, low, high, open, close, volume ]
def plot_emas_product(plt, klines, product, hours=0):
    open_prices = []
    close_prices = []
    low_prices = []
    high_prices = []
    macd = MACD(12.0, 26.0, 9.0, scale=24.0, plot_mode=True)
    macd_diff_values = []
    macd_signal_values = []
    timestamps = []
    minmax = MINMAX(50)
    pc = PriceChannel()
    pc_values = []
    ema_volume = EMA(12)
    ema_volume_values = []
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
    min_values = []
    max_values = []

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

        minimum, maximum = minmax.update(close_price)
        min_values.append(minimum)
        max_values.append(maximum)

        obv_value = obv.update(close=close_price, volume=volume)
        obv_values.append(obv_value)

        ema26_obv_values.append(ema26_obv.update(obv_value))
        ema50_obv_values.append(ema50_obv.update(obv_value))

        macd.update(open_price)
        if macd.result != 0 and macd.result_signal != 0:
            macd_diff_values.append(macd.result)
            macd_signal_values.append(macd.result_signal)

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
    macd_xvalues = np.linspace(0, hours, num=len(macd_diff_values))
    fig1, = plt.plot(macd_xvalues, macd_diff_values, label="MACD DIFF")
    fig2, = plt.plot(macd_xvalues, macd_signal_values, label="MACD SIG")
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
    diff_values = plot_emas_product(plt, klines, accnt.ticker_id, hours=128)
    plt.show()
