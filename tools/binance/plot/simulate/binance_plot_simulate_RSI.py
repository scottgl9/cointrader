#!/usr/bin/env python3

import sys
try:
    import trader
except ImportError:
    sys.path.append('.')
    import trader

import os.path
import sqlite3
import sys
from trader.indicator.RSI import RSI
import matplotlib.pyplot as plt
import argparse
from trader.indicator.EMA import EMA
from trader.indicator.OBV import OBV


def get_rows_as_msgs(c):
    msgs = []
    for row in c:
        msg = {'E': row[0], 'c': row[1], 'h': row[2], 'l': row[3],
               'o': row[4], 'q': row[5], 's': row[6], 'v': row[7]}
        msgs.append(msg)
    return msgs


def simulate(conn, client, base=None, currency=None, ticker_id=None):
    c = conn.cursor()
    #c.execute("SELECT * FROM miniticker WHERE s='{}' ORDER BY E ASC".format(ticker_id))
    c.execute("SELECT E,c,h,l,o,q,s,v FROM miniticker WHERE s='{}'".format(ticker_id)) # ORDER BY E ASC")")

    ema12 = EMA(12, scale=24)
    ema26 = EMA(26, scale=24)
    ema50 = EMA(50, scale=24, lag_window=5)
    obv_ema12 = EMA(12, scale=24) #EMA(12, scale=24)
    obv_ema26 = EMA(26, scale=24) #EMA(26, scale=24)
    obv_ema50 = EMA(50,scale=24) #EMA(50, scale=24, lag_window=5)
    obv_ema12_values = []
    obv_ema26_values = []
    obv_ema50_values = []

    rsi = RSI(window=30) #, smoother=EMA(12, scale=24), unit_scale=True)
    rsi_values = []
    rsi2 = RSI(window=30, smoother=EMA(24, scale=24))
    rsi2_values = []

    obv = OBV()
    ema12_values = []
    ema26_values = []
    ema50_values = []
    close_prices = []
    open_prices = []
    low_prices = []
    diff_values = []
    signal_values = []
    high_prices = []
    volumes = []

    i=0

    msgs = get_rows_as_msgs(c)

    for msg in msgs:
        close = float(msg['c'])
        low = float(msg['l'])
        high = float(msg['h'])
        open = float(msg['o'])
        volume = float(msg['v'])
        volumes.append(volume)

        obv_value = obv.update(close=close, volume=volume)
        obv_ema12_values.append(obv_ema12.update(obv_value))
        obv_ema26_values.append(obv_ema26.update(obv_value))
        obv_ema50_values.append(obv_ema50.update(obv_value))

        ema12_value = ema12.update(close)
        ema12_values.append(ema12_value)
        ema26_values.append(ema26.update(close))
        ema50_value = ema50.update(close)
        ema50_values.append(ema50_value)

        rsi.update(close)
        if rsi.result != 0:
            rsi_values.append(rsi.result)

        rsi2.update(close)
        if rsi2.result != 0:
            rsi2_values.append(rsi2.result)

        close_prices.append(close)
        open_prices.append(open)
        low_prices.append(low)
        high_prices.append(high)
        #lstsqs_x_values.append(i)
        i += 1

    plt.subplot(211)
    symprice, = plt.plot(close_prices, label=ticker_id)
    #plt.legend(handles=[symprice])
    plt.subplot(212)
    fig11, = plt.plot(rsi_values, label="RSI")
    fig12, = plt.plot(rsi2_values, label="RSI2")
    plt.legend(handles=[fig11, fig12])
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

    symbol_default = 'BTCUSDT'
    parser.add_argument('-s', action='store', dest='symbol',
                        default=symbol_default,
                        help='trade symbol')

    results = parser.parse_args()

    if not os.path.exists(results.filename):
        print("file {} doesn't exist, exiting...".format(results.filename))
        sys.exit(-1)

    filename = results.filename
    base = results.base
    currency = results.currency
    print("Loading {}".format(filename))
    conn = sqlite3.connect(filename)

    ticker_id = "{}{}".format(base, currency)
    if results.symbol != symbol_default:
        ticker_id = results.symbol
    simulate(conn, client, ticker_id=ticker_id)
    conn.close()
