#!/usr/bin/python

import numpy as np
from scipy import optimize
import matplotlib.pyplot as plt
from sklearn import datasets, linear_model
from trader.myhelpers import *
from sklearn.metrics import mean_squared_error, r2_score
from trader.indicator.test.BOX import BOX
from trader.indicator.EMA import EMA
from trader.indicator.SMMA import SMMA
from trader.indicator.VWAP import VWAP
from trader.indicator.MACD import MACD
from trader.indicator.MINMAX import MINMAX
from trader.indicator.KST import KST
from trader.indicator.QUAD import QUAD
from trader.indicator.QUAD2 import QUAD2
from trader.indicator.RSI import RSI
from trader.indicator.REMA import REMA
from trader.indicator.RSQUARE import RSQUARE
from trader.indicator.TSI import TSI
from trader.indicator.test.SVI import SVI
from trader.indicator.KAMA import KAMA
from trader.indicator.OBV import OBV
from trader.indicator.LinReg import LinReg
from trader.indicator.test.PriceChannel import PriceChannel
from trader.SupportResistLevels import SupportResistLevels
from trader.indicator.IchimokuCloud import IchimokuCloud
from trader.indicator.PSAR import PSAR
from trader.lib.Crossover2 import Crossover2
from trader.lib.CrossoverDouble import CrossoverDouble
import math
from trader.account.AccountBinance import AccountBinance
from trader.account.binance.client import Client
from trader.MeasureTrend import MeasureTrend
from trader.account.binance.exceptions import BinanceAPIException
from config import *
import sys

def piecewise_linear(x, x0, x1, b, k1, k2, k3):
    condlist = [x < x0, (x >= x0) & (x < x1), x >= x1]
    funclist = [lambda x: k1*x + b, lambda x: k1*x + b + k2*(x-x0), lambda x: k1*x + b + k2*(x-x0) + k3*(x - x1)]
    return np.piecewise(x, condlist, funclist)

# kline format: [ time, low, high, open, close, volume ]

def plot_emas_product(plt, klines, product):
    open_prices = []
    close_prices = []
    low_prices = []
    high_prices = []
    macd = MACD(12.0*24.0, 26.0*24.0, 9.0*24.0)
    rsi = RSI()
    rsi_values = []
    macd_signal = []
    timestamps = []
    minmax = MINMAX(50)
    pc = PriceChannel()
    pc_values = []
    prices = prices_from_kline_data(klines)
    ema_volume = EMA(12)
    kst = KST()
    kst_values = []
    kama = KAMA()
    kama_prices = []
    ema_volume_values = []
    price_x_values = []
    ema12 = EMA(12, scale=24)
    ema12_prices = []
    ema26 = EMA(26, scale=24)
    ema26_prices = []
    ema50 = EMA(50, scale=24)
    ema50_prices = []
    # this creates a very quadratic looking curve
    rema12 = REMA(12)#, scale=24)
    rema12_prices = []
    quad2 = QUAD2()
    quad2_values = []
    double_cross = CrossoverDouble(window=10)
    cross_short = Crossover2(window=10)
    cross_long = Crossover2(window=10)
    rsquare = RSQUARE()
    rsquare_values = []

    ema26_obv = EMA(26, scale=24)
    ema26_obv_values = []
    ema50_obv = EMA(50, scale=24)
    ema50_obv_values = []

    obv = OBV()
    obv_values = []
    min_values = []
    max_values = []


    for i in range(1, len(klines) - 1):
        low = float(klines[i][1])
        high = float(klines[i][2])
        open_price = float(klines[i][3])
        close_price = float(klines[i][4])
        volume = float(klines[i][5])

        open_prices.append(open_price)
        close_prices.append(close_price)
        low_prices.append(low)
        high_prices.append(high)

        minimum, maximum = minmax.update(close_price)
        min_values.append(minimum)
        max_values.append(maximum)

        kst_values.append(kst.update(close_price))

        obv_value = obv.update(close=close_price, volume=volume)
        obv_values.append(obv_value)
        #obp_value = obp.update(price=close_price)
        #obp_values.append(obp_value)
        ema26_obv_values.append(ema26_obv.update(obv_value))
        ema50_obv_values.append(ema50_obv.update(obv_value))

        #rep_value = rep.update(close_price)
        #if rep_value != 0:
        #    rep_values.append(rep_value)

        #SpanA, SpanB = cloud.update(close=close_price, low=low, high=high)
        #if SpanA != 0 and SpanB != 0:
        #    Senkou_SpanA_values.append(SpanA)
        #    Senkou_SpanB_values.append(SpanB)
        #    #close_last_values.append(close_last_window)
        #    span_x_values.append(i)

        #sar_value = sar.update(close=close_price, low=low, high=high)
        #sar_x_values.append(i)
        #sar_values.append(sar_value)

        #prev_low, prev_high, low_low, high_high = levels.update(close_price, low, high)
        #if prev_low != 0 and prev_high != 0:
        #    prev_low_values.append(prev_low)
        #    prev_high_values.append(prev_high)
        #    low_low_values.append(low_low)
        #    high_high_values.append(high_high)
        #    prev_x_values.append(i)

        macd.update(open_price)
        ema12_price = ema12.update(close_price)
        ema12_prices.append(ema12_price)
        rema12_prices.append(rema12.update(close_price))
        ema26_prices.append(ema26.update(close_price))
        ema50_prices.append(ema50.update(close_price))
        kama_prices.append(kama.update(close_price))

        #result = zigzag.update_from_kline(open_price, low, high)
        #if result != 0.0:
        #    zigzag_y.append(result)
        #    zigzag_x.append(i)

        #result = zigzag.update_from_kline(close_price, low, high)
        #if result != 0.0:
        #    zigzag_y.append(result)
        #    zigzag_x.append(i)

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
        last_close = close_price

    #result = pc.get_values()
    #if len(result) != 0:
    #    print(result)
    #    pc_values = np.append(pc_values, result)

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


    #pc_values = pc.get_values()

    #for i in range(0, len(ema12_prices)):
    #    #cross_short.update(ema12_prices[i], ema26_prices[i])
    #    double_cross.update(ema12_prices[i], ema26_prices[i], ema50_prices[i])
    #    if double_cross.crossup_detected():
    #        plt.axvline(x=i, color='green')
    #    elif double_cross.crossdown_detected():
    #        plt.axvline(x=i, color='red')
    #prices = prices_from_kline_data(klines)
    low_lines = []
    high_lines = []
    for i in range(0, len(close_prices)):
        close = close_prices[i]
        pc.update(close)
        price_x_values.append(i)
        if pc.split_up():
            plt.axvline(x=i, color='green')
        elif pc.split_down():
            plt.axvline(x=i, color='red')

    for result in pc.get_values():
        center = result[0]
        low_line = result[1]
        high_line = result[2]
        pc_values = np.append(pc_values, center)
        low_lines = np.append(low_lines, low_line)
        high_lines = np.append(high_lines, high_line)

    symprice, = plt.plot(close_prices, label=product) #, color='black')
    #ema4, = plt.plot(ema12_prices, label='EMA12')
    #ema5, = plt.plot(ema26_prices, label='EMA26')
    #ema6, = plt.plot(ema50_prices, label='EMA50')
    #ema7, = plt.plot(rema12_prices, label='REMA12')
    #plt.plot(min_values)
    #plt.plot(max_values)
    plt.plot(pc_values)
    plt.plot(low_lines)
    plt.plot(high_lines)
    #p, e = optimize.curve_fit(piecewise_linear, price_x_values, close_prices)
    #plt.plot(price_x_values, piecewise_linear(price_x_values, *p))
    #plt.plot(pc_values)
    #plt.plot([0, pc.total_age], [pc.start_low, pc.cur_low])
    #plt.plot([0, pc.total_age], [pc.start_high, pc.cur_high])
    #plt.legend(handles=[symprice, ema4, ema5, ema6])
    plt.subplot(212)
    fig1, = plt.plot(obv_values, label="OBV")
    fig2, = plt.plot(ema26_obv_values, label="OBVEMA26")
    fig3, = plt.plot(ema50_obv_values, label="OBVEMA50")
    #fig3, = plt.plot(obv_values, label="OBP")
    plt.legend(handles=[fig1, fig2, fig3])
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
