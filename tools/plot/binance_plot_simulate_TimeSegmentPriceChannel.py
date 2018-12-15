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
from trader.lib.TimeSegmentValues import TimeSegmentValues
from trader.indicator.DTWMA import DTWMA
from trader.indicator.ZLEMA import *
from trader.lib.TimeSegmentPriceChannel import TimeSegmentPriceChannel


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
    ema50 = EMA(100, scale=24, lag_window=5)
    ema200 = EMA(200, scale=24, lag_window=5)

    dtwma = DTWMA(window=30)
    tspc = TimeSegmentPriceChannel(seconds=3600)
    tspc_min_values = []
    tspc_min_x_values = []
    tspc_max_values = []
    tspc_max_x_values = []
    tspc_mid_values = []
    tspc_mid_x_values = []

    ema12_values = []
    ema26_values = []
    ema50_values = []
    ema200_values = []
    close_prices = []
    open_prices = []
    low_prices = []
    high_prices = []
    volumes = []

    i=0
    for msg in get_rows_as_msgs(c):
        close = float(msg['c'])
        low = float(msg['l'])
        high = float(msg['h'])
        open = float(msg['o'])
        volume = float(msg['v'])
        ts=int(msg['E'])
        volumes.append(volume)

        ema12_value = ema12.update(close)
        ema12_values.append(ema12_value)
        ema26_values.append(ema26.update(close))
        ema50_value = ema50.update(close)
        ema50_values.append(ema50_value)
        ema200_value = ema200.update(close)
        ema200_values.append(ema200_value)

        tspc.update(close, ts)
        if tspc.min() != 0:
            tspc_min_values.append(tspc.min())
            tspc_min_x_values.append(i)
        if tspc.max() != 0:
            tspc_max_values.append(tspc.max())
            tspc_max_x_values.append(i)
        if tspc.median() != 0:
            tspc_mid_values.append(tspc.median())
            tspc_mid_x_values.append(i)

        close_prices.append(close)
        open_prices.append(open)
        low_prices.append(low)
        high_prices.append(high)
        #lstsqs_x_values.append(i)
        i += 1

    plt.subplot(211)
    symprice, = plt.plot(close_prices, label=ticker_id)
    #fig1, = plt.plot(ema12_values, label='EMA12')
    #fig2, = plt.plot(ema26_values, label='EMA26')
    #fig3, = plt.plot(ema50_values, label='EMA50')
    #fig4, = plt.plot(ema200_values, label='EMA200')
    plt.plot(tspc_min_x_values, tspc_min_values)
    plt.plot(tspc_max_x_values, tspc_max_values)
    plt.plot(tspc_mid_x_values, tspc_mid_values)
    plt.legend(handles=[symprice])#, fig1, fig2, fig3, fig4])
    #plt.subplot(312)
    #fig21, = plt.plot(tsv_x_values, tsv_values, label='TSV_PERCENT')
    #fig22, = plt.plot(tsv2_x_values, tsv2_values, label='TSV2_PERCENT')
    #plt.legend(handles=[fig21, fig22])
    #plt.subplot(313)
    #fig31, = plt.plot(tsv_x_values, tsv_counts, label='TSV_COUNTS')
    #fig32, = plt.plot(tsv2_x_values, tsv2_counts, label='TSV2_COUNTS')
    #plt.legend(handles=[fig31, fig32])

    plt.show()

if __name__ == '__main__':
    client = Client(MY_API_KEY, MY_API_SECRET)

    base = 'BTC'
    currency='USDT'
    filename = 'cryptocurrency_database.miniticker_collection_04092018.db'
    if len(sys.argv) == 4:
        base=sys.argv[1]
        currency = sys.argv[2]
        filename = sys.argv[3]
    if len(sys.argv) == 3:
        base=sys.argv[1]
        currency = sys.argv[2]

    print("Loading {}".format(filename))
    conn = sqlite3.connect(filename)

    simulate(conn, client, base, currency, type="MACD")
    conn.close()