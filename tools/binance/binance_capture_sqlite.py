#!/usr/bin/python

import sys
try:
    import trader
except ImportError:
    sys.path.append('.')

from trader.account.binance.binance.websockets import BinanceSocketManager
from trader.account.binance.binance.client import Client
from trader.account.binance.AccountBinance import AccountBinance
from datetime import datetime
import sqlite3
import time
import logging
import os
import sys
from trader.config import *

# {u'c': u'0.00035038', u'E': 1521434160493, u'h': u'0.00037032', u'l': u'0.00033418', u'o': u'0.00033855', u'q': u'361.61821435', u's': u'BATETH', u'v': u'1044884.00000000', u'e': u'24hrMiniTicker'}

# GDAX kline format: [ timestamp, low, high, open, close, volume ]


class BinanceTrader:
    def __init__(self, client, commit_count=1000, logger=None):
        self.client = client
        self.logger = logger
        self.commit_count = commit_count
        self.bm = None
        self.counter = 0
        self.tickers = {}
        db_file = "cryptocurrency_database.miniticker_collection_{}.db".format(datetime.now().strftime("%m%d%Y"))
        if os.path.exists(db_file):
            self.logger.info("{} already exists, exiting....".format(db_file))
            sys.exit(0)
        self.db_conn = self.create_db_connection(db_file)
        self.logger.info("Started capturing to {}".format(db_file))
        cur = self.db_conn.cursor()
        cur.execute("""CREATE TABLE miniticker (E integer, c real, h real, l real, o real, q real, s text, v real)""")
        self.db_conn.commit()
        self.accnt = AccountBinance(self.client)

    def create_db_connection(self, db_file):
        """ create a database connection to the SQLite database
            specified by db_file
        :param db_file: database file
        :return: Connection object or None
        """
        try:
            conn = sqlite3.connect(db_file, check_same_thread=False)
            return conn
        except sqlite3.Error as e:
            print(e)

        return None

    def insert(self, conn, msg):
        values = [msg['E'], msg['c'], msg['h'], msg['l'], msg['o'], msg['q'], msg['s'], msg['v']]
        cur = conn.cursor()
        sql = """INSERT INTO miniticker (E, c, h, l, o, q, s, v) values(?, ?, ?, ?, ?, ?, ?, ?)"""
        cur.execute(sql, values)

        self.counter += 1
        if self.counter >= self.commit_count:
            conn.commit()
            self.counter = 0

    def get_websocket_kline(self, msg):
        kline = list()
        kline.append(int(msg['E']))
        kline.append(float(msg['l']))
        kline.append(float(msg['h']))
        kline.append(float(msg['o']))
        kline.append(float(msg['c']))
        kline.append(float(msg['v']))
        return kline

    # update tickers dict to contain kline ticker values for all traded symbols
    def process_websocket_message(self, msg):
        for ticker in msg:
            if 's' not in ticker or 'E' not in ticker: continue
            self.tickers[ticker['s']] = self.get_websocket_kline(ticker)
            return self.tickers[ticker['s']]

    def process_message(self, msg):
        if len(msg) == 0: return

        if not isinstance(msg, list):
            if 's' not in msg.keys(): return
            self.insert(self.db_conn, msg)
            return

        for part in msg:
            if 's' not in part.keys(): continue
            self.insert(self.db_conn, part)

    def run(self):
        self.bm = BinanceSocketManager(self.client)
        self.bm.daemon = True
        self.bm.start_miniticker_socket(self.process_message)
        self.bm.start()
        while True:
            try:
                time.sleep(5)
            except KeyboardInterrupt:
                self.db_conn.commit()
                self.logger.info("Shutting down...")
                self.bm.close()
                #self.bm.join()
                break


def get_all_tickers(client):
    result = []
    for key, value in client.get_exchange_info().items():
        if key != 'symbols': continue
        for asset in value:
            result.append(asset['symbol'])
    return result


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


def filter_by_balances(assets, balances):
    if len(assets) == 0: return assets
    result = []
    for name, info in assets.items():
        print(name, info)
        if name in balances.keys():
          result.append(name)
    return result


if __name__ == '__main__':
    logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
    logger = logging.getLogger()

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)
    logger.setLevel(logging.INFO)

    client = Client(MY_API_KEY, MY_API_SECRET)
    assets_info = get_info_all_assets(client)
    balances = filter_assets_by_minqty(assets_info, get_asset_balances(client))
    print(assets_info)
    print(balances)
    currency_list = ['BTC', 'ETH', 'BNB', 'USDT']

    bt = BinanceTrader(client, logger=logger)
    bt.run()
