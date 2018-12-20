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
from trader.lib.IndicatorCache import IndicatorCache

def simulate(conn, client, base, currency):
    ticker_id = "{}{}".format(base, currency)
    cache = IndicatorCache(ticker_id)
    cache.load_cache_from_db(conn)

    plt.subplot(211)
    cache_list = cache.get_cache_list()
    handles = []
    for id, values in cache_list.items():
        if id == 'ts' or id.startswith('O'):
            continue
        handle, = plt.plot(values, label=id)
        handles.append(handle)

    #fig21, = plt.plot(obv_ema12_values, label='OBV12')
    #fig22, = plt.plot(obv_ema26_values, label='OBV26')
    #fig23, = plt.plot(obv_ema50_values, label='OBV50')
    plt.legend(handles=handles)
    #plt.plot(signal_values)
    #plt.plot(tsi_values)
    plt.show()

if __name__ == '__main__':
    client = None

    base = 'BTC'
    currency='USDT'
    filename = 'cache.db'
    if len(sys.argv) == 4:
        base=sys.argv[1]
        currency = sys.argv[2]
        filename = sys.argv[3]
    if len(sys.argv) == 3:
        base=sys.argv[1]
        currency = sys.argv[2]

    print("Loading {}".format(filename))
    conn = sqlite3.connect(filename)

    simulate(conn, client, base, currency)
    conn.close()
