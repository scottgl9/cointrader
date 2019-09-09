#!/usr/bin/env python3

import sys
try:
    import trader
except ImportError:
    sys.path.append('.')

import os.path
import time
import sqlite3
from datetime import datetime
import sys
from trader.account.binance.client import Client
from trader.MultiTrader import MultiTrader

#try:
#    from trader.lib.native.Kline import Kline
#except ImportError:
from trader.lib.struct.Kline import Kline

from trader.account.AccountBinance import AccountBinance
from trader.TraderConfig import TraderConfig
from trader.config import *
import argparse
import logging
import json


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', action='store', dest='strategy',
                        default='basic_signal_market_strategy',
                        help='name of strategy to use')

    parser.add_argument('-g', action='store', dest='signal_names',
                        default='',
                        help='name of signal(s) to use (comma separated)')

    parser.add_argument('-r', action='store', dest='hourly_signal_names',
                        default='',
                        help='name of hourly signal(s) to use (comma separated)')

    parser.add_argument('-c', action='store', dest='cache_dir',
                        default='cache',
                        help='simulation cache directory')

    results = parser.parse_args()

    logFormatter = logging.Formatter("%(message)s")
    logger = logging.getLogger()

    config = TraderConfig("trader.ini")
    config.select_section('binance.simulate')

    #if not results.signal_names and not results.hourly_signal_names:
    #    parser.print_help()
    #    sys.exit(0)

    if results.strategy:
        config.set('strategy', results.strategy)

    if results.signal_names:
        config.set('signals', results.signal_names)

    if results.hourly_signal_names:
        config.set('hourly_signal', results.hourly_signal_names)

    strategy = config.get('strategy')
    signal_names = config.get('signals')
    hourly_names = config.get('hourly_signal')

    # get balances from trader.ini to be used in creating filename
    btc_balance = float(config.get('BTC'))
    eth_balance = float(config.get('ETH'))
    bnb_balance = float(config.get('BNB'))
    balance_txt = ""
    if btc_balance:
        balance_txt += "{}BTC".format(btc_balance)
    if eth_balance:
        balance_txt += "{}ETH".format(eth_balance)
    if bnb_balance:
        balance_txt += "{}BNB".format(bnb_balance)

    base_cache_path = "{}/{}".format(results.cache_dir, strategy)
    for dbname in sorted(os.listdir(base_cache_path)):
        cache_path = "{}/{}".format(base_cache_path, dbname)
        print("{}:".format(dbname))
        for signal_name in signal_names.split(','):
            for hourly_name in hourly_names.split(','):
                trade_cache_name = "{}-{}-{}".format(signal_name, hourly_name, balance_txt)
                trade_result_path = "{}/{}.txt".format(cache_path, trade_cache_name)
                with open(trade_result_path, 'r') as f:
                    result = f.read()
                print("{} {}:".format(signal_name, hourly_name))
                print(result)
