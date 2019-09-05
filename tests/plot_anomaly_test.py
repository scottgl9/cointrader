#!/usr/bin/env python3

# import pandas as pd
#import pandas.io.data as web
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
from trader.myhelpers import *
from trader.indicator.SMMA import SMMA
from trader.indicator.EMA import EMA
from trader.indicator.SMA import SMA

# kline format: [ time, low, high, open, close, volume ]

if __name__ == '__main__':
    ticker = 'BTC-USD'

    smma = EMA(12)
    smma2 = SMMA(12)
    sma0 = SMA(4)
    sma_prices = []
    volumes = []
    volumes_smma = []
    last_volume = 0.0
    prices = []
    klines = retrieve_klines_24hrs(ticker)
    for kline in klines:
        if last_volume != 0.0:
            volumes.append(float(kline[5]) - last_volume)#smma.update(float(kline[5])))
            volumes_smma.append(smma.update(float(kline[5]) - last_volume))
        prices.append(float(kline[3]))
        sma_prices.append(sma0.update(float(kline[3])))
        last_volume = float(kline[5])

    # find all prices for which all values before and after are less than price
    for i in range(1, len(sma_prices) - 1):
        if sma_prices[i-1] < sma_prices[i] and sma_prices[i+1] < sma_prices[i]:
            print("peak at {}: {}".format(i, sma_prices[i]))

    ema0 = compute_ema_dict_from_klines(klines, 4)
    average_volume = sum(volumes) / len(volumes)
    plt.figure(1)
    plt.subplot(211)
    plt.plot(prices)
    plt.plot(sma_prices)
    plt.plot(ema0["y"])
    plt.subplot(212)
    #plt.plot(volumes)
    plt.plot(volumes_smma)
    plt.axhline(average_volume)
    plt.show()