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
from trader.indicator.KAMA import KAMA
from trader.SupportResistLevels import SupportResistLevels
from trader.indicator.IchimokuCloud import IchimokuCloud
from trader.indicator.PSAR import PSAR
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
    timestamps = []
    prices = prices_from_kline_data(klines)
    quad_maxes = []
    quad_x = []
    quad_x2 = []
    quad_y = []
    quad = QUAD()
    quad2 = QUAD()
    ema_quad = EMA(26)
    ema_quad2 = EMA(26)
    ema_volume = EMA(12)
    kama = KAMA()
    kama_prices = []
    ema_volume_values = []
    ema12 = EMA(12)
    ema12_prices = []
    ema26 = EMA(26)
    ema26_prices = []
    trend = MeasureTrend()
    trend_tsi = MeasureTrend(window=20, detect_width=8, use_ema=False)
    sar = PSAR()

    levels = SupportResistLevels()
    cloud = IchimokuCloud()
    prev_low_values = []
    prev_high_values = []
    low_low_values = []
    high_high_values = []
    prev_x_values = []
    Senkou_SpanA_values = []
    Senkou_SpanB_values = []
    close_last_values = []
    span_x_values = []

    tsi = TSI()
    tsi_values = []
    zigzag_x = []
    zigzag_y = []
    zigzag = ZigZag(cutoff=0.2)
    volume_amount = 0.0
    last_volume_amount = 0.0

    price_channel_lows = []
    price_channel_highs = []
    pclow_ema = EMA(26)
    pchigh_ema = EMA(26)

    diffwindow = DiffWindow(30)
    last_diff_result = 0

    initial_time = float(klines[0][0])
    c_gt_price = False
    timestamps = []
    peaks = []
    valleys = []
    sar_x_values = []
    sar_values = []

    for i in range(1, len(klines) - 1):
        low = float(klines[i][1])
        high = float(klines[i][2])
        open_price = float(klines[i][3])
        close_price = float(klines[i][4])
        volume = float(klines[i][5])

        SpanA, SpanB = cloud.update(close=close_price, low=low, high=high)
        if SpanA != 0 and SpanB != 0:
            Senkou_SpanA_values.append(SpanA)
            Senkou_SpanB_values.append(SpanB)
            #close_last_values.append(close_last_window)
            span_x_values.append(i)

        sar_value = sar.update(close=close_price, low=low, high=high)
        sar_x_values.append(i)
        sar_values.append(sar_value)

        prev_low, prev_high, low_low, high_high = levels.update(close_price, low, high)
        if prev_low != 0 and prev_high != 0:
            prev_low_values.append(prev_low)
            prev_high_values.append(prev_high)
            low_low_values.append(low_low)
            high_high_values.append(high_high)
            prev_x_values.append(i)

        volume_amount = ema_volume.update(volume)
        ema_volume_values.append(volume_amount)

        last_volume_amount = volume_amount
        trend.update_price(open_price)
        macd.update(open_price)
        ema12_prices.append(ema12.update(close_price))
        ema26_prices.append(ema26.update(close_price))
        kama_prices.append(kama.update(close_price))

        result = zigzag.update_from_kline(open_price, low, high)
        if result != 0.0:
            zigzag_y.append(result)
            zigzag_x.append(i)

        result = zigzag.update_from_kline(close_price, low, high)
        if result != 0.0:
            zigzag_y.append(result)
            zigzag_x.append(i)

        tsi_value = tsi.update(close_price)
        trend_tsi.update_price(tsi_value)
        tsi_values.append(tsi_value)
        #if trend_tsi.valley_detected() and trend_tsi.valley_value() < -10.0:
        #    print("valley {}, {}".format(i, trend_tsi.valley_value()))
        #    #valleys.append(i)
        #    #plt.axhline(y=trend.valley_value(), color='red')
        #if trend_tsi.peak_detected() and trend_tsi.peak_value() > 10.0:
        #    print("peak {}, {}".format(i, trend_tsi.peak_value()))
        #    #peaks.append(i)
        #    #plt.axhline(y=trend.peak_value(), color='blue')
        rsi_values.append(rsi.update(klines[i][4]))
        macd_signal.append(float(macd.diff))
        timestamps.append((float(klines[i][0]) - initial_time) / (60.0))

    #print(prev_low_values)

    #for i in range(0, len(macd_signal)):
    #    quad.update(macd_signal[i], timestamps[i])#ema_quad.update(klines[i][3]), ts)
    #    ts = timestamps[i]
    #    A, B, C = quad.compute()
    #    if C > 0.0: # and C > min(prices) and C < max(prices):
    #        quad_x.append(ts)
    #        y = A * (ts * ts) + (B * ts) + C
    #        quad_y.append(y)
    #        quad_maxes.append(C)
    #        #print(i, y, A, B, C)

    prices = prices_from_kline_data(klines)
    symprice, = plt.plot(prices, label=product) #, color='black')
    #ema4, = plt.plot(ema26_prices["y"], label='EMA26')
    #lowlevel0, = plt.plot(prev_x_values, prev_low_values, label='LOWS')
    #lowlevel1, = plt.plot(prev_x_values, low_low_values, label='LLOWS')
    #highlevel0, = plt.plot(prev_x_values, prev_high_values, label='HIGHS')
    #highlevel1, = plt.plot(prev_x_values, high_high_values, label='HHIGHS')
    #SpanA, = plt.plot(span_x_values, Senkou_SpanA_values, label="SpanA")
    #SpanB, = plt.plot(span_x_values, Senkou_SpanB_values, label="SpanB")
    #sar0, = plt.plot(sar_x_values, sar_values, label='PSAR')
    #closePlot, = plt.plot(span_x_values, close_last_values, label="Close")
    ema5, = plt.plot(ema26_prices, label='EMA26')
    #kama0, = plt.plot(kama_prices, label='KAMA')

    plt.legend(handles=[symprice, ema5])
    plt.subplot(212)
    fig1, = plt.plot(rsi_values, label="RSI")
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
    klines = accnt.get_klines(hours=72)
    diff_values = plot_emas_product(plt, klines, accnt.ticker_id)
    plt.show()
