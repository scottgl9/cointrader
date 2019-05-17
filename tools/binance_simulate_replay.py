#!/usr/bin/python

import sys
try:
    import trader
except ImportError:
    sys.path.append('.')

import os.path
import sqlite3
from datetime import datetime
import sys
from trader.account.binance.client import Client
from trader.MultiTrader import MultiTrader
from trader.lib.struct.Kline import Kline
from trader.account.AccountBinance import AccountBinance
from trader.config import *
import argparse
import logging
import json


def create_db_connection(filename):
    try:
        conn = sqlite3.connect(filename, check_same_thread=False)
        return conn
    except sqlite3.Error as e:
        print(e)

    return None


def simulate_trade_cache(conn, strategy, signal_name, trade_cache, logger):
    c = conn.cursor()
    c.execute("SELECT * FROM miniticker ORDER BY E ASC")

    if not os.path.exists("asset_info.json"):
        client = Client(MY_API_KEY, MY_API_SECRET)
    else:
        client = None

    #balances = filter_assets_by_minqty(assets_info, get_asset_balances(client))
    accnt = AccountBinance(client, simulation=True)
    accnt.update_asset_balance('BTC', 0.06, 0.06)
    #accnt.update_asset_balance('ETH', 4.0, 4.0)
    #accnt.update_asset_balance('BNB', 15.0, 15.0)

    signal_names = [signal_name] #, "BTC_USDT_Signal"]

    multitrader = MultiTrader(client,
                              strategy,
                              signal_names=signal_names,
                              simulate=True,
                              accnt=accnt,
                              logger=logger,
                              store_trades=True)

    multitrader.order_handler.store_trades = False

    print(multitrader.accnt.balances)

    tickers = {}

    found = False

    initial_btc_total = 0.0

    first_ts = None
    last_ts = None

    kline = None

    counters = {}

    for row in c:
        msg = {'E': row[0], 'c': row[1], 'h': row[2], 'l': row[3],
               'o': row[4], 'q': row[5], 's': row[6], 'v': row[7]}
        tickers[msg['s']] = float(msg['c'])
        if not first_ts:
            first_ts = datetime.utcfromtimestamp(int(msg['E'])/1000)
        else:
            last_ts = datetime.utcfromtimestamp(int(msg['E'])/1000)

        if not found:
            if multitrader.accnt.total_btc_available(tickers):
                found = True
                total_btc = multitrader.accnt.get_total_btc_value(tickers)
                initial_btc_total = total_btc
                multitrader.update_initial_btc()
                print("Initial BTC={}".format(total_btc))

        if msg['s'] not in trade_cache.keys():
            continue

        if not kline:
            kline = Kline(symbol=msg['s'],
                          open=float(msg['o']),
                          close=float(msg['c']),
                          low=float(msg['l']),
                          high=float(msg['h']),
                          volume=float(msg['v']),
                          ts=int(msg['E']))
        else:
            kline.symbol = msg['s']
            kline.open = float(msg['o'])
            kline.close = float(msg['c'])
            kline.low = float(msg['l'])
            kline.high= float(msg['h'])
            kline.volume = float(msg['v'])
            kline.ts = int(msg['E'])

        if kline.symbol not in counters.keys():
            counters[kline.symbol] = 1
        else:
            counter = counters[kline.symbol]
            counters[kline.symbol] += 1

            for trade in trade_cache[kline.symbol]:
                if counter == trade['index']:
                    price = float(trade['price'])
                    size = float(trade['size'])
                    if trade['type'] == 'buy':
                        multitrader.order_handler.place_buy_market_order(kline.symbol, price, size, 0)
                    elif trade['type'] == 'sell':
                        buy_price = float(trade['buy_price'])
                        multitrader.order_handler.place_sell_market_order(kline.symbol, price, size, buy_price, 0)
                    break

    total_time_hours = (last_ts - first_ts).total_seconds() / (60 * 60)
    print("total time (hours): {}".format(round(total_time_hours, 2)))

    print(multitrader.accnt.balances)
    final_btc_total = multitrader.accnt.get_total_btc_value(tickers=tickers)
    pprofit = round(100.0 * (final_btc_total - initial_btc_total) / initial_btc_total, 2)
    print("Final BTC={} profit={}%".format(multitrader.accnt.get_total_btc_value(tickers=tickers), pprofit))
    for pair in multitrader.trade_pairs.values():
        for signal in pair.strategy.get_signals():
            if signal.buy_price != 0.0:
                buy_price = float(signal.buy_price)
                last_price = float(pair.strategy.last_price)
                symbol = pair.strategy.ticker_id
                pprofit = round(100.0 * (last_price - buy_price) / buy_price, 2)
                print("{} ({}): {}%".format(symbol, signal.id, pprofit))

    return multitrader.get_stored_trades()


def get_detail_all_assets(client):
    return client.get_asset_details()


def get_info_all_assets(client):
    assets = {}
    for key, value in client.get_exchange_info().items():
        if key != 'symbols':
            continue
        for asset in value:
            minNotional = ''
            minQty = ''
            tickSize = ''
            stepSize = ''
            for filter in asset['filters']:
                if 'minQty' in filter:
                    minQty = filter['minQty']
                if 'tickSize' in filter:
                    tickSize = filter['tickSize']
                if 'stepSize' in filter:
                    stepSize = filter['stepSize']
                if 'minNotional' in filter:
                    minNotional = filter['minNotional']

            assets[asset['symbol']] = {'minQty': minQty,
                                       'tickSize': tickSize,
                                       'stepSize': stepSize,
                                       'minNotional': minNotional
                                       }

    return assets


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', action='store', dest='filename',
                        default='cryptocurrency_database.miniticker_collection_04092018.db',
                        help='filename of kline sqlite db')

    parser.add_argument('-s', action='store', dest='strategy',
                        default='hybrid_signal_market_strategy',
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

    logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
    logger = logging.getLogger()

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)
    logger.setLevel(logging.DEBUG)

    conn = sqlite3.connect(results.filename)

    trade_cache = {}

    trade_cache_name = "{}-{}".format(results.strategy, results.signal_name)

    if not os.path.exists(results.cache_dir):
        os.mkdir(results.cache_dir)

    # if we already ran simulation, load the results
    trade_cache_filename = os.path.join(results.cache_dir, results.filename.replace('.db', '.json'))
    if os.path.exists(trade_cache_filename):
        with open(trade_cache_filename, "r") as f:
            trade_cache_all = json.loads(str(f.read()))
            if trade_cache_name not in trade_cache_all.keys():
                logger.info("{} not in {}, exiting...".format(trade_cache_name, trade_cache_filename))
                sys.exit(0)
            logger.info("Loading {} from {}".format(trade_cache_name, trade_cache_filename))
            trade_cache = trade_cache_all[trade_cache_name]
    else:
        logger.info("{} doesn't exist, exiting....".format(trade_cache_filename))
        sys.exit(0)

    try:
        simulate_trade_cache(conn, results.strategy, results.signal_name, trade_cache, logger)
    except (KeyboardInterrupt, SystemExit):
        logger.info("CTRL+C: Exiting....")
        conn.close()
        sys.exit(0)
