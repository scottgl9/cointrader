#!/usr/bin/env python3

import sys
try:
    import trader
except ImportError:
    sys.path.append('.')
    import trader

import numpy as np
#from scipy import optimize
from datetime import datetime
import matplotlib.pyplot as plt
from trader.indicator.EMA import EMA
from trader.KlinesDB import KlinesDB
from trader.account.cbpro.cbpro import AuthenticatedClient
from trader.account.cbpro.AccountCoinbasePro import AccountCoinbasePro
from trader.indicator.OBV import OBV
from trader.config import *


def piecewise_linear(x, x0, x1, b, k1, k2, k3):
    condlist = [x < x0, (x >= x0) & (x < x1), x >= x1]
    funclist = [lambda x: k1*x + b, lambda x: k1*x + b + k2*(x-x0), lambda x: k1*x + b + k2*(x-x0) + k3*(x - x1)]
    return np.piecewise(x, condlist, funclist)

# kline format: [ time, low, high, open, close, volume ]
def plot_emas_product(plt, klines, product, hours=0):
    open_prices = []
    close_prices = []
    low_prices = []
    high_prices = []
    macd_signal = []
    timestamps = []
    ema12 = EMA(12, scale=24)
    ema12_prices = []
    ema26 = EMA(26, scale=24)
    ema26_prices = []
    ema50 = EMA(50, scale=24)

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

    #balances = accnt.get_account_balances()
    #print(balances)
    plt.figure(1)
    #plt.subplot(211)

    symprice, = plt.plot(close_prices, label=product) #, color='black')
    low, = plt.plot(low_prices, label="low")
    high, = plt.plot(high_prices, label="high")

    plt.legend(handles=[symprice, low, high])
    #plt.subplot(212)
    #plt.figure(2)
    #fig1, = plt.plot(xvalues, obv_values, label="OBV")
    #fig2, = plt.plot(xvalues, ema26_obv_values, label="OBVEMA26")
    #fig3, = plt.plot(xvalues, ema50_obv_values, label="OBVEMA50")
    #fig3, = plt.plot(obv_values, label="OBP")
    #plt.legend(handles=[fig1, fig2, fig3])
    #plt.plot(kst_values)
    #plt.plot(rsquare_values)
    return macd_signal

def abs_average(values):
    total = 0.0
    for value in values:
        total += abs(value)
    total = total / float(len(values))
    return total

if __name__ == '__main__':
    #print(client.get_user_trades())
    base = 'BTC'
    currency='USD'
    if len(sys.argv) == 3:
        base=sys.argv[1]
        currency = sys.argv[2]
    client = AuthenticatedClient(CBPRO_KEY, CBPRO_SECRET, CBPRO_PASS)
    accnt = AccountCoinbasePro(client=client, simulate=False)
    #klines = accnt.get_klines(hours=128, ticker_id="{}-{}".format(base, currency))
    symbol="{}-{}".format(base, currency)
    end_ts = int(datetime.now().timestamp())
    start_ts = end_ts - 3600 * 250
    klines = accnt.get_hourly_klines(symbol, start_ts, end_ts)
    diff_values = plot_emas_product(plt, klines, symbol, hours=250)
    plt.show()
