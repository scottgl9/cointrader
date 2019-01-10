#!/usr/bin/python

import sys
try:
    import trader
except ImportError:
    sys.path.append('.')
    import trader

import sqlite3
import sys
from trader.account.binance.client import Client
from trader.config import *
import matplotlib.pyplot as plt
import argparse
from trader.indicator.OBV import OBV
from trader.indicator.ZLEMA import *
from trader.indicator.DTWMA import DTWMA
from trader.lib.SegmentJump import SegmentJump

def get_rows_as_msgs(c):
    msgs = []
    for row in c:
        msg = {'E': row[0], 'c': row[1], 'h': row[2], 'l': row[3],
               'o': row[4], 'q': row[5], 's': row[6], 'v': row[7]}
        msgs.append(msg)
    return msgs


def simulate(conn, client, base, currency, type="channel"):
    ticker_id = "{}{}".format(base, currency)
    c = conn.cursor()
    #c.execute("SELECT * FROM miniticker WHERE s='{}' ORDER BY E ASC".format(ticker_id))
    c.execute("SELECT E,c,h,l,o,q,s,v FROM miniticker WHERE s='{}'".format(ticker_id)) # ORDER BY E ASC")")

    ema12 = EMA(12, scale=24)
    ema26 = EMA(26, scale=24)
    ema50 = EMA(50, scale=24)
    ema100 = EMA(100, scale=24)
    ema200 = EMA(200, scale=24)
    obv_ema12 = EMA(12, scale=24)
    obv_ema26 = EMA(26, scale=24)
    obv_ema50 = EMA(50,scale=24)
    obv_ema12_values = []
    obv_ema26_values = []
    obv_ema50_values = []

    #tsj_filter = EMA(26, scale=24)
    tsj = SegmentJump(tsv1_minutes=1, tsv2_minutes=15, up_multiplier=4, down_multiplier=3) #, filter=tsj_filter)
    tsj_values = []

    obv = OBV()
    ema12_values = []
    ema26_values = []
    ema100_values = []
    ema200_values = []
    close_prices = []
    open_prices = []
    low_prices = []
    high_prices = []
    volumes = []

    peaks = []
    valleys = []

    i=0
    for msg in get_rows_as_msgs(c):
        close = float(msg['c'])
        low = float(msg['l'])
        high = float(msg['h'])
        open = float(msg['o'])
        volume = float(msg['v'])
        ts = int(msg['E'])

        volumes.append(volume)

        obv_value = obv.update(close=close, volume=volume)
        obv_ema12_values.append(obv_ema12.update(obv_value))
        obv_ema26_values.append(obv_ema26.update(obv_value))
        obv_ema50_values.append(obv_ema50.update(obv_value))

        ema12_value = ema12.update(close)
        ema12_values.append(ema12_value)
        ema26_values.append(ema26.update(close))
        ema50.update(close)
        ema100_value = ema100.update(close)
        ema100_values.append(ema100_value)
        ema200_value = ema200.update(close)
        ema200_values.append(ema200_value)

        tsj_values.append(tsj.update(ema26.result, ts))

        if tsj.up_detected():
            valleys.append(i)
        elif tsj.down_detected():
            peaks.append(i)

        close_prices.append(close)
        open_prices.append(open)
        low_prices.append(low)
        high_prices.append(high)
        i += 1

    plt.subplot(311)

    for index in peaks:
        plt.axvline(x=index, color='red')
    for index in valleys:
        plt.axvline(x=index, color='green')

    symprice, = plt.plot(close_prices, label=ticker_id)

    fig1, = plt.plot(ema12_values, label='EMA12')
    fig2, = plt.plot(ema26_values, label='EMA26')
    fig3, = plt.plot(ema100_values, label='EMA100')
    fig4, = plt.plot(ema200_values, label='EMA200')
    plt.legend(handles=[symprice, fig1, fig2, fig3, fig4])
    plt.subplot(312)
    plt.plot(tsj_values)
    plt.subplot(313)
    #fig21, = plt.plot(obv_ema12_values, label='OBV12')
    #fig22, = plt.plot(obv_ema26_values, label='OBV26')
    #fig23, = plt.plot(obv_ema50_values, label='OBV50')
    #plt.legend(handles=[fig21, fig22, fig23])
    plt.plot(volumes)
    #plt.plot(signal_values)
    #plt.plot(tsi_values)
    plt.show()

if __name__ == '__main__':
    client = None

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', action='store', dest='filename',
                        default='cryptocurrency_database.miniticker_collection_04092018.db',
                        help='filename of kline sqlite db')

    parser.add_argument('-b', action='store', dest='base',
                        default='BTC',
                        help='base part of symbol')

    parser.add_argument('-c', action='store', dest='currency',
                        default='USDT',
                        help='currency part of symbol')

    results = parser.parse_args()

    if not os.path.exists(results.filename):
        print("file {} doesn't exist, exiting...".format(results.filename))
        sys.exit(-1)

    filename = results.filename
    base = results.base
    currency = results.currency

    print("Loading {}".format(filename))
    conn = sqlite3.connect(filename)

    simulate(conn, client, base, currency, type="MACD")
    conn.close()
