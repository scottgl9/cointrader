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
from pypika import Query, Table, Field, Order
from trader.strategy import *
from datetime import datetime, timedelta
import threading
import sys
from trader.WebHandler import WebThread
from trader.account.binance.client import Client
from trader.MultiTrader import MultiTrader
from trader.account.AccountBinance import AccountBinance
from trader.config import *
import argparse
import logging


def simulate(conn, client, strategy, logger):
    c = conn.cursor()
    c.execute("SELECT * FROM miniticker ORDER BY E ASC")

    assets_info = get_info_all_assets(client)
    #balances = filter_assets_by_minqty(assets_info, get_asset_balances(client))
    accnt = AccountBinance(client, simulation=True)
    accnt.update_asset_balance('BTC', 0.06, 0.06)
    #accnt.update_asset_balance('ETH', 0.1, 0.1)
    #accnt.update_asset_balance('BNB', 15.0, 15.0)

    multitrader = MultiTrader(client,
                              strategy,
                              assets_info=assets_info,
                              volumes=None,
                              simulate=True,
                              accnt=accnt,
                              logger=logger,
                              store_trades=True)

    print(multitrader.accnt.balances)

    tickers = {}

    found = False

    initial_btc_total = 0.0

    first_ts = None
    last_ts = None

    for row in c:
        msg = {'E': row[0], 'c': row[1], 'h': row[2], 'l': row[3],
               'o': row[4], 'q': row[5], 's': row[6], 'v': row[7]}
        tickers[msg['s']] = float(msg['c'])
        if not first_ts:
            first_ts = datetime.utcfromtimestamp(int(msg['E'])/1000)
        else:
            last_ts = datetime.utcfromtimestamp(int(msg['E'])/1000)
        if msg['s'] == 'BTCUSDT' and not found:
            if multitrader.accnt.total_btc_available(tickers):
                found = True
                #total_btc = multitrader.accnt.balances['BTC']['balance']
                total_btc = multitrader.accnt.get_total_btc_value(tickers)
                initial_btc_total = total_btc
                total_usd = float(msg['o']) * total_btc
                print("Initial BTC={}".format(total_btc))

        multitrader.update_tickers(tickers)
        multitrader.process_message(msg)

    # total_time_hours = (last_ts - first_ts).total_seconds() / (60 * 60)
    # print("total time (hours): {}".format(round(total_time_hours, 2)))
    #
    # print(multitrader.accnt.balances)
    # final_btc_total = multitrader.accnt.get_total_btc_value(tickers=tickers)
    # pprofit = round(100.0 * (final_btc_total - initial_btc_total) / initial_btc_total, 2)
    # print("Final BTC={} profit={}%".format(multitrader.accnt.get_total_btc_value(tickers=tickers), pprofit))
    # for pair in multitrader.trade_pairs.values():
    #     for signal in pair.strategy.get_signals():
    #         if signal.buy_price != 0.0:
    #             buy_price = float(signal.buy_price)
    #             last_price = float(pair.strategy.last_price)
    #             symbol = pair.strategy.ticker_id
    #             pprofit = round(100.0 * (last_price - buy_price) / buy_price, 2)
    #             print("{} ({}): {}%".format(symbol, signal.id, pprofit))

    return multitrader.get_stored_trades()

def get_info_all_assets(client):
    assets = {}
    for key, value in client.get_exchange_info().items():
        if key != 'symbols':
            continue
        for asset in value:
            minQty = ''
            tickSize = ''
            for filter in asset['filters']:
                if 'minQty' in filter:
                    minQty = filter['minQty']
                if 'tickSize' in filter:
                    tickSize = filter['tickSize']
            assets[asset['symbol']] = {'minQty': minQty,'tickSize': tickSize}
    return assets

def get_asset_balances(client):
    balances = {}
    for accnt in client.get_account()['balances']:
        if float(accnt['free']) == 0.0 and float(accnt['locked']) == 0.0:
            continue

        balances[accnt['asset']] = float(accnt['free']) + float(accnt['locked'])
    return balances

def filter_assets_by_minqty(assets_info, balances):
    currencies = ['BTC', 'ETH', 'BNB', 'USDT']
    result = {}
    for name, balance in balances.items():
        for currency in currencies:
            symbol = "{}{}".format(name, currency)
            if symbol not in assets_info.keys(): continue

            minQty = float(assets_info[symbol]['minQty'])
            if float(balance) >= minQty:
                result[name] = balance
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', action='store', dest='filename',
                        default='cryptocurrency_database.miniticker_collection_04092018.db',
                        help='filename of kline sqlite db')

    parser.add_argument('-s', action='store', dest='strategy',
                        default='hybrid_signal_market_strategy',
                        help='name of strategy to use')

    results = parser.parse_args()

    logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
    logger = logging.getLogger()

    fileHandler = logging.FileHandler("{0}/{1}.log".format(".", "simulate"))
    fileHandler.setFormatter(logFormatter)
    logger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)
    logger.setLevel(logging.DEBUG)

    client = Client(MY_API_KEY, MY_API_SECRET)
    conn = sqlite3.connect(results.filename)

    # start the Web API
    #thread = threading.Thread(target=WebThread, args=(strategy,))
    #thread.daemon = True
    #thread.start()

    logger.info("Running simulate with {}".format(results.filename))

    try:
        trades = simulate(conn, client, results.strategy, logger)
        print(trades)
    except (KeyboardInterrupt, SystemExit):
        logger.info("CTRL+C: Exiting....")
        conn.close()
        sys.exit(0)
