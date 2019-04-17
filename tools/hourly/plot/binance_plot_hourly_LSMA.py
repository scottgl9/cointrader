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
from trader.HourlyKlinesDB import HourlyKlinesDB
from trader.indicator.OBV import OBV
try:
    from trader.indicator.native.EMA import EMA
except ImportError:
    from trader.indicator.EMA import EMA

from trader.indicator.LSMA import LSMA

def simulate(hkdb, symbol):
    msgs = hkdb.get_dict_klines_through_ts(symbol)

    obv = OBV()
    lsma6_obv = LSMA(6)
    lsma24 = LSMA(24)
    # 1 week LSMA
    lsma168 = LSMA(168)
    # 1 month LSMA
    lsma720 = LSMA(720)
    lsma6_obv_values = []
    lsma24_values = []
    lsma168_values = []
    lsma720_values = []
    close_prices = []
    open_prices = []
    low_prices = []
    high_prices = []
    volumes = []

    i=0
    for msg in msgs: #get_rows_as_msgs(c):
        ts = int(msg['ts'])
        close = float(msg['close'])
        low = float(msg['low'])
        high = float(msg['high'])
        open = float(msg['open'])
        volume = float(msg['quote_volume'])
        volumes.append(volume)

        obv_value = obv.update(close=close, volume=volume)
        lsma6_obv_values.append(lsma6_obv.update(obv_value, ts))

        lsma24_values.append(lsma24.update(close, ts))
        lsma168_values.append(lsma168.update(close, ts))
        lsma720_values.append(lsma720.update(close, ts))

        close_prices.append(close)
        open_prices.append(open)
        low_prices.append(low)
        high_prices.append(high)
        i += 1

    plt.subplot(211)
    symprice, = plt.plot(close_prices, label=symbol)

    fig2, = plt.plot(lsma24_values, label='LSMA1DAY')
    fig3, = plt.plot(lsma168_values, label='LSMA1WEEK')
    fig4, = plt.plot(lsma720_values, label='LSMA1MONTH')
    plt.legend(handles=[symprice, fig2, fig3, fig4])
    plt.subplot(212)
    fig21, = plt.plot(lsma6_obv_values, label='OBVLSMA12')
    plt.legend(handles=[fig21])
    plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', action='store', dest='filename',
                        default='binance_hourly_klines.db',
                        help='filename of hourly kline sqlite db')

    parser.add_argument('-s', action='store', dest='symbol',
                        default='',
                        help='trade symbol')

    parser.add_argument('-l', action='store_true', dest='list_table_names',
                        default=False,
                        help='List table names in db')

    results = parser.parse_args()

    if not os.path.exists(results.filename):
        print("file {} doesn't exist, exiting...".format(results.filename))
        sys.exit(-1)

    filename = results.filename
    symbol = results.symbol

    hkdb = HourlyKlinesDB(None, filename, None)
    print("Loading {}".format(filename))

    if results.list_table_names:
        for symbol in hkdb.get_table_list():
            print(symbol)

    if symbol:
        simulate(hkdb, symbol)
    hkdb.close()
