# Keep track of all executed buy orders which don't yet have corresponding sell orders
# This allows us to restore the state of the MultiTrader even if it exits prematurely

import sqlite3
import os.path
import sys

class TraderDB(object):
    def __init__(self, filename, logger=None):
        self.db = None
        self.filename = filename
        self.logger = logger


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
            if self.get_trade_count() == 0:
                return trades
            cur = self.db.cursor()
            cur.execute("""SELECT ts, symbol, price, qty, bought from trades""")
            for row in cur:
                trade = {}
                trade['ts'] = row[0]
                trade['symbol'] = row[1]
                trade['price'] = row[2]
                trade['qty'] = row[3]
                trade['bought'] = row[4]
                trade['sigid'] = row[5]
                trades.append(trade)
        return trades


    def get_trades(self, symbol):
        trades = []
        if self.db:
            if self.get_trade_count() == 0:
                return trades
            cur = self.db.cursor()
            cur.execute("""SELECT ts, symbol, price, qty, bought from trades WHERE symbol='{}'""".format(symbol))
            for row in cur:
                trade = {}
                trade['ts'] = row[0]
                trade['symbol'] = row[1]
                trade['price'] = row[2]
                trade['qty'] = row[3]
                trade['bought'] = row[4]
                trade['sigid'] = row[5]
                trades.append(trade)
        return trades


    def get_trade_count(self):
        count = 0
        if self.db:
            cur = self.db.cursor()
            count = int(cur.execute("""SELECT COUNT(*) FROM trades""").fetchone()[0])

        return count


    def insert_trade(self, ts, symbol, price, qty, bought=True, sig_id=0):
        if not self.db:
            return
        values = [ts, symbol, price, qty, bought, sig_id]
        cur = self.db.cursor()
        sql = """INSERT INTO trades (ts, symbol, price, qty, bought, sigid) values(?, ?, ?, ?, ?, ?)"""
        try:
            cur.execute(sql, values)
            self.db.commit()
        except sqlite3.OperationalError:
            if self.logger:
                self.logger.info("FAILED to insert {} into {}".format(symbol, self.filename))


    def remove_trade(self, symbol, sig_id=0):
        if not self.db:
            return
        if self.get_trade_count() == 0:
            return
        cur = self.db.cursor()
        if sig_id != 0:
            sql = """DELETE FROM trades WHERE symbol='{}' AND sigid={}""".format(symbol, sig_id)
        else:
            sql = """DELETE FROM trades WHERE symbol='{}'""".format(symbol)
        try:
            cur.execute(sql)
            self.db.commit()
        except sqlite3.OperationalError:
            if self.logger:
                self.logger.warning("FAILED to remove {} from {}".format(symbol, self.filename))


    def create_db_connection(self, filename):
        try:
            conn = sqlite3.connect(filename, check_same_thread=False)
            return conn
        except sqlite3.Error as e:
            print(e)

        return None


    def create_table(self):
        cur = self.db.cursor()
        sql = """CREATE TABLE IF NOT EXISTS trades (id integer, ts integer, symbol text, price real, qty real, bought boolean, sigid integer)"""
        cur.execute(sql)
        self.db.commit()


    def close(self):
        if self.db:
            self.db.close()
            self.db = None
