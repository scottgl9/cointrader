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
from trader.indicator.EMA import EMA
from trader.indicator.LSMA import LSMA
from trader.lib.Indicator import Indicator

def get_rows_as_msgs(c):
    msgs = []
    for row in c:
        msg = {'ts': int(row[0]), 'close': float(row[1]), 'high': float(row[2]), 'low': float(row[3]),
               'open': float(row[4]), 'volume_quote': float(row[5]), 's': row[6], 'volume': float(row[7])}
        msgs.append(msg)
    return msgs


def simulate(conn, client, base, currency):
    ticker_id = "{}{}".format(base, currency)
    c = conn.cursor()
    #c.execute("SELECT * FROM miniticker WHERE s='{}' ORDER BY E ASC".format(ticker_id))
    c.execute("SELECT E,c,h,l,o,q,s,v FROM miniticker WHERE s='{}'".format(ticker_id)) # ORDER BY E ASC")")

    msgs = get_rows_as_msgs(c)
    close_prices = []
    for msg in msgs:
        close_prices.append(msg['close'])

    ema12 = Indicator(EMA, 12, scale=24)
    ema12.load(msgs)
    ema12_values = ema12.results()
    lsma = Indicator(LSMA, 12)
    lsma.load(msgs)
    lsma_values = lsma.results()
    ema12.load(msgs)
    ema12_values = ema12.results()
    obv = Indicator(OBV)
    obv.load(msgs)
    obv_values = obv.results()

    plt.subplot(211)
    symprice, = plt.plot(close_prices, label=ticker_id)
    fig1, = plt.plot(ema12_values, label='EMA12')
    fig2, = plt.plot(lsma_values, label='LSMA12')
    plt.legend(handles=[symprice, fig1, fig2])
    plt.subplot(212)
    fig21, = plt.plot(obv_values, label='OBV')
    plt.legend(handles=[fig21])
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

    parser.add_argument('-s', action='store', dest='symbol',
                        default='BTCUSDT',
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

    simulate(conn, client, base, currency)
    conn.close()
