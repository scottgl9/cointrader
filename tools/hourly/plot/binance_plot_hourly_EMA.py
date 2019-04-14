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
from trader.account.binance.client import Client
from trader.config import *
import matplotlib.pyplot as plt
import argparse
from trader.indicator.OBV import OBV
try:
    from trader.indicator.native.EMA import EMA
except ImportError:
    from trader.indicator.EMA import EMA

def get_rows_as_msgs(c):
    msgs = []
    cnames = ['ts', 'open', 'high', 'low', 'close', 'base_volume', 'quote_volume',
              'trade_count', 'taker_buy_base_volume', 'taker_buy_quote_volume']
    for row in c:
        msg = {}
        for i in range(0, len(cnames)):
            msg[cnames[i]] = row[i]
        msgs.append(msg)
    return msgs


def simulate(conn, symbol):
    c = conn.cursor()
    c.execute("SELECT * FROM {} ORDER BY ts ASC".format(symbol))

    obv = OBV()
    ema12 = EMA(12, scale=24)
    ema26 = EMA(26, scale=24)
    ema50 = EMA(50, scale=24)
    ema100 = EMA(100, scale=24)
    ema200 = EMA(200, scale=24)
    ema300 = EMA(300, scale=24)
    ema500 = EMA(500, scale=24)
    obv_ema12 = EMA(12)
    obv_ema26 = EMA(26)
    obv_ema50 = EMA(50)
    obv_ema12_values = []
    obv_ema26_values = []
    obv_ema50_values = []
    ema12_values = []
    ema26_values = []
    ema50_values = []
    ema100_values = []
    ema200_values = []
    ema300_values = []
    ema500_values = []
    close_prices = []
    open_prices = []
    low_prices = []
    high_prices = []
    volumes = []

    i=0
    for msg in get_rows_as_msgs(c):
        ts = int(msg['ts'])
        close = float(msg['close'])
        low = float(msg['low'])
        high = float(msg['high'])
        open = float(msg['open'])
        volume = float(msg['quote_volume'])
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
        ema100.update(close)
        ema100_values.append(ema100.result)
        ema200.update(close)
        ema200_values.append(ema200.result)
        ema300.update(close)
        ema300_values.append(ema300.result)
        ema500.update(close)
        ema500_values.append(ema500.result)

        close_prices.append(close)
        open_prices.append(open)
        low_prices.append(low)
        high_prices.append(high)
        i += 1

    plt.subplot(211)
    symprice, = plt.plot(close_prices, label=symbol)

    fig1, = plt.plot(ema12_values, label='EMA12')
    fig2, = plt.plot(ema26_values, label='EMA26')
    fig3, = plt.plot(ema50_values, label='EMA50')
    fig4, = plt.plot(ema200_values, label='EMA200')
    plt.legend(handles=[symprice, fig1, fig2, fig3, fig4])
    plt.subplot(212)
    fig21, = plt.plot(obv_ema12_values, label='OBV12')
    fig22, = plt.plot(obv_ema26_values, label='OBV26')
    fig23, = plt.plot(obv_ema50_values, label='OBV50')
    plt.legend(handles=[fig21, fig22, fig23])
    plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', action='store', dest='filename',
                        default='binance_hourly_klines.db',
                        help='filename of hourly kline sqlite db')

    parser.add_argument('-s', action='store', dest='symbol',
                        default='BTCUSDT',
                        help='trade symbol')

    results = parser.parse_args()

    if not os.path.exists(results.filename):
        print("file {} doesn't exist, exiting...".format(results.filename))
        sys.exit(-1)

    filename = results.filename
    symbol = results.symbol

    print("Loading {}".format(filename))
    conn = sqlite3.connect(filename)

    simulate(conn, symbol)
    conn.close()
