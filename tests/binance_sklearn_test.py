#!/usr/bin/python

import numpy as np
from sklearn import tree
import matplotlib.pyplot as plt
from trader.indicator.EMA import EMA
from trader.indicator.OBV import OBV
from trader.account.AccountBinance import AccountBinance
from trader.account.binance.client import Client
from config import *
import sys

# kline format: [ time, low, high, open, close, volume ]

def plot_emas_product(plt, klines, product):
    ema_obv = EMA(26)
    ema_obv_values = []
    obv = OBV()
    obv_values = []

    for i in range(1, len(klines) - 1):
        low = float(klines[i][1])
        high = float(klines[i][2])
        open_price = float(klines[i][3])
        close_price = float(klines[i][4])
        volume = float(klines[i][5])

        obv_value = obv.update(close=close_price, volume=volume)
        obv_values.append(obv_value)
        ema_obv_values.append(ema_obv.update(obv_value))


# trading algorithm
def algo(t, h, l, v, acc=10):
    features = []
    labels = []

    for i in range(len(t) - acc):

        temp_t = t[acc + i - 1]
        temp_h = h[acc + i - 1]
        temp_l = l[acc + i - 1]
        temp_v = v[acc + i - 1]

        features.append([temp_t, temp_h, temp_l, temp_v])

        # 1 means price went up
        if t[acc + i] > t[acc + i - 1]:
            labels.append([1])
        else:
            labels.append([0])

    clf = tree.DecisionTreeClassifier()
    clf.fit(features, labels)
    temp_list = []

    for i in range(acc):
        temp_list.append([])
        temp_list[i].append(t[-1 * (acc - i)])
        temp_list[i].append(h[-1 * (acc - i)])
        temp_list[i].append(l[-1 * (acc - i)])
        temp_list[i].append(v[-1 * (acc - i)])

    if clf.predict(temp_list)[0] == 1:
        return 1
    else:
        return 0


def algo_test(plt, klines):
    obv = OBV()
    obv_values = []
    lows = []
    highs = []
    opens = []
    closes = []
    volumes = []
    timestamps = []
    acc = 100
    decision = 0

    for i in range(1, len(klines) - 1):
        ts = float(klines[i][0])
        low = float(klines[i][1])
        high = float(klines[i][2])
        open = float(klines[i][3])
        close = float(klines[i][4])
        volume = float(klines[i][5])

        obv_value = obv.update(close=close, volume=volume)
        obv_values.append(obv_value)

        timestamps.append(ts)
        lows.append(low)
        highs.append(high)
        opens.append(open)
        closes.append(close)
        volumes.append(volume)

    count = len(klines)
    pos = 0

    while pos < count:
        if pos > acc:
            decision = algo(closes[:pos], highs[:pos], lows[:pos], obv_values[:pos], acc=acc)
            if decision == 1:
                print("bought at {}".format(closes[pos]))
            elif decision == 0:
                print("sold at {}".format(closes[pos]))
        pos += 1

if __name__ == '__main__':
    client = Client(MY_API_KEY, MY_API_SECRET)
    base = 'BTC'
    currency='USDT'
    if len(sys.argv) == 3:
        base=sys.argv[1]
        currency = sys.argv[2]
    accnt = AccountBinance(client, base, currency)
    #plt.figure(1)
    #plt.subplot(211)
    klines = accnt.get_klines(hours=72)
    algo_test(plt, klines)
    #diff_values = plot_emas_product(plt, klines, accnt.ticker_id)
    #plt.show()
