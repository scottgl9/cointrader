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
from trader.lib.PriceSegmentTree import PriceSegmentTree
from trader.indicator.EMA import EMA
from trader.indicator.OBV import OBV
import pydot

def generate_graph(graph, node, t=0, n=0):
    edge = pydot.Edge("depth={}".format(n), "child={}".format(t))
    graph.add_edge(edge)

    if node.start_segment:
        generate_graph(graph, node.start_segment, 1, n+1)
    if node.mid_segment:
        generate_graph(graph, node.mid_segment, 2, n+1)
    if node.end_segment:
        generate_graph(graph, node.end_segment, 3, n+1)

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
    ema50 = EMA(100, scale=24)
    ema200 = EMA(200, scale=24)

    obv = OBV()
    obv_values = []

    ema12_values = []
    ema26_values = []
    ema50_values = []
    ema200_values = []
    close_prices = []
    open_prices = []
    low_prices = []
    high_prices = []
    volumes = []
    ts_values = []

    pst_ready = False
    pst_update_ts = 0
    pst = PriceSegmentTree()

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

        ts_values.append(ts)
        close_prices.append(close)
        open_prices.append(open)
        low_prices.append(low)
        high_prices.append(high)

        # if len(ts_values) > 2 and (ts_values[-1] - ts_values[0]) >= 1000*3600:
        #     pst_ready = True
        #
        # if pst_ready:
        #     if pst_update_ts == 0 or (ts - pst_update_ts) > 1000 * 300:
        #         pst.reset(close_prices, ts_values)
        #         pst.split()
        #         if pst.prev_root:
        #             pst.compare_reset()
        #             pst.compare(pst.prev_root, pst.root, t=[])
        #             result = pst.get_compare_results()
        #             print(result)
        #         pst_update_ts = ts

        i += 1

    pst.reset(ema12_values, ts_values)
    pst.split()

    #g = pydot.Dot(graph_type='graph')
    #generate_graph(g, pst.root)
    #graph_dot_data = g.to_string()

    #graph = None
    #(graph,) = pydot.graph_from_dot_data(graph_dot_data)
    #graph.
    #graph.write_png('example.png')

    plt.subplot(211)
    count = 0
    for node in pst.get_leaf_nodes():
        start = ts_values.index(node.start_ts)
        end = ts_values.index(node.end_ts)
        print(start, end, node.depth, node.percent)

    # i=0
    # for ts in ts_values:
    #     if ts == psp_down_start_ts:
    #         plt.axvline(x=i, color='red')
    #         plt.axvline(x=i+1, color='red')
    #     elif ts == psp_down_end_ts:
    #         plt.axvline(x=i-1, color='red')
    #         plt.axvline(x=i, color='red')
    #     elif ts == psp_up_start_ts:
    #         plt.axvline(x=i, color='green')
    #         plt.axvline(x=i+1, color='green')
    #     elif ts == psp_up_end_ts:
    #         plt.axvline(x=i-1, color='green')
    #         plt.axvline(x=i, color='green')
    #     i += 1

    symprice, = plt.plot(close_prices, label=ticker_id)
    fig1, = plt.plot(ema12_values, label='EMA12')
    fig2, = plt.plot(ema26_values, label='EMA26')
    fig3, = plt.plot(ema50_values, label='EMA50')
    fig4, = plt.plot(ema200_values, label='EMA200')
    plt.legend(handles=[symprice, fig1, fig2, fig3, fig4])
    plt.subplot(212)
    #plt.plot(obv_values)
    #plt.legend(handles=[fig21, fig22, fig23, fig24])

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
