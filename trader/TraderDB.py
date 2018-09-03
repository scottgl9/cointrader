# Keep track of all executed buy orders which don't yet have corresponding sell orders
# This allows us to restore the state of the MultiTrader even if it exits prematurely

import sqlite3
import os.path
import sys
try:
    from sqlwrapper import sqlitewrapper
except ImportError:
    print("WARNING: Failed to load sqlwrapper, continuing...")


class TraderDB(object):
    def __init__(self, filename):
        self.db = sqlitewrapper()
        self.filename = filename

    def connect(self):
        exists = True
        if not os.path.exists(self.filename):
            exists = False

        self.db.connect(self.filename)

        if not exists:
            self.db.create_table('trades', ['id', 'ts', 'symbol', 'price', 'qty', 'bought'],
                                 ['integer', 'integer', 'text', 'real', 'real', 'boolean'], 'id')

    def load_trades(self):
        return self.db.fetch_all('trades')

    def insert_trade(self, ts, symbol, price, qty, bought=True):
        self.db.insert('trades', ['ts', 'symbol', 'price', 'qty', 'bought'], [ts, symbol, price, qty, bought])

    def remove_trade(self, symbol):
        self.db.delete('trades', "symbol='{}'".format(symbol))
