#!/usr/bin/env python3

import sys
try:
    import trader
except ImportError:
    sys.path.append('.')

from trader.account.cbpro import WebsocketClient, AuthenticatedClient
from trader.account.cbpro.AccountCoinbasePro import AccountCoinbasePro
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
# {
#     "type": "match",
#     "side": "buy",
#     "product_id": "LINK-USD",
#     "time": "2019-09-19T17:39:10.382000Z",
#     "sequence": 291246433,
#     "trade_id": 1099829,
#     "maker_order_id": "f321783f-ce5a-40ca-95ad-695b112fc8e2",
#     "taker_order_id": "6a0cf3c5-2225-4c60-9e96-86ab548e3614",
#     "size": "141.63000000",
#     "price": "1.8488"
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
            # for 'ticker' messages
            cur.execute(
                """CREATE TABLE miniticker (ts integer, p real, ask real, bid real, q real, s text, buy boolean)""")
            # for 'matches' messages
            #cur.execute(
            #    """CREATE TABLE matches (ts integer, seq integer, p real, q real, s text, buy boolean)""")
            self.db.commit()
            return self.db
        except sqlite3.Error as e:
            print(e)
        return None

    def on_message(self, msg):
        if msg['type'] == 'subscriptions':
            return
        if msg['type'] == 'match':
            symbol = msg['product_id']
            ts = int(time.mktime(aniso8601.parse_datetime(msg['time']).timetuple()))
            # # buy or sell
            buy = False
            if msg['side'] == 'buy':
                buy = True
            p = float(msg['price'])
            q = float(msg['size'])
            seq = int(msg['sequence'])
            values = [ts, seq, p, q, symbol, buy]
            cur = self.db.cursor()
            sql = """INSERT INTO matches (ts, seq, p, q, s, buy) values(?, ?, ?, ?, ?, ?)"""
            cur.execute(sql, values)
        elif msg['type'] == 'ticker':
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

    db_file = "cbpro_database_miniticker_collection_{}.db".format(datetime.now().strftime("%m%d%Y"))
    if os.path.exists(db_file):
        logger.info("{} already exists, exiting....".format(db_file))
        sys.exit(0)

    client = AuthenticatedClient(key=CBPRO_KEY, b64secret=CBPRO_SECRET, passphrase=CBPRO_PASS)
    accnt = AccountCoinbasePro(client=client)
    tickers = accnt.get_all_ticker_symbols()
    products = []
    for ticker in tickers:
        if ticker.endswith('GBP') or ticker.endswith('EUR'):
            continue
        products.append(ticker)

    # channel list: full, level2, ticker, user, matches, heartbeat
    channels = ["ticker"] #["matches"]

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
                if ws.db:
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
