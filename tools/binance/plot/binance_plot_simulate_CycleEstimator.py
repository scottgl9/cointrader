#!/usr/bin/env python3

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
from trader.indicator.AEMA import AEMA
from trader.indicator.OBV import OBV
from trader.lib.CycleEstimator import CycleEstimator
from trader.account.AccountBinance import AccountBinance
import argparse


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
    accnt = AccountBinance(None, True)
    accnt.load_detail_all_assets()
    accnt.load_info_all_assets()
    cycle_estimator = CycleEstimator()
    close_prices = []
    open_prices = []
    low_prices = []
    high_prices = []
    base_volumes = []
    quote_volumes = []
    obv = OBV()
    obv_aema12 = AEMA(12, scale_interval_secs=60)
    obv_aema12_values = []
    aema6 = AEMA(6, scale_interval_secs=60)
    aema6_values = []
    aema12 = AEMA(12, scale_interval_secs=60)
    aema12_values = []
    aema26 = AEMA(26, scale_interval_secs=60)
    aema26_values = []
    aema50 = AEMA(50, scale_interval_secs=60)
    aema50_values = []
    aema100 = AEMA(100, scale_interval_secs=60)
    aema100_values = []
    aema200 = AEMA(200, scale_interval_secs=60)
    aema200_values = []
    aema_diff_6_12 = []
    min_values = []
    min_x_values = []
    max_values = []
    max_x_values = []

    base_step_size = accnt.get_base_step_size(base=base, currency=currency)
    print("base step size: {}".format(base_step_size))
    currency_step_size = accnt.get_currency_step_size(base=base, currency=currency)
    print("currency step size: {}".format(currency_step_size))

    i=0
    for msg in get_rows_as_msgs(c):
        close = float(msg['c'])
        low = float(msg['l'])
        high = float(msg['h'])
        open = float(msg['o'])
        volume_base = float(msg['v'])
        volume_quote = float(msg['q'])
        ts = int(msg['E'])

        base_volumes.append(volume_base)
        quote_volumes.append(volume_quote)

        obv.update(close, volume_base)
        obv_aema12.update(obv.result, ts)
        obv_aema12_values.append(obv_aema12.result)
        aema6_values.append(aema6.update(close, ts))
        aema12_values.append(aema12.update(close, ts))
        aema26_values.append(aema26.update(close, ts))
        aema50_values.append(aema50.update(close, ts))
        aema100_values.append(aema100.update(close, ts))
        aema200_values.append(aema200.update(close, ts))

        if aema12.result:
            value = accnt.round_quote(aema12.result, currency_step_size)
            cycle_estimator.update(value, ts)
            min_value, max_value = cycle_estimator.get_trade_range()
            if min_value and max_value:
                min_x_values.append(i)
                min_values.append(min_value)
                max_x_values.append(i)
                max_values.append(max_value)

        close_prices.append(close)
        open_prices.append(open)
        low_prices.append(low)
        high_prices.append(high)

        i += 1

    print(cycle_estimator.price_count_index)
    plt.subplot(211)
    symprice, = plt.plot(close_prices, label=ticker_id)

    fig1, = plt.plot(aema12_values, label='AEMA12')
    fig3, = plt.plot(aema50_values, label='AEMA50')
    fig4, = plt.plot(aema100_values, label='AEMA100')
    fig5, = plt.plot(aema200_values, label='AEMA200')
    fig6, = plt.plot(aema26_values, label='AEMA26')
    plt.plot(min_x_values, min_values)
    plt.plot(max_x_values, max_values)
    plt.legend(handles=[symprice, fig1, fig3, fig4, fig5, fig6])

    #plt.subplot(312)
    #plt.plot(aema_diff_6_12)

    plt.subplot(212)
    plt.plot(obv_aema12_values)
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
