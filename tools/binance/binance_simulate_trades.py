#!/usr/bin/python

import sys
try:
    import trader
except ImportError:
    sys.path.append('.')

import os.path
import sys
import argparse
import logging
import json
from trader.TraderConfig import TraderConfig


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

    total_trade_info = {}

    for symbol, percents in trade_info.items():
        ptotal = round(sum(percents), 2)
        total_trade_info[symbol] = ptotal

    total_trade_info = sorted(total_trade_info.items(), key=lambda x: x[1])
    for symbol, percent in total_trade_info:
        print("{}: {}%".format(symbol, percent))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', action='store', dest='filename',
                        default='cryptocurrency_database.miniticker_collection_04092018.db',
                        help='filename of kline sqlite db')

    parser.add_argument('-s', action='store', dest='strategy',
                        default='',
                        help='name of strategy to use')

    parser.add_argument('-g', action='store', dest='signal_name',
                        default='',
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

    config = TraderConfig("trader.ini")
    config.select_section('binance.simulate')

    if results.strategy:
        config.set('strategy', results.strategy)

    if results.signal_name:
        config.set('signals', results.signal_name)

    #if results.hourly_signal_name:
    #    config.set('hourly_signal', results.hourly_signal_name)

    strategy = config.get('strategy')
    signal_name = config.get('signals')
    hourly_name = config.get('hourly_signal')

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

    trade_cache_name = "{}-{}-{}".format(signal_name, hourly_name, balance_txt)
    cache_path = "{}/{}".format(results.cache_dir, strategy)
    cache_path = "{}/{}".format(cache_path, results.filename.replace(".db", ""))
    if not os.path.exists(cache_path):
        logger.error("Cache directory {} doesn't exist, exiting...".format(cache_path))
        sys.exit(-1)

    trade_json_path = "{}/trades.json".format(cache_path)
    if not os.path.exists(trade_json_path):
        logger.error("{} doesn't exist, run tools/binance_simulate.py".format(trade_json_path))
        sys.exit(-1)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)
    logger.setLevel(logging.DEBUG)

    # load simulation results
    logger.info("Loading {}".format(trade_json_path))
    with open(trade_json_path, "r") as f:
        trade_cache = json.loads(str(f.read()))
    if trade_cache_name not in trade_cache.keys():
        logger.error("{} not in {}, exiting...".format(trade_cache_name, trade_json_path))
        sys.exit(-1)
    end_tickers_cache = trade_cache['end_tickers']
    trade_cache = trade_cache[trade_cache_name]['trades']

    process_trade_cache(trade_cache, end_tickers_cache)
