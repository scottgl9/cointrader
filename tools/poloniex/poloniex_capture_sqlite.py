#!/usr/bin/env python3

import sys
try:
    import trader
except ImportError:
    sys.path.append('.')

from trader.account.cbpro import WebsocketClient, AuthenticatedClient, PublicClient
from trader.account.AccountPoloniex import AccountPoloniex
from datetime import datetime
import sqlite3
import time
import logging
import os
import sys
import aniso8601
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
        self.accnt = AccountPoloniex(self.client)

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

# ticker channel example:
# {
#    u'open_24h':u'181.93000000',
#    u'product_id':u'ETH-USD',
#    u'sequence':7285507796,
#    u'price':u'181.06000000',
#    u'best_ask':u'181.06',
#    u'best_bid':u'181.05',
#    u'high_24h':u'182.01000000',
#    u'trade_id':51300425,
#    u'volume_24h':u'51345.14784956',
#    u'last_size':u'3.77041565',
#    u'time':   u'2019-09-13T22:30:21.263000   Z',
#    u'volume_30d':u'2026958.29721173',
#    u'type':u'ticker',
#    u'side':u'buy',
#    u'low_24h':u'177.57000000'
# }
class MyWSClient(WebsocketClient):
    def create_db_connection(self, filename):
        """ create a database connection to the SQLite database
            specified by db_file
        :param db_file: database file
        :return: Connection object or None
        """
        try:
            self.db = sqlite3.connect(filename, check_same_thread=False)
            cur = self.db.cursor()
            cur.execute(
                """CREATE TABLE miniticker (ts integer, p real, ask real, bid real, q real, s text, buy boolean)""")
            self.db.commit()
            return self.db
        except sqlite3.Error as e:
            print(e)
        return None

    def on_message(self, msg):
        if msg['type'] != 'ticker':
            return
        symbol = msg['product_id']
        ts = int(time.mktime(aniso8601.parse_datetime(msg['time']).timetuple()))
        p = float(msg['price'])
        ask = float(msg['best_ask'])
        bid = float(msg['best_bid'])
        q = float(msg['last_size'])
        # buy or sell
        buy = False
        if msg['side'] == 'buy':
            buy = True
        values = [ts, p, ask, bid, q, symbol, buy]
        cur = self.db.cursor()
        sql = """INSERT INTO miniticker (ts, p, ask, bid, q, s, buy) values(?, ?, ?, ?, ?, ?, ?)"""
        cur.execute(sql, values)

    def on_close(self):
        sys.exit(0)


if __name__ == '__main__':
    logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
    logger = logging.getLogger()

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)
    logger.setLevel(logging.INFO)

    db_file = "cbpro_database.miniticker_collection_{}.db".format(datetime.now().strftime("%m%d%Y"))
    if os.path.exists(db_file):
        logger.info("{} already exists, exiting....".format(db_file))
        sys.exit(0)

    client = Poloniex(key=POLONIEX_API_KEY, secret=POLONIEX_SECRET_KEY, coach=False)
    accnt = AccountPoloniex(client=client)
    tickers = accnt.get_all_ticker_symbols()
    products = []
    for ticker in tickers:
        if ticker.endswith('GBP') or ticker.endswith('EUR'):
            continue
        products.append(ticker)

    # channel list: full, level2, ticker, user, matches, heartbeat
    channels = ["ticker"]

    while 1:
        ws = MyWSClient(should_print=False,
                        products=products,
                        channels=channels,
                        api_key=CBPRO_KEY,
                        api_secret=CBPRO_SECRET,
                        api_passphrase=CBPRO_PASS
                        )
        try:
            ws.create_db_connection(db_file)
            ws.start()
            print("started capturing {}...".format(db_file))
            while 1:
                time.sleep(30)
                ws.db.commit()
        except (KeyboardInterrupt, SystemExit):
            ws.close()
            sys.exit(0)
        except Exception as e:
            print('Error occurred: {}'.format(e))
            ws.close()
            print("Connection closed, restarting...")
            time.sleep(2)
            sys.exit(-1)
