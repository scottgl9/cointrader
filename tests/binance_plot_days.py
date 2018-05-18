#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt
import numpy as np
from sklearn import datasets, linear_model
from trader.myhelpers import *
from sklearn.metrics import mean_squared_error, r2_score
from trader.indicator.BOX import BOX
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
from trader.indicator.OBV import OBV
from trader.SupportResistLevels import SupportResistLevels
from trader.indicator.IchimokuCloud import IchimokuCloud
from trader.indicator.PSAR import PSAR
import math
from trader.account.AccountBinance import AccountBinance
from trader.account.binance.client import Client
from trader.MeasureTrend import MeasureTrend
from trader.account.binance.exceptions import BinanceAPIException
from config import *
import sys

# kline format: [ time, low, high, open, close, volume ]

def plot_emas_product(plt, klines, product):
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
    ema12 = EMA(12)
    ema12_prices = []
    ema26 = EMA(26)
    ema26_prices = []
    ema_obv = EMA(26)
    ema_obv_values = []
    box=BOX()
    box_low_values = []
    box_high_values = []
    box_x_values = []
    obv = OBV()
    obv_values = []
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

        obv_value = obv.update(close=close_price, volume=volume)
        obv_values.append(obv_value)
        ema_obv_values.append(ema_obv.update(obv_value))

        macd.update(open_price)
        ema12_prices.append(ema12.update(close_price))
        ema26_prices.append(ema26.update(close_price))

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

        rsi_values.append(rsi.update(klines[i][4]))
        macd_signal.append(float(macd.diff))
        timestamps.append((float(klines[i][0]) - initial_time) / (60.0))

    prices = prices_from_kline_data(klines)
    symprice, = plt.plot(prices, label=product) #, color='black')
    ema4, = plt.plot(ema12_prices, label='EMA12')
    ema5, = plt.plot(ema26_prices, label='EMA26')

    #kama0, = plt.plot(kama_prices, label='KAMA')

    plt.legend(handles=[symprice, ema4, ema5])
    plt.subplot(212)
    fig1, = plt.plot(obv_values, label="OBV")
    fig2, = plt.plot(ema_obv_values, label="OBVEMA")
    plt.legend(handles=[fig1, fig2])#, fig2, fig3])
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

    ticker_id = "{}{}".format(base, currency)
    accnt = AccountBinance(client, base, currency)
    #balances = accnt.get_account_balances()
    #print(balances)
    plt.figure(1)
    plt.subplot(211)
    klines = client.get_historical_klines(ticker_id, Client.KLINE_INTERVAL_1DAY, "6 months ago")
    diff_values = plot_emas_product(plt, klines, accnt.ticker_id)
    plt.show()
