#!/usr/bin/python

#from pymongo import MongoClient
import os.path
import time
import sys
import math
#from gdax.myhelpers import *
from trader import gdax
import sqlite3
from datetime import datetime, timedelta
from pypika import Query, Table, Field, Order
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as md
from trader.indicator.SMMA import SMMA
from trader.indicator.EMA import EMA
from trader.indicator.SMA import SMA
from trader.MeasureTrend import MeasureTrend

week = ['Sunday',
        'Monday',
        'Tuesday',
        'Wednesday',
        'Thursday',
        'Friday',
        'Saturday']

def query_klines_sort_field(c, select_field, order_field):
    q = Query.from_('klines').select(select_field).orderby(order_field, order=Order.desc).limit(50)
    #c.execute("SELECT {} FROM klines ORDER BY {} DESC LIMIT 100".format(select_field, order_field))
    c.execute(str(q))
    for row in c:
        print(row)
        dt = datetime.utcfromtimestamp(row[0])
        print(week[dt.weekday()])
        print(dt.strftime('%Y-%m-%dT%H:%M:%S'))

def query_klines_sort_diff(c):
    klines = Table('klines')
    #q = Query.from_(klines).select('timestamp', (klines.close - klines.open).as_('profit')).orderBy('profit')#limit(50) #.orderBy((klines.close - klines.open).as_('profit')).limit(50)
    #q = "SELECT klines.timestamp, klines.open, klines.close, klines.close - klines.open as diff FROM klines ORDER BY diff DESC"
    q = "SELECT klines.open, klines.close, klines.volume, klines.timestamp FROM klines ORDER BY klines.timestamp ASC"
    c.execute(str(q))
    open_prices = []
    close_prices = []
    base_prices = []
    timestamps = []
    volumes = []
    ema = SMMA(12)
    ema2 = EMA(12)
    ema3 = EMA(26)
    ema4 = EMA(50)
    ema_volumes = []
    ema_values = []
    last_value = 0.0
    trend = MeasureTrend()
    for row in c:
        #print(row)
        #dt = datetime.utcfromtimestamp(row[0])
        #if float(row[0]) > 500.0:
        open_prices.append(float(row[0]))
        open_prices.append(float(row[1]))
        #    open_prices.append 
        #   #base_prices.append(math.log(float(row[0]), 10))
        #    #base_prices.append(ema3.update(float(row[0])))
        close_prices.append(float(row[1]))
        volumes.append(float(row[2]))
        timestamps.append(datetime.fromtimestamp(int(row[3])))
        value = float(row[0])#ema.update(float(row[2]))
        ema_value = ema2.update(value)
        ema_values.append(ema_value)
        #if float(row[2]) >= value:
        if last_value != 0.0:
            ema_volumes.append(ema.update(abs((value - last_value) / last_value)))#float(row[2]))
        last_value = value
        #else:
        #    ema_volumes.append(0.0)

    #for value in np.exp(open_prices[:350000]):
    #    if value != np.NaN and value != np.inf:
    #        print(value)
    plt.figure(1)
    plt.subplot(211)
    #ema_values = ema_values[-3000:-1]
    #last_peak = 0.0
    #last_valley = 0.0
    #for i in range(0, len(ema_values)):
    #    trend.update_price(ema_values[i])
    #    peak_price = trend.get_peak_price()
    #    valley_price = trend.get_valley_price()
    #    if peak_price != 0.0:
    #        if last_peak != 0.0 and abs(peak_price - last_peak)/last_peak > 0.02:
    #            print(peak_price)
    #            print(abs(peak_price - last_peak) / last_peak)
    #            plt.axvline(x=i)
    #        last_peak = peak_price
    #    if valley_price != 0.0:
    #        if last_valley != 0.0 and abs(valley_price - last_valley)/last_valley > 0.02:
    #            print(valley_price)
    #            print(abs(valley_price - last_valley) / last_valley)
    #            plt.axvline(x=i, color='red')
    #        last_valley = valley_price


    #plt.plot(timestamps[-3000:-1], open_prices[-3000:-1])
    #plt.plot(timestamps[-3000:-1], ema_values)
    #plt.plot(open_prices)
    # attempt #1
    #result = np.log10(np.array(open_prices))
    for value in open_prices:
        base_prices.append(ema3.update(value))
    noise = np.array(open_prices) - np.array(base_prices)
    #noise = np.array(open_prices) - np.array(base_prices)
    #result = np.log((np.array(open_prices) ** 2 - noise ** 2))
    result = np.log((np.array(open_prices) - noise)) ** 2#np.sqrt(result ** 2 - noise ** 2)

    #smoother = []
    #for value in result:
    #    smoother.append(ema4.update(value))
    #noise2 = result - np.array(smoother)

    plt.plot(open_prices)
    #plt.plot(result) # - noise2)
    #plt.plot(np.log10(np.sqrt(result)))
    #ax = plt.gca()
    #xfmt = md.DateFormatter('%Y-%m-%d %H:%M:%S')
    #ax.xaxis.set_major_formatter(xfmt)
    #plt.plot(close_prices[-3000:-1])
    plt.subplot(212)
    #plt.plot(ema_volumes[-3000:-1])
    #plt.plot(ema_volumes)
    plt.plot(noise)
    #plt.plot(np.log10(open_prices))
    #plt.plot(np.log2(open_prices))
    #plt.plot(base_prices)
    plt.show()

if __name__ == '__main__':
        ticker_id = 'LTC-BTC'
        conn = sqlite3.connect('{}_klines.db'.format(ticker_id.replace('-', '_')))
        c = conn.cursor()
        query_klines_sort_diff(c) #, '*', 'volume')
        conn.close()
