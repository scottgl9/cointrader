#!/usr/bin/python

import sys
try:
    import trader
except ImportError:
    sys.path.append('.')
    import trader

import sqlite3
import sys
import os
from datetime import datetime
import time
from trader.account.binance.client import Client
from trader.config import *
import matplotlib.pyplot as plt
import argparse
from trader.HourlyKlinesDB import HourlyKlinesDB
import numpy as np
import pylab as plt
from numpy import fft
import pandas as pd
from trader.lib.Fourier import FourierFit, FourierFilter


# def fourierExtrapolation(x, n_predict=0, n_harm=10):
#     n = x.size
#     #n_harm = 10                     # number of harmonics in model
#     t = np.arange(0, n)
#     p = np.polyfit(t, x, 1)         # find linear trend in x
#     x_notrend = x - p[0] * t        # detrended x
#     x_freqdom = fft.fft(x_notrend)  # detrended x in frequency domain
#     f = fft.fftfreq(n)
#     indexes = list(range(n))             # frequencies
#     # sort indexes by frequency, lower -> higher
#     indexes.sort(key = lambda i: np.absolute(f[i]))
#
#     t = np.arange(0, n + n_predict)
#     restored_sig = np.zeros(t.size)
#     for i in indexes[:1 + n_harm * 2]:
#         ampli = np.absolute(x_freqdom[i]) / n   # amplitude
#         phase = np.angle(x_freqdom[i])          # phase
#         restored_sig += ampli * np.cos(2 * np.pi * f[i] * t + phase)
#     return restored_sig + p[0] * t


def simulate(hkdb, symbol, start_ts, end_ts):
    msgs = hkdb.get_dict_klines(symbol, start_ts, end_ts)
    close_prices = []
    open_prices = []
    low_prices = []
    high_prices = []
    volumes = []

    i=0
    for msg in msgs:
        ts = int(msg['ts'])
        close = float(msg['close'])
        low = float(msg['low'])
        high = float(msg['high'])
        open = float(msg['open'])
        volume = float(msg['quote_volume'])
        volumes.append(volume)

        close_prices.append(close)
        open_prices.append(open)
        low_prices.append(low)
        high_prices.append(high)
        i += 1

    x = np.array(close_prices)
    print(x.size)
    ff10 = FourierFit(n_harm=10)
    ff10.load(x)
    ff10.process()
    signal10 = ff10.get_result()

    ff100 = FourierFit(n_harm=100)
    ff100.load(x)
    ff100.process()
    signal100 = ff100.get_result()

    ff500 = FourierFit(n_harm=500)
    ff500.load(x)
    ff500.process()
    signal500 = ff500.get_result()

    fftest = FourierFilter()
    fftest.load(x)
    fftest.process()
    fftest_signal = fftest.get_result()

    plt.subplot(211)
    fig1, = plt.plot(x, label=symbol)
    fig2, = plt.plot(signal10, label='FFT10')
    fig3, = plt.plot(signal100, label='FFT100')
    fig4, = plt.plot(signal500, label='FFT500')
    plt.legend(handles=[fig1, fig2, fig3, fig4])
    plt.subplot(212)
    #fig21, = plt.plot(signal10, label='FFT10')
    #fig22, = plt.plot(signal100, label='FFT100')
    #fig23, = plt.plot(signal500, label='FFT500')
    #plt.legend(handles=[fig21, fig22, fig23])
    plt.plot(x)
    plt.plot(fftest_signal)
    plt.show()


# get first timestamp from kline sqlite db
def get_first_timestamp(filename, symbol):
    conn = sqlite3.connect(filename)
    c = conn.cursor()
    c.execute("SELECT E FROM miniticker WHERE s='{}' ORDER BY E ASC LIMIT 1".format(symbol))
    result = c.fetchone()
    return int(result[0])

def get_last_timestamp(filename, symbol):
    conn = sqlite3.connect(filename)
    c = conn.cursor()
    #c.execute("SELECT ts FROM {} ORDER BY ts DESC LIMIT 1".format(symbol))
    c.execute("SELECT E FROM miniticker WHERE s='{}' ORDER BY E DESC LIMIT 1".format(symbol))
    result = c.fetchone()
    return int(result[0])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # used to get first timestamp for symbol from precaptured live market data
    parser.add_argument('-f', action='store', dest='filename',
                        default='',
                        help='filename of kline sqlite db')

    parser.add_argument('--hours', action='store', dest='hours',
                        default=48,
                        help='Hours before first ts in db specified by -f')

    parser.add_argument('-k', action='store', dest='hourly_filename',
                        default='binance_hourly_klines.db',
                        help='filename of hourly kline sqlite db')

    parser.add_argument('-s', action='store', dest='symbol',
                        default='',
                        help='trade symbol')

    parser.add_argument('-l', action='store_true', dest='list_table_names',
                        default=False,
                        help='List table names in db')

    parser.add_argument('--start-date', action='store', dest='start_date',
                        default='',
                        help='specify start date in month/day/year format')

    parser.add_argument('--end-date', action='store', dest='end_date',
                        default='',
                        help='specify end date in month/day/year format')

    results = parser.parse_args()


    hourly_filename = results.hourly_filename
    symbol = results.symbol
    start_ts = 0
    end_ts = 0

    if results.filename:
        if not os.path.exists(results.filename):
            print("file {} doesn't exist, exiting...".format(results.filename))
            sys.exit(-1)
        else:
            end_ts = get_last_timestamp(results.filename, symbol)
            start_ts = get_first_timestamp(results.filename, symbol)
            start_ts = start_ts - 1000 * 3600 * int(results.hours)
            print(start_ts, end_ts)
    elif results.start_date and results.end_date:
        start_dt = datetime.strptime(results.start_date, '%m/%d/%Y')
        end_dt = datetime.strptime(results.end_date, '%m/%d/%Y')
        start_ts = int(time.mktime(start_dt.timetuple()) * 1000.0)
        end_ts = int(time.mktime(end_dt.timetuple()) * 1000.0)

    if not os.path.exists(results.hourly_filename):
        print("file {} doesn't exist, exiting...".format(results.filename))
        sys.exit(-1)

    hkdb = HourlyKlinesDB(None, hourly_filename, None)
    print("Loading {}".format(hourly_filename))

    if results.list_table_names:
        for symbol in hkdb.get_table_list():
            print(symbol)

    if symbol:
        simulate(hkdb, symbol, start_ts, end_ts)
    else:
        parser.print_help()
    hkdb.close()
