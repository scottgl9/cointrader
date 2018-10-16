#!/usr/bin/python

import matplotlib.pyplot as plt
import numpy as np
from sklearn import linear_model
from trader.myhelpers import *
from trader.indicator.EMA import EMA
from trader.indicator.VWAP import VWAP
from trader.indicator.MACD import MACD
from trader.indicator.test.QUAD import QUAD
from trader.indicator.DiffWindow import DiffWindow
from trader.MeasureTrend import MeasureTrend


# kline format: [ time, low, high, open, close, volume ]

def plot_emas_product(plt, klines, product):
    #klines = retrieve_klines_last_hour(product, hours=4)
    #klines = retrieve_klines_24hrs(product)
    vwap = VWAP(60)
    vwaps = []
    #macd = MACD()
    #macd_signal = []
    #for kline in klines:
    #    macd.update(float(kline[3]))
    #    #macd.update()
    #    macd_signal.append(float(macd.signal.result))
    price_min = []
    price_max = []
    timestamps = []
    prices = prices_from_kline_data(klines)
    quad_maxes = []
    quad_x = []
    quad_y = []
    price_min.append(float(klines[0][1]))
    price_max.append(float(klines[0][2]))
    quad = QUAD()
    ema_quad = EMA(9)
    trend = MeasureTrend()
    diffwindow = DiffWindow(30)
    last_diff_result = 0

    initial_time = float(klines[0][0])

    for i in range(1, len(klines) - 1):
        ts = (float(klines[i][0]) - initial_time) / (60.0)
        price_min.append(float(klines[i][1]))
        price_max.append(float(klines[i][2]))
        quad.update(ema_quad.update(klines[i][3]), ts)
        vwaps.append(vwap.kline_update(float(klines[i][1]), float(klines[i][2]), float(klines[i][4]), float(klines[i][5])))
        if 1: #try:
            A, B, C = quad.compute()

            if C != 0 and C > 0.0: # and C > min(prices) and C < max(prices):
                if 1: #C > min(prices) and C < max(prices):
                    timestamp_max = initial_time + 60.0 * (-B / (2 * A))
                    timestamp_current = initial_time + i * 60.0
                    print(A, B, C, timestamp_current, prices[i], timestamp_max)
                    #ts = ts + 2.0
                    y = A * (ts * ts) + (B * ts) + C
                    #if y > min(prices) and y < max(prices):
                    quad_x.append(ts)
                    quad_y.append(ema_quad.update(y))
                    #else:
                    #    last_diff_result = 0
                    quad_maxes.append(C)
        #except:
        #    pass
    print(quad_x)

    price_max_value = max(price_max)
    diff = price_max_value - min(price_min)
    level1 = price_max_value - 0.236 * diff
    level2 = price_max_value - 0.382 * diff
    level3 = price_max_value - 0.618 * diff

    plt.axhspan(level1, min(price_min), alpha=0.4, color='lightsalmon')
    plt.axhspan(level2, level1, alpha=0.5, color='palegoldenrod')
    plt.axhspan(level3, level2, alpha=0.5, color='palegreen')
    plt.axhspan(price_max_value, level3, alpha=0.5, color='powderblue')

    vwap0 = []
    for kline in klines:
        vwap.kline_update(low=kline[1], high=kline[2], close=kline[4], volume=kline[5])
        vwap0.append(vwap.result)

    ema0 = compute_ema_dict_from_klines(klines, 4)
    # Create linear regression object
    regr = linear_model.LinearRegression()

    # Train the model using the training sets
    #ema_x = []
    #for i in range(0, len(ema0['y'])):
    #    ema_x
    #regr.fit(ema0['x'], ema0['y']


    #ema1 = compute_ema_dict_from_klines(klines, 12)
    #ema2 = compute_ema_dict_from_klines(klines, 26)
    smma0 = compute_smma_from_kline_prices(prices, 12)
    count = 0
    diff_values = []
    for i in range(0, len(quad_y)):
        diff_values.append(diffwindow.update(quad_y[i]))
        if diffwindow.detect_peak() and last_diff_result != -1:
            plt.axvline(x=quad_x[i], color='blue')
            print(diffwindow.get_max_value())
            last_diff_result = -1
        elif diffwindow.detect_valley() and last_diff_result != 1:
            plt.axvline(x=quad_x[i], color='red')
            print(diffwindow.get_min_value())
            last_diff_result = 1
        #elif diffwindow.detect_falling():
        #    plt.axvline(x=count, color='orange')
        #elif diffwindow.detect_rising():
        #    plt.axvline(x=count, color='green')
        count += 1
    #compute_ema_crossover_from_klines(ema1, ema2)
    prices = prices_from_kline_data(klines)
    symprice, = plt.plot(prices, label=product) #, color='black')
    #minprice, =  plt.plot(price_min, label='MIN')
    #maxprice, =  plt.plot(price_max, label='MAX')
    #sma12, = plt.plot(smma0, label='SMMA12')
    ema4, = plt.plot(ema0["y"], label='EMA4')
    plt.plot(vwaps)
    #quad0, = plt.plot(quad_x, quad_y, label='QUAD')
    #plt.plot(diff_values)
    #quadmax0, = plt.plot(quad_x, quad_maxes, label='QUADMAX')
    #vwap30, = plt.plot(vwap0, label='VWAP30')
    #macd0, = plt.plot(macd_signal, label='MACDSIG')
    #ema12, = plt.plot(ema1["y"], label='EMA12')
    #ema26, = plt.plot(ema2["y"], label='EMA26')
    #ema50, = plt.plot(compute_ema_from_kline_prices(prices, 50), label='EMA50')
    plt.legend(handles=[symprice, ema4])
    print(diff_values)
    return diff_values

def abs_average(values):
    total = 0.0
    for value in values:
        total += abs(value)
    total = total / float(len(values))
    return total

if __name__ == '__main__':
    ticker = 'LTC-USD'
    plt.figure(1)
    plt.subplot(211)
    klines = retrieve_klines_24hrs(ticker)
    #klines = retrieve_klines_last_hour(ticker, hours=5)

    diff_values = plot_emas_product(plt, klines, ticker)

    plt.subplot(212)
    plt.plot(diff_values)
    #klines2 = retrieve_klines_24hrs('BTC-USD')
    klines2 = retrieve_klines_last_hour('LTC-USD', hours=5)

    prices2 = np.array(prices_from_kline_data(klines2))
    prices1 = np.array(prices_from_kline_data(klines))
    avg1 = abs_average(prices1)
    avg2 = abs_average(prices2)
    print(avg1)
    print(avg2)
    if avg2 > avg1:
        scalar = (max(prices2) - min(prices2)) / (max(prices1) - min(prices1))
        print(scalar)
        prices1 = scalar * (prices1 - avg1)
        prices2 = prices2 - avg2
    #    for i in range(0, len(prices1)):
    #        prices1[i] += avg2
    elif avg2 < avg1:
        scalar = (max(prices1) - min(prices1)) / (max(prices2) - min(prices2))
        print(scalar)
        prices2 = scalar*prices2 + avg1 - avg2
    #    for i in range(0, len(prices2)):
    #        prices2[i] += avg1

    #diff = prices2 - prices1
    
    #ltc, =plt.plot(prices1, label='ltc')
    #btc, =plt.plot(prices2, label='btc')
    #plt.legend(handles=[ltc, btc])

    #plot_emas_product(plt, klines2, 'BTC-USD')
    #plt.subplot(212)
    macd = MACD()
    #klines = retrieve_klines_last_hour('LTC-USD', hours=4)
    price_changes = []
    volume_changes = []

    last_price = float(klines[0][4])
    last_volume =float(klines[0][5])

    emavol = EMA(4)
    emaprice = EMA(4)

    price_max = []
    price_min = []

    price_min.append(float(klines[0][1]))
    price_max.append(float(klines[0][2]))

    for i in range(1, len(klines)):
        price_changes.append(emaprice.update(float(klines[i][4])))
        volume_changes.append(emavol.update(float(klines[i][5])))
        
        last_price = float(klines[i][4])
        last_volume = float(klines[i][5])

        price_min.append(float(klines[i][1]))
        price_max.append(float(klines[i][2]))

    avg_volume = abs_average(volume_changes)
    avg_price = abs_average(price_changes)

    #for i in range(0, len(price_changes)):
    #    price_changes[i] /= avg_price
    #    volume_changes[i] /= avg_volume


    price_max_value = max(price_max)
    diff = price_max_value - min(price_min)
    level1 = price_max_value - 0.236 * diff
    level2 = price_max_value - 0.382 * diff
    level3 = price_max_value - 0.618 * diff

    #fig, ax = plt.subplots()
    #plt.plot(prices_from_kline_data(klines), color='black')

    #plt.axhspan(level1, min(price_min), alpha=0.4, color='lightsalmon')
    #plt.axhspan(level2, level1, alpha=0.5, color='palegoldenrod')
    #plt.axhspan(level3, level2, alpha=0.5, color='palegreen')
    #plt.axhspan(price_max_value, level3, alpha=0.5, color='powderblue')

    #ema4, = plt.plot(ema0["y"], label='EMA4')
    #macd0, = plt.plot(np.array(price_changes) / avg_price, label='PRICEDIFF')
    #signal0, = plt.plot(np.array(volume_changes) / avg_volume, label='VOLDIFF')
    #plt.legend(handles=[macd0])
    plt.show()
