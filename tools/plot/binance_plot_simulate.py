#!/usr/bin/python

import sys
try:
    import trader
except ImportError:
    sys.path.append('.')
    import trader

import os.path
import time
import sqlite3
import sys
from trader.WebHandler import WebThread
from trader.account.binance.client import Client
from trader.MultiTrader import MultiTrader
from trader.account.AccountBinance import AccountBinance
from trader.config import *
import numpy as np
import matplotlib.pyplot as plt
from trader.indicator.ehler.FREMA import FREMA
from trader.indicator.ehler.DSMA import DSMA
from trader.indicator.ehler.InstantTrendline import InstantTrendline

def get_rows_as_msgs(c):
    msgs = []
    for row in c:
        msg = {'E': row[0], 'c': row[1], 'h': row[2], 'l': row[3],
               'o': row[4], 'q': row[5], 's': row[6], 'v': row[7]}
        msgs.append(msg)
    return msgs


def simulate(conn, client, base, currency, indicator_name):
    ticker_id = "{}{}".format(base, currency)
    c = conn.cursor()
    #c.execute("SELECT * FROM miniticker WHERE s='{}' ORDER BY E ASC".format(ticker_id))
    c.execute("SELECT E,c,h,l,o,q,s,v FROM miniticker WHERE s='{}'".format(ticker_id)) # ORDER BY E ASC")")

    open_prices = []
    close_prices = []
    low_prices = []
    high_prices = []
    indicator = None
    if indicator_name == 'FREMA':
        indicator = FREMA()
    elif indicator_name == 'DSMA':
        indicator = DSMA()
    elif indicator_name == 'InstantTrendline':
        indicator = InstantTrendline()

    indicator_values = []

    i=0
    for msg in get_rows_as_msgs(c):
        close = float(msg['c'])
        low = float(msg['l'])
        high = float(msg['h'])
        open = float(msg['o'])
        volume = float(msg['v'])

        result = indicator.update(close)
        if result != 0:
            indicator_values.append(result)

        close_prices.append(close)
        open_prices.append(open)
        low_prices.append(low)
        high_prices.append(high)
        #lstsqs_x_values.append(i)
        i += 1

    fig = plt.figure()
    ax = fig.add_subplot(2,1,1)

    symprice, = plt.plot(close_prices, label=ticker_id)
    plt.legend(handles=[symprice])
    plt.subplot(212)
    plt.plot(indicator_values)
    plt.show()

if __name__ == '__main__':
    base = 'BTC'
    currency='USDT'
    filename = 'cryptocurrency_database.miniticker_collection_04092018.db'
    indicator = "EMA"
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("{} <base> <currency> <db filename> <indicator name>".format(sys.argv[0]))
        sys.exit(0)
    if len(sys.argv) == 5:
        base=sys.argv[1]
        currency = sys.argv[2]
        filename = sys.argv[3]
        indicator = sys.argv[4]
    if len(sys.argv) == 4:
        base=sys.argv[1]
        currency = sys.argv[2]
        filename = sys.argv[3]
    if len(sys.argv) == 3:
        base=sys.argv[1]
        currency = sys.argv[2]

    print("Loading {}".format(filename))
    conn = sqlite3.connect(filename)

    client = Client(MY_API_KEY, MY_API_SECRET)

    simulate(conn, client, base, currency, indicator)
    conn.close()
