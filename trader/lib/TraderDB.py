# Keep track of all executed buy orders which don't yet have corresponding sell orders
# This allows us to restore the state of the MultiTrader even if it exits prematurely

import sqlite3
import os.path
import sys

class TraderDB(object):
    def __init__(self, filename):
        self.db = None
        self.filename = filename

    def connect(self):
        exists = False
        if os.path.exists(self.filename):
            exists = True

        self.db = self.create_db_connection(self.filename)

        if not exists:
            self.create_table()

    def get_all_trades(self):
        trades = []
        if self.db:
            cur = self.db.cursor()
            cur.execute("""SELECT ts, symbol, price, qty, bought from trades""")
            for row in cur:
                trade = {}
                trade['ts'] = row[0]
                trade['symbol'] = row[1]
                trade['price'] = row[2]
                trade['qty'] = row[3]
                trade['bought'] = row[4]
                trades.append(trade)
        return trades

    def get_trades(self, symbol):
        trades = []
        if self.db:
            cur = self.db.cursor()
            cur.execute("""SELECT ts, symbol, price, qty, bought from trades WHERE symbol='{}'""".format(symbol))
            for row in cur:
                trade = {}
                trade['ts'] = row[0]
                trade['symbol'] = row[1]
                trade['price'] = row[2]
                trade['qty'] = row[3]
                trade['bought'] = row[4]
                trades.append(trade)
        return trades

    def insert_trade(self, ts, symbol, price, qty, bought=True):
        if self.db:
            values = [ts, symbol, price, qty, bought]
            cur = self.db.cursor()
            sql = """INSERT INTO trades (ts, symbol, price, qty, bought) values(?, ?, ?, ?, ?)"""
            cur.execute(sql, values)
            self.db.commit()

    def remove_trade(self, symbol):
        if len(self.db.get_trades(symbol)) == 0:
            return
        cur = self.db.cursor()
        sql = """DELETE FROM trades WHERE symbol={}""".format(symbol)
        cur.execute(sql)
        self.db.commit()

    def create_db_connection(self, filename):
        try:
            conn = sqlite3.connect(filename, check_same_thread=False)
            return conn
        except sqlite3.Error as e:
            print(e)

        return None

    def create_table(self):
        cur = self.db.cursor()
        sql = """CREATE TABLE IF NOT EXISTS trades (id integer, ts integer, symbol text, price real, qty real, bought boolean)"""
        cur.execute(sql)
        self.db.commit()

    def close(self):
        if self.db:
            self.db.close()
            self.db = None
