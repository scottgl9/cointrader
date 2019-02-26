#!/usr/bin/python

import sys
try:
    import trader
except ImportError:
    sys.path.append('.')

import os.path
import time
import sqlite3
from datetime import datetime, timedelta
import threading
import sys
from trader.WebHandler import WebThread
from trader.account.binance.client import Client
from trader.MultiTrader import MultiTrader
from trader.lib.Kline import Kline
from trader.account.AccountBinance import AccountBinance
from trader.config import *
import argparse
import logging
import json


def process_trade_cache(trade_cache, end_tickers_cache):
    trade_info = {}
    for symbol, info in trade_cache.items():
        for trade in info:
            sell_price = trade['price']
            type = trade['type']
            if type != 'sell':
                continue

            buy_price = trade['buy_price']

            # sell trade occurred, so calculate percent profit
            percent = round(100.0 * (sell_price - buy_price) / buy_price, 2)
            if symbol not in trade_info:
                trade_info[symbol] = [percent]
            else:
                trade_info[symbol].append(percent)

        # more buy trades than sell trades, so compute profit of last buy order
        if (len(info) & 1) != 0:
            buy_price = info[-1]['price']
            sell_price = end_tickers_cache[symbol]
            percent = round(100.0 * (sell_price - buy_price) / buy_price, 2)
            if symbol not in trade_info:
                trade_info[symbol] = [percent]
            else:
                trade_info[symbol].append(percent)

    for symbol, percents in trade_info.items():
        ptotal = round(sum(percents), 2)
        print("{}: {}%".format(symbol, ptotal))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', action='store', dest='filename',
                        default='cryptocurrency_database.miniticker_collection_04092018.db',
                        help='filename of kline sqlite db')

    parser.add_argument('-s', action='store', dest='strategy',
                        default='basic_signal_market_strategy',
                        help='name of strategy to use')

    parser.add_argument('-g', action='store', dest='signal_name',
                        default='Hybrid_Crossover_Test',
                        help='name of signal to use')

    parser.add_argument('-c', action='store', dest='cache_dir',
                        default='cache',
                        help='simulation cache directory')

    results = parser.parse_args()

    if not os.path.exists(results.filename):
        print("file {} doesn't exist, exiting...".format(results.filename))
        sys.exit(-1)

    if not os.path.exists(results.cache_dir):
        os.mkdir(results.cache_dir)

    #logFormatter = logging.Formatter("[%(levelname)-5.5s]  %(message)s")
    logFormatter = logging.Formatter("%(message)s")
    logger = logging.getLogger()

    trade_cache = {}
    end_tickers_cache = {}

    trade_cache_name = "{}-{}".format(results.strategy, results.signal_name)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)
    logger.setLevel(logging.DEBUG)

    # load simulation results
    trade_cache_filename = os.path.join(results.cache_dir, results.filename.replace('.db', '.json'))
    if os.path.exists(trade_cache_filename):
        logger.info("Loading {}".format(trade_cache_filename))
        with open(trade_cache_filename, "r") as f:
            trade_cache = json.loads(str(f.read()))
        if trade_cache_name not in trade_cache.keys():
            logger.error("{} not in {}, exiting...".format(trade_cache_name, trade_cache_filename))
            sys.exit(-1)
        end_tickers_cache = trade_cache[trade_cache_name]['end_tickers']
        trade_cache = trade_cache[trade_cache_name]['trades']

    process_trade_cache(trade_cache, end_tickers_cache)

