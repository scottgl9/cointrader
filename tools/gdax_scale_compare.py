#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt
from trader.myhelpers import *
from datetime import  datetime, date
import matplotlib
from trader.indicator.EMA import EMA
from trader.indicator.SMMA import SMMA
from trader.indicator.VWAP import VWAP
from trader.indicator.MACD import MACD
import math

# kline format: [ time, low, high, open, close, volume ]

def abs_average(values):
    total = 0.0
    for value in values:
        total += abs(value)
    total = total / float(len(values))
    return total

def get_scalar(data1, data2):
    return (max(data2) - min(data2)) / (max(data1) - min(data1))

def move_to_zero_and_scale(prices1, prices2):
    avg1 = abs_average(prices1)
    avg2 = abs_average(prices2)

    if avg2 > avg1:
        scalar = (max(prices2) - min(prices2)) / (max(prices1) - min(prices1))
        print(scalar)
        prices1 = scalar * (prices1 - avg1)
        prices2 = prices2 - avg2
    elif avg2 < avg1:
        scalar = (max(prices1) - min(prices1)) / (max(prices2) - min(prices2))
        print(scalar)
        prices1 = prices1 - avg2
        prices2 = scalar*(prices2 - avg2)
    return prices1, prices2

def plot_fibonacci_bands(plt, timestamps, prices1, prices2):
    #dates = matplotlib.dates.date2num(timestamps)
    line1, =plt.plot(prices1, label=ticker1)
    line2, =plt.plot(prices2, label=ticker2)
    #line3, = plt.plot(prices2 - prices1)

    #plt.gcf().autofmt_xdate()

    macd = MACD()
    #klines = retrieve_klines_last_hour('LTC-USD', hours=4)
    macd_data = []
    macd_signal = []
    macd_diff = []
    count = 0
    last_macd_diff = 0.0
    current_macd_diff = 0.0
    last_macd_det = 0.0
    macd_det = 0.0
    peak = last_peak = 0.0
    valley = last_valley = 0.0

    for price in prices1:
        macd.update(float(price))
        #macd.update()
        macd_data.append(macd.result)
        macd_signal.append(macd.signal.result)
        macd_diff.append(macd.diff)
        current_macd_diff = macd.diff

        last_macd_det = macd_det
        if (macd.diff - last_macd_diff) != 0.0:
            macd_det = macd.diff - last_macd_diff

        if macd.diff != 0.0:
            last_macd_diff = macd.diff

        if (last_macd_det < 0.0 and macd_det > 0.0):
            #if abs(last_macd_det) > 0.5 and abs(macd_det) > 0.5:
            if 1:
                print(macd_det, last_macd_det)
                if abs(last_macd_det) > abs(macd_det) and abs(last_macd_det) < 2*abs(macd_det):
                    last_valley = valley
                    valley = current_macd_diff
                    if last_valley != 0.0:
                        plt.axvline(x=count)
                        print("valley={} {}".format(valley, (abs(valley) - abs(last_valley)) / last_valley * 100.0))
                elif abs(last_macd_det) < abs(macd_det) and 2 * abs(last_macd_det) > abs(last_macd_det):
                    last_valley = valley
                    valley = current_macd_diff
                    if last_valley != 0.0:
                        plt.axvline(x=count)
                        print("valley={} {}".format(valley, (abs(valley) - abs(last_valley)) / last_valley * 100.0))
        elif (last_macd_det > 0.0 and macd_det < 0.0):
            print(macd_det, last_macd_det)
            #if (abs(last_macd_det) + abs(macd_det)) > 1.5:
            #if abs(last_macd_det) > 0.5 and abs(macd_det) > 0.5:
            if 1:
                print(macd_det, last_macd_det)
                if abs(macd_det) > 0.02 and abs(last_macd_det) > 0.02 and abs(last_macd_det) > abs(macd_det) and abs(last_macd_det) < 2 * abs(macd_det):
                    last_peak = peak
                    peak = current_macd_diff
                    if last_peak != 0.0:
                        #plt.axvline(x=count)
                        print("peak={} {}".format(peak, (abs(peak) - abs(last_peak)) / last_peak * 100.0))
                elif abs(macd_det) > 0.02 and abs(last_macd_det)> 0.02 and abs(last_macd_det) < abs(macd_det) and 2 * abs(last_macd_det) > abs(last_macd_det):
                    last_peak = peak
                    peak = current_macd_diff
                    if last_peak != 0.0:
                        #plt.axvline(x=count)
                        print("peak={} {}".format(peak, (peak - last_peak) / last_peak * 100.0))
        #if (last_macd_diff < 0.0 and macd.diff > 0.0):
        #    plt.axvline(x=count)
        #if (last_macd_diff > 0.0 and macd.diff < 0.0):
        #    plt.axvline(x=count)

        count += 1

    scalar = 1.0 #get_scalar(macd_diff, prices1)

    macdplot, = plt.plot(np.array(macd_diff) * scalar)
    plt.legend(handles=[line1, line2, macdplot])

    price_max_value = max(prices1)
    diff = price_max_value - min(prices1)
    level1 = price_max_value - 0.236 * diff
    level2 = price_max_value - 0.382 * diff
    level3 = price_max_value - 0.618 * diff

    #plt.axvline(x=100)

    plt.axhspan(level1, min(prices1), alpha=0.4, color='lightsalmon')
    plt.axhspan(level2, level1, alpha=0.5, color='lavender')
    plt.axhspan(level3, level2, alpha=0.5, color='palegreen')
    plt.axhspan(price_max_value, level3, alpha=0.5, color='powderblue')

def get_times_from_klines(klines):
    times = []
    initial = 0
    for kline in klines:
        if initial == 0: initial = int(kline[0])
        #times.append((int(kline[0]) - initial)/60)
        times.append(date.fromtimestamp(float(kline[0])))

    return times

if __name__ == '__main__':
    ticker1 = 'LTC-USD'
    ticker2 = 'BTC-USD'
    plt.figure(1)
    klines = retrieve_klines_last_hour(ticker1, hours=4)
    klines2 = retrieve_klines_last_hour(ticker2, hours=4)
    #klines = retrieve_klines_24hrs(ticker1)
    #klines2 = retrieve_klines_24hrs(ticker2)
    if len(klines) > len(klines2):
        klines2 = klines2[:len(klines)]
    elif len(klines) < len(klines2):
        diffsize = len(klines2) - len(klines)
        klines = klines2[len(klines2)]

    prices2 = np.array(prices_from_kline_data(klines2))
    prices1 = np.array(prices_from_kline_data(klines))

    prices1, prices2 = move_to_zero_and_scale(prices1, prices2)

    timestamps = get_times_from_klines(klines)
    if len(timestamps) > len(prices2):
        timestamps = timestamps[0:len(prices2)]
    else:
        klines = klines[:len(timestamps)]

    plot_fibonacci_bands(plt, timestamps, prices1, prices2)

    plt.show()
