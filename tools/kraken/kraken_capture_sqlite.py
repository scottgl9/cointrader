#!/usr/bin/env python3

import sys
try:
    import trader
except ImportError:
    sys.path.append('.')

from trader.account.kraken import API, KrakenAPI
from trader.account.kraken.kraken import kraken_wsclient_py as wsclient
from trader.account.kraken.AccountKraken import AccountKraken
from datetime import datetime
import sqlite3
import time
import logging
import os
import sys
from trader.config import *

# {u'c': u'0.00035038', u'E': 1521434160493, u'h': u'0.00037032', u'l': u'0.00033418', u'o': u'0.00033855', u'q': u'361.61821435', u's': u'BATETH', u'v': u'1044884.00000000', u'e': u'24hrMiniTicker'}

# GDAX kline format: [ timestamp, low, high, open, close, volume ]


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
# class MyWSClient(WebsocketClient):
#     def create_db_connection(self, filename):
#         """ create a database connection to the SQLite database
#             specified by db_file
#         :param db_file: database file
#         :return: Connection object or None
#         """
#         try:
#             self.db = sqlite3.connect(filename, check_same_thread=False)
#             cur = self.db.cursor()
#             cur.execute(
#                 """CREATE TABLE miniticker (ts integer, p real, ask real, bid real, q real, s text, buy boolean)""")
#             self.db.commit()
#             return self.db
#         except sqlite3.Error as e:
#             print(e)
#         return None
#
#     def on_message(self, msg):
#         print(msg)
#         # if msg['type'] != 'ticker':
#         #     return
#         # symbol = msg['product_id']
#         # ts = int(time.mktime(aniso8601.parse_datetime(msg['time']).timetuple()))
#         # p = float(msg['price'])
#         # ask = float(msg['best_ask'])
#         # bid = float(msg['best_bid'])
#         # q = float(msg['last_size'])
#         # # buy or sell
#         # buy = False
#         # if msg['side'] == 'buy':
#         #     buy = True
#         # values = [ts, p, ask, bid, q, symbol, buy]
#         # cur = self.db.cursor()
#         # sql = """INSERT INTO miniticker (ts, p, ask, bid, q, s, buy) values(?, ?, ?, ?, ?, ?, ?)"""
#         # cur.execute(sql, values)
#
#     def on_close(self):
#         sys.exit(0)
def my_handler(message):
    # Here you can do stuff with the messages
    print(message)


class KrakenTrader:
    def __init__(self, client=None, pairs=None, subscription='ticker', commit_count=1000, logger=None):
        #self.client = client
        self.logger = logger
        self.pairs = pairs
        self.subscription = subscription
        #self.commit_count = commit_count
        self.km = None
        #self.counter = 0
        #self.tickers = {}
        #db_file = "cryptocurrency_database.miniticker_collection_{}.db".format(datetime.now().strftime("%m%d%Y"))
        #if os.path.exists(db_file):
        #    self.logger.info("{} already exists, exiting....".format(db_file))
        #    sys.exit(0)
        #self.db_conn = self.create_db_connection(db_file)
        #self.logger.info("Started capturing to {}".format(db_file))
        #cur = self.db_conn.cursor()
        #cur.execute("""CREATE TABLE miniticker (E integer, c real, h real, l real, o real, q real, s text, v real)""")
        #self.db_conn.commit()
        #self.accnt = AccountKraken(self.client)

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

    def process_message(self, msg):
        if not msg:
            return

        if ('event' in msg and (msg['event'] == 'heartbeat' or msg['event'] == 'systemStatus' or
            msg['event'] == 'subscriptionStatus')):
            return
        print(msg)
        # if len(msg) == 0: return
        #
        # if not isinstance(msg, list):
        #     if 's' not in msg.keys(): return
        #     self.insert(self.db_conn, msg)
        #     return
        #
        # for part in msg:
        #     if 's' not in part.keys(): continue
        #     self.insert(self.db_conn, part)

    def run(self):
        self.km = wsclient.WssClient() #key=KRAKEN_API_KEY, secret=KRAKEN_SECRET_KEY)
        self.km.daemon = True
        self.km.subscribe_public(
            subscription={
                'name': self.subscription
            },
            pair=self.pairs,
            callback=self.process_message
        )
        self.km.start()
        while True:
            try:
                time.sleep(5)
            except KeyboardInterrupt:
                #self.db_conn.commit()
                #self.logger.info("Shutting down...")
                self.km.close()
                #self.bm.join()
                break


if __name__ == '__main__':
    logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
    logger = logging.getLogger()

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)
    logger.setLevel(logging.INFO)

    db_file = "kraken_database.miniticker_collection_{}.db".format(datetime.now().strftime("%m%d%Y"))
    if os.path.exists(db_file):
        logger.info("{} already exists, exiting....".format(db_file))
        sys.exit(0)

    api = API(key=KRAKEN_API_KEY, secret=KRAKEN_SECRET_KEY)
    client = KrakenAPI(api=api)
    accnt = AccountKraken(client=client)
    #tickers = accnt.get_all_ticker_symbols()
    #products = []
    #for ticker in tickers:
    #    if ticker.endswith('GBP') or ticker.endswith('EUR'):
    #        continue
    #    products.append(ticker)

    kt = KrakenTrader(pairs=["XBT/USD", "XRP/USD", "ETH/USD"], logger=logger)
    kt.run()
