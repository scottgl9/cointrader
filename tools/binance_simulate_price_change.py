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


def process_cache_largest_price_change(min_ticker_cache, max_ticker_cache):
    result = {}
    symbols = min_ticker_cache.keys()
    for symbol in symbols:
        pchange = 0
        min_price, min_price_ts = min_ticker_cache[symbol]
        max_price, max_price_ts = max_ticker_cache[symbol]
        if min_price_ts < max_price_ts:
            pchange = round(100.0 * (max_price - min_price) / min_price, 2)
        elif max_price_ts < min_price_ts:
            pchange = round(100.0 * (min_price - max_price) / max_price, 2)
        result[symbol] = pchange

    for symbol, pchange in sorted(result.items(), key=lambda x: x[1]):
        if symbol.endswith('BTC'):
            if len(symbol) <= 6:
                print("{}:\t\t{}%".format(symbol, pchange))
            else:
                print("{}:\t{}%".format(symbol, pchange))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', action='store', dest='filename',
                        default='cryptocurrency_database.miniticker_collection_04092018.db',
                        help='filename of kline sqlite db')

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

        min_ticker_cache = trade_cache['min_tickers']
        max_ticker_cache = trade_cache['max_tickers']
        process_cache_largest_price_change(min_ticker_cache, max_ticker_cache)
