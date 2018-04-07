#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt
import numpy as np
from sklearn import datasets, linear_model
from trader.myhelpers import *
from sklearn.metrics import mean_squared_error, r2_score
from trader.indicator.EMA import EMA
from trader.indicator.SMMA import SMMA
from trader.indicator.VWAP import VWAP
from trader.indicator.MACD import MACD
from trader.indicator.QUAD import QUAD
from trader.indicator.RSI import RSI
from trader.indicator.TSI import TSI
from trader.indicator.DiffWindow import DiffWindow
from trader.indicator.ZigZag import ZigZag
import math
from trader.AccountBinance import AccountBinance
from trader.account.binance.client import Client
from trader.MeasureTrend import MeasureTrend
from trader.account.binance.exceptions import BinanceAPIException
from config import *
import sys

# kline format: [ time, low, high, open, close, volume ]

def plot_emas_product(plt, klines, product):
    #klines = retrieve_klines_last_hour(product, hours=4)
    #klines = retrieve_klines_24hrs(product)
    #vwap = VWAP(60)
    #vwaps = []
    macd = MACD(12.0*24.0, 26.0*24.0, 9.0*24.0)
    rsi = RSI()
    rsi_values = []
    macd_signal = []
    price_min = []
    price_max = []
    timestamps = []
    prices = prices_from_kline_data(klines)
    quad_maxes = []
    quad_x = []
    quad_x2 = []
    quad_y = []
    price_min.append(float(klines[0][1]))
    price_max.append(float(klines[0][2]))
    quad = QUAD()
    quad2 = QUAD()
    ema_quad = EMA(26)
    ema_quad2 = EMA(26)
    ema12 = EMA(12)
    ema12_prices = []
    trend = MeasureTrend()
    trend_tsi = MeasureTrend(window=20, detect_width=8, use_ema=False)
    tsi = TSI()
    tsi_values = []
    zigzag_x = []
    zigzag_y = []
    zigzag = ZigZag()

    diffwindow = DiffWindow(30)
    last_diff_result = 0

    initial_time = float(klines[0][0])
    c_gt_price = False
    timestamps = []
    peaks = []
    valleys = []
    for i in range(1, len(klines) - 1):
        trend.update_price(float(klines[i][3]))
        macd.update(float(klines[i][3]))
        ema12_prices.append(ema12.update(float(klines[i][3])))

        result = zigzag.update(float(klines[i][3]))
        if result != 0.0:
            zigzag_y.append(result)
            zigzag_x.append(i)

        tsi_value = tsi.update(float(klines[i][3]))
        trend_tsi.update_price(tsi_value)
        tsi_values.append(tsi_value)
        if trend_tsi.valley_detected() and trend_tsi.valley_value() < -10.0:
            print("valley {}, {}".format(i, trend_tsi.valley_value()))
            #valleys.append(i)
            #plt.axhline(y=trend.valley_value(), color='red')
        if trend_tsi.peak_detected() and trend_tsi.peak_value() > 10.0:
            print("peak {}, {}".format(i, trend_tsi.peak_value()))
            #peaks.append(i)
            #plt.axhline(y=trend.peak_value(), color='blue')
        rsi_values.append(rsi.update(klines[i][4]))
        macd_signal.append(float(macd.diff))
        timestamps.append((float(klines[i][0]) - initial_time) / (60.0))

    print(zigzag_y)

    for i in range(0, len(macd_signal)):
        quad.update(macd_signal[i], timestamps[i])#ema_quad.update(klines[i][3]), ts)
        ts = timestamps[i]
        A, B, C = quad.compute()

        if C > 0.0: # and C > min(prices) and C < max(prices):
            quad_x.append(ts)
            y = A * (ts * ts) + (B * ts) + C
            quad_y.append(y)
            quad_maxes.append(C)
            #print(i, y, A, B, C)

    ema26_prices = compute_ema_dict_from_klines(klines, 26)
    #ema12_prices = compute_ema_dict_from_klines(klines, 12)

    prices = prices_from_kline_data(klines)
    symprice, = plt.plot(prices, label=product) #, color='black')
    ema4, = plt.plot(ema26_prices["y"], label='EMA26')
    ema5, = plt.plot(ema12_prices, label='EMA12')
    plt.plot(zigzag_x, zigzag_y)
    #plt.plot(vwaps)
    #quad0, = plt.plot(quad_x, quad_y, label='QUAD')
    #plt.plot(quad_x2, quad_maxes)
    plt.legend(handles=[symprice, ema4, ema5])
    plt.subplot(212)
    #print(rsi_values)
    fig1, = plt.plot(tsi_values, label="TSI")
    #fig1, = plt.plot(rsi_values, label="RSI") #macd_signal, label='MACD')
    #fig2, = plt.plot(quad_x, quad_y, label='QUAD')
    #fig3, = plt.plot(quad_x, quad_maxes, label='QUAD_MAX')
    plt.legend(handles=[fig1])#, fig2, fig3])
    return macd_signal

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
    diff_values = plot_emas_product(plt, klines, accnt.ticker_id)
    plt.show()
