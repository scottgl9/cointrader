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
import matplotlib.pyplot as plt
import argparse
from trader.lib.unused.Angle import Angle
from trader.lib.MAAvg import MAAvg
from trader.indicator.DTWMA import DTWMA
from trader.indicator.EMA import EMA
from trader.account.AccountBinance import AccountBinance


def get_rows_as_msgs(c):
    msgs = []
    for row in c:
        msg = {'E': row[0], 'c': row[1], 'h': row[2], 'l': row[3],
               'o': row[4], 'q': row[5], 's': row[6], 'v': row[7]}
        msgs.append(msg)
    return msgs


def simulate(conn, client, base, currency, filename, type="channel"):
    ticker_id = "{}{}".format(base, currency)
    c = conn.cursor()
    #c.execute("SELECT * FROM miniticker WHERE s='{}' ORDER BY E ASC".format(ticker_id))
    c.execute("SELECT E,c,h,l,o,q,s,v FROM miniticker WHERE s='{}'".format(ticker_id)) # ORDER BY E ASC")")

    accnt = AccountBinance(client, simulation=True, simulate_db_filename=filename)

    info =  accnt.get_asset_info(ticker_id)
    print(info)
    tick_size = info['tickSize']
    step_size = info['stepSize']
    min_notional = info['minNotional']

    ema12 = EMA(12, scale=24)
    ema26 = EMA(26, scale=24)
    ema50 = EMA(100, scale=24, lag_window=5)
    ema200 = EMA(200, scale=24, lag_window=5)

    maavg = MAAvg()
    maavg.add(ema12)
    maavg.add(ema26)
    maavg.add(ema50)

    dtwma = DTWMA(window=30)
    angle = Angle(seconds=3600, tick_size=tick_size, step_size=step_size)
    angle_values = []
    ema12_values = []
    ema26_values = []
    ema50_values = []
    ema200_values = []
    maavg_values = []
    detrend_values = []
    detrend_x_values = []
    close_prices = []
    open_prices = []
    low_prices = []
    diff_values = []
    signal_values = []
    high_prices = []
    volumes = []

    i=0
    for msg in get_rows_as_msgs(c):
        close = float(msg['c'])
        low = float(msg['l'])
        high = float(msg['h'])
        open = float(msg['o'])
        volume = float(msg['v'])
        ts = int(msg['E'])
        volumes.append(volume)

        ema12.update(close)
        ema26.update(close)
        ema50.update(close)
        ema200.update(close)
        maavg.update()
        maavg_values.append(maavg.result)
        ema12_values.append(ema12.result)
        ema26_values.append(ema26.result)
        ema200_values.append(ema200.result)

        if maavg.result != 0 and ema200.result != 0:
            angle.update(value1=maavg.result, value2=ema200.result, ts=ts)
            if angle.result != 0:
                angle_values.append(angle.result)

        result = angle.detrend_result()
        if result != 0:
            detrend_values.append(result)
            detrend_x_values.append(i)

        close_prices.append(close)
        open_prices.append(open)
        low_prices.append(low)
        high_prices.append(high)
        #lstsqs_x_values.append(i)
        i += 1

    plt.subplot(211)
    #symprice, = plt.plot(close_prices, label=ticker_id)
    fig1, = plt.plot(maavg_values, label='MAAVG')
    fig4, = plt.plot(ema200_values, label='EMA200')
    plt.legend(handles=[fig1])
    plt.subplot(212)
    fig21, = plt.plot(angle_values, label='ANGLE')
    #fig22, = plt.plot(slope2_values, label='SLOPE26')

    #plt.plot(bb_low_values)
    plt.legend(handles=[fig21])
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

    simulate(conn, client, base, currency, filename, type="MACD")
    conn.close()
